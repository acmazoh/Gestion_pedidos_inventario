from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone

class PedidosActivosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ahora = timezone.now()
        pedidos = Pedido.objects.filter(estado__in=['en_preparacion', 'listo']).order_by('fecha_creacion')
        pedidos_data = []
        for pedido in pedidos:
            items = [
                {
                    'id': item.id,
                    'producto': item.producto.nombre,
                    'cantidad': item.cantidad,
                }
                for item in pedido.items.select_related('producto')
            ]
            segundos_transcurridos = (ahora - pedido.fecha_creacion).total_seconds()
            es_nuevo = segundos_transcurridos < 30
            pedidos_data.append({
                'id': pedido.id,
                'mesa_o_online': pedido.mesa_o_online,
                'estado': pedido.estado,
                'fecha_creacion': pedido.fecha_creacion.isoformat(),
                'hora_formateada': pedido.fecha_creacion.strftime('%H:%M'),
                'items': items,
                'es_nuevo': es_nuevo,
                'total_items': len(items),
            })
        return Response({
            'pedidos': pedidos_data,
            'timestamp': ahora.isoformat(),
            'total': len(pedidos_data),
        })
from decimal import Decimal
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Pedido, PedidoProducto
from .serializers import PedidoSerializer, PedidoItemSerializer
from products.models import Producto

TAX_RATE = Decimal(str(getattr(settings, 'TAX_RATE', 0.19)))


class PedidoViewSet(viewsets.ModelViewSet):
    """
    CRUD de Pedidos.
    RF-06: totales con impuestos | RF-07: validación de stock al confirmar.
    """
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propios pedidos
        return (
            Pedido.objects
            .filter(creado_por=self.request.user)
            .prefetch_related('items__producto')
            .order_by('-fecha_creacion')
        )

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    # ── RF-06: calcular total ────────────────────────────────────────────────
    @action(detail=True, methods=['get'], url_path='calculate-total')
    def calculate_total(self, request, pk=None):
        """
        GET /api/orders/{id}/calculate-total/
        Devuelve desglose: items, subtotal, impuesto (19%), total.
        """
        pedido = self.get_object()
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

    # ── Agregar / actualizar ítem ────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
        """
        POST /api/orders/{id}/add-item/
        Body: {producto_id, cantidad}
        Si el producto ya existe en el pedido, suma la cantidad.
        """
        pedido = self.get_object()
        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden agregar ítems a pedidos en estado Pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        if not producto_id or cantidad < 1:
            return Response(
                {'error': 'producto_id y cantidad (≥1) son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            producto = Producto.objects.get(pk=producto_id, disponible=True)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado o inactivo.'}, status=404)

        item, created = PedidoProducto.objects.get_or_create(
            pedido=pedido, producto=producto,
            defaults={'cantidad': cantidad},
        )
        if not created:
            item.cantidad += cantidad
            item.save()

        # Refrescar el pedido desde la base de datos para asegurar consistencia
        pedido.refresh_from_db()
        return Response(self.get_serializer(pedido).data, status=status.HTTP_200_OK)

    # ── Eliminar ítem ────────────────────────────────────────────────────────
    @action(detail=True, methods=['delete'], url_path=r'items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        """DELETE /api/orders/{id}/items/{item_id}/"""
        pedido = self.get_object()
        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'No se puede modificar un pedido que no está Pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            item = PedidoProducto.objects.get(pk=item_id, pedido=pedido)
        except PedidoProducto.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=404)

        item.delete()
        pedido.refresh_from_db()
        return Response(self.get_serializer(pedido).data, status=status.HTTP_200_OK)

    # ── Actualizar cantidad de ítem ──────────────────────────────────────────
    @action(detail=True, methods=['patch'], url_path=r'items/(?P<item_id>\d+)/quantity')
    def update_item_quantity(self, request, pk=None, item_id=None):
        """PATCH /api/orders/{id}/items/{item_id}/quantity/  — body: {cantidad}"""
        pedido = self.get_object()
        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'No se puede modificar un pedido que no está Pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            item = PedidoProducto.objects.get(pk=item_id, pedido=pedido)
        except PedidoProducto.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=404)

        cantidad = int(request.data.get('cantidad', 1))
        if cantidad < 1:
            item.delete()
        else:
            item.cantidad = cantidad
            item.save()

        pedido.refresh_from_db()
        return Response(self.get_serializer(pedido).data, status=status.HTTP_200_OK)

    # ── RF-07: confirmar orden con validación de stock ───────────────────────
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """
        POST /api/orders/{id}/confirm/
        Valida stock de ingredientes. Si hay faltantes devuelve 409 con detalle.
        Si hay suficiencia, descuenta stock y pasa pedido a 'en_preparacion'.
        """
        pedido = self.get_object()

        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden confirmar pedidos en estado Pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pedido.items.exists():
            return Response(
                {'error': 'El pedido no tiene productos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calcular ingredientes requeridos
        required: dict = {}    # ingrediente_obj -> cantidad total requerida
        ing_productos: dict = {}  # ingrediente_obj -> set de nombres de productos

        for item in pedido.items.select_related('producto'):
            receta = list(
                item.producto.productoingrediente_set.select_related('ingrediente')
            )
            if receta:
                for pi in receta:
                    needed = pi.cantidad * item.cantidad
                    required[pi.ingrediente] = required.get(pi.ingrediente, 0) + needed
                    ing_productos.setdefault(pi.ingrediente, set()).add(item.producto.nombre)
            else:
                for ing in item.producto.ingredientes.all():
                    required[ing] = required.get(ing, 0) + item.cantidad
                    ing_productos.setdefault(ing, set()).add(item.producto.nombre)

        # Detectar faltantes de stock
        shortages = [
            {
                'ingrediente': ing.nombre,
                'unidad': getattr(ing, 'get_unidad_medida_display', lambda: '')(),
                'required': req,
                'available': ing.stock,
                'missing': req - ing.stock,
                'productos': sorted(ing_productos.get(ing, [])),
            }
            for ing, req in required.items()
            if ing.stock < req
        ]

        if shortages:
            return Response({'shortages': shortages}, status=status.HTTP_409_CONFLICT)

        # Descontar stock y confirmar
        for ing, req in required.items():
            ing.stock -= req
            ing.save(update_fields=['stock'])

        pedido.estado = 'en_preparacion'
        pedido.save(update_fields=['estado'])

        return Response(self.get_serializer(pedido).data, status=status.HTTP_200_OK)
