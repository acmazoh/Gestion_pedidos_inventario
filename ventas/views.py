# Exportar historial de ventas a CSV
from django.http import HttpResponse, JsonResponse
import csv

def historial_ventas_csv(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    transacciones = Transaccion.objects.all().select_related('pedido')
    if desde:
        transacciones = transacciones.filter(fecha__date__gte=desde)
    if hasta:
        transacciones = transacciones.filter(fecha__date__lte=hasta)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Pedido', 'Mesa / Cliente', 'Productos', 'Total'])
    for t in transacciones.order_by('-fecha'):
        productos = ', '.join([
            f"{item.producto.nombre} x{item.cantidad}"
            for item in t.pedido.items.select_related('producto').all()
        ])
        writer.writerow([
            t.fecha.strftime('%d/%m/%Y %H:%M'),
            t.pedido.id,
            getattr(t.pedido, 'mesa_o_online', ''),
            productos,
            f"${t.total}"
        ])
    return response

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum
from products.models import Producto, Categoria
from .models import Pedido, PedidoProducto, Transaccion
from .forms import PedidoForm, PedidoProductoForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Historial de ventas
class HistorialVentasView(LoginRequiredMixin, View):
    template_name = 'ventas/historial_ventas.html'

    def get(self, request):
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        transacciones = Transaccion.objects.all().select_related('pedido')
        if desde:
            transacciones = transacciones.filter(fecha__date__gte=desde)
        if hasta:
            transacciones = transacciones.filter(fecha__date__lte=hasta)
        total_periodo = transacciones.aggregate(total=Sum('total'))['total'] or 0
        return render(request, self.template_name, {
            'transacciones': transacciones.order_by('-fecha'),
            'desde': desde,
            'hasta': hasta,
            'total_periodo': total_periodo,
        })

# Cambiar estado de pedido desde cocina
class MarcarListoView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'en_preparacion':
            pedido.estado = 'listo'
            pedido.save()
        return redirect('cocina_dashboard')


class MarcarEntregadoView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'listo':
            pedido.estado = 'pagado'
            pedido.save()
            # Registrar transacción
            total = 0
            for item in pedido.items.select_related('producto'):
                total += item.producto.precio * item.cantidad
            Transaccion.objects.create(pedido=pedido, total=total)
        return redirect('cocina_dashboard')


class ProductoVentaListView(ListView):
    model = Producto
    template_name = 'ventas/producto_venta_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        from django.db.models import F, OuterRef, Exists
        from products.models import ProductoIngrediente

        queryset = super().get_queryset().filter(disponible=True)
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        # Solo productos con receta y todos los ingredientes con stock suficiente
        queryset = queryset.filter(productoingrediente__isnull=False).distinct()
        pi_sub = ProductoIngrediente.objects.filter(
            producto=OuterRef('pk'),
            ingrediente__stock__lt=F('cantidad')
        )
        queryset = queryset.annotate(
            tiene_faltante=Exists(pi_sub)
        ).filter(tiene_faltante=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            try:
                context['categoria_seleccionada'] = Categoria.objects.get(id=categoria_id)
            except Categoria.DoesNotExist:
                pass
        return context


class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'ventas/pedido_form.html'

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('pedido_detail', kwargs={'pk': self.object.pk})


class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'ventas/pedido_list.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        role = getattr(profile, 'role', None)
        role_name = (role.name or '').strip().lower() if role else ''

        if role_name == 'waiter':
            return Pedido.objects.filter(estado__in=['en_preparacion', 'listo']).order_by('-fecha_creacion')

        return Pedido.objects.exclude(estado='pagado').order_by('-fecha_creacion')


class PedidoDetailView(LoginRequiredMixin, ListView):
    model = PedidoProducto
    template_name = 'ventas/pedido_detail.html'
    context_object_name = 'items'

    def get(self, request, pk, *args, **kwargs):
        from decimal import Decimal, ROUND_HALF_UP
        from django.conf import settings
        pedido = get_object_or_404(Pedido, pk=pk)
        form = PedidoProductoForm()
        items = list(pedido.items.select_related('producto'))
        for item in items:
            item.subtotal = item.producto.precio * item.cantidad
        subtotal = sum(item.subtotal for item in items)
        tax_rate = Decimal(str(getattr(settings, 'TAX_RATE', 0.19)))
        impuesto = (Decimal(subtotal) * tax_rate).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        total = Decimal(subtotal) + impuesto
        # Para mostrar el porcentaje de impuesto en la plantilla
        tax_rate_percent = (tax_rate * 100).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        return render(request, self.template_name, {
            'pedido': pedido,
            'form': form,
            'items': items,
            'subtotal': subtotal,
            'impuesto': impuesto,
            'total': total,
            'tax_rate': tax_rate_percent,
        })

    def post(self, request, pk, *args, **kwargs):
        from decimal import Decimal, ROUND_HALF_UP
        from django.conf import settings
        pedido = get_object_or_404(Pedido, pk=pk)
        form = PedidoProductoForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            item, created = PedidoProducto.objects.get_or_create(
                pedido=pedido,
                producto=producto,
                defaults={'cantidad': cantidad},
            )
            if not created:
                item.cantidad += cantidad
                item.save()
            return redirect('pedido_detail', pk=pedido.pk)

        items = list(pedido.items.select_related('producto'))
        for item in items:
            item.subtotal = item.producto.precio * item.cantidad
        subtotal = sum(item.subtotal for item in items)
        tax_rate = Decimal(str(getattr(settings, 'TAX_RATE', 0.19)))
        impuesto = (Decimal(subtotal) * tax_rate).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        total = Decimal(subtotal) + impuesto
        return render(request, self.template_name, {
            'pedido': pedido,
            'form': form,
            'items': items,
            'subtotal': subtotal,
            'impuesto': impuesto,
            'total': total,
        })


class PedidoProductoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pedido_pk, item_pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pedido_pk)
        if pedido.estado != 'pendiente':
            return redirect('pedido_detail', pk=pedido_pk)
        item = get_object_or_404(PedidoProducto, pk=item_pk, pedido=pedido)
        item.delete()
        return redirect('pedido_detail', pk=pedido_pk)


class PedidoProductoQuantityUpdateView(LoginRequiredMixin, View):
    def post(self, request, pedido_pk, item_pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pedido_pk)
        if pedido.estado != 'pendiente':
            return redirect('pedido_detail', pk=pedido_pk)
        item = get_object_or_404(PedidoProducto, pk=item_pk, pedido=pedido)
        action = request.POST.get('action')

        if action == 'increment':
            item.cantidad += 1
            item.save()
        elif action == 'decrement':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                # eliminar si se reduce por debajo de 1
                item.delete()
        return redirect('pedido_detail', pk=pedido_pk)


class PedidoConfirmarView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)

        if pedido.estado != 'pendiente':
            messages.error(request, 'El pedido no puede modificarse en su estado actual.')
            return redirect('pedido_detail', pk=pk)

        if not pedido.items.exists():
            messages.error(request, 'La orden está vacía y no puede confirmarse.')
            return redirect('pedido_detail', pk=pk)

        # Calcular requisitos de ingredientes para el pedido completo
        required_per_ingredient = {}
        ingredient_products = {}

        for item in pedido.items.select_related('producto'):
            receta = list(item.producto.productoingrediente_set.select_related('ingrediente'))
            if receta:
                for pi in receta:
                    required = pi.cantidad * item.cantidad
                    required_per_ingredient.setdefault(pi.ingrediente, 0)
                    required_per_ingredient[pi.ingrediente] += required
                    ingredient_products.setdefault(pi.ingrediente, set()).add(item.producto.nombre)
            else:
                for ingrediente in item.producto.ingredientes.all():
                    required_per_ingredient.setdefault(ingrediente, 0)
                    required_per_ingredient[ingrediente] += item.cantidad
                    ingredient_products.setdefault(ingrediente, set()).add(item.producto.nombre)

        shortages = []
        for ingrediente, required in required_per_ingredient.items():
            if ingrediente.stock < required:
                shortages.append({
                    'ingrediente': ingrediente,
                    'required': required,
                    'available': ingrediente.stock,
                    'missing': required - ingrediente.stock,
                    'productos': sorted(ingredient_products.get(ingrediente, [])),
                })

        if shortages:
            # Render detail view with error info
            items = list(pedido.items.select_related('producto'))
            for item in items:
                item.subtotal = item.producto.precio * item.cantidad
            total = sum(item.subtotal for item in items)
            return render(request, 'ventas/pedido_detail.html', {
                'pedido': pedido,
                'form': PedidoProductoForm(),
                'items': items,
                'total': total,
                'confirm_errors': shortages,
            })

        # Si hay suficiencia, descontar stock y confirmar.
        for ingrediente, required in required_per_ingredient.items():
            ingrediente.stock -= required
            ingrediente.save()

        pedido.estado = 'en_preparacion'
        pedido.save()
        return redirect('pedido_detail', pk=pk)


# ── RF-08: Vista de Cocina en Tiempo Real ────────────────────────────────────

class PedidosActivosAPIView(LoginRequiredMixin, View):
    """API endpoint que retorna pedidos activos en JSON para actualizaci\u00f3n en tiempo real.

    Responde con un JSON que contiene:
    - pedidos: lista de pedidos activos con sus detalles
    - timestamp: marca de tiempo para comparaci\u00f3n de actualizaci\u00f3n
    """

    def get(self, request):
        # Pedidos en preparaci\u00f3n o listos
        pedidos = Pedido.objects.filter(
            estado__in=['en_preparacion', 'listo']
        ).order_by('fecha_creacion')

        # \u00d9ltima actualizaci\u00f3n para detectar cambios (hace 5 segundos)
        last_update = request.GET.get('last_update')
        pedidos_json = []

        for pedido in pedidos:
            items = []
            for item in pedido.items.select_related('producto'):
                items.append({
                    'id': item.id,
                    'producto': item.producto.nombre,
                    'cantidad': item.cantidad,
                })

            # Detectar si es orden nueva (creada hace menos de 30 segundos)
            ahora = timezone.now()
            segundos_transcurridos = (ahora - pedido.fecha_creacion).total_seconds()
            es_nuevo = segundos_transcurridos < 30

            pedidos_json.append({
                'id': pedido.id,
                'mesa_o_online': pedido.mesa_o_online,
                'estado': pedido.estado,
                'fecha_creacion': pedido.fecha_creacion.isoformat(),
                'hora_formateada': pedido.fecha_creacion.strftime('%H:%M'),
                'items': items,
                'es_nuevo': es_nuevo,
                'total_items': len(items),
            })

        return JsonResponse({
            'pedidos': pedidos_json,
            'timestamp': timezone.now().isoformat(),
            'total': len(pedidos_json),
        })
class CocinaDashboardView(LoginRequiredMixin, ListView):
    """Interfaz de cocina: muestra los pedidos confirmados en tiempo real."""

    model = Pedido
    template_name = 'ventas/cocina_dashboard.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        # Mostrar pedidos que fueron confirmados (en preparación) y listos.
        return super().get_queryset().filter(
            estado__in=['en_preparacion', 'listo']
        ).order_by('fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Obtener el rol del usuario autenticado
        try:
            profile = user.userprofile
            role_name = profile.role.name if profile.role else ''
        except Exception:
            role_name = ''
        context['user_role'] = role_name
        return context


class PedidoMarcarListoView(LoginRequiredMixin, View):
    """Cocina marca el pedido como 'listo'."""
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'en_preparacion':
            pedido.estado = 'listo'
            pedido.save()
        return redirect('cocina_dashboard')


class PedidoMarcarEntregadaView(LoginRequiredMixin, View):
    """Marca el pedido como 'entregada' y registra la Transaccion automáticamente (RF-11)."""
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'listo':
            pedido.estado = 'entregada'
            pedido.save()
            total = sum(
                item.producto.precio * item.cantidad
                for item in pedido.items.select_related('producto')
            )
            Transaccion.objects.get_or_create(pedido=pedido, defaults={'total': total})
        return redirect('cocina_dashboard')


class PedidoMarcarPagadoView(LoginRequiredMixin, View):
    """Marca el pedido como 'pagado' desde la lista de pedidos."""
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'entregada':
            pedido.estado = 'pagado'
            pedido.save()
        return redirect('pedido_list')


class HistorialVentasView(LoginRequiredMixin, ListView):
    """Historial de ventas (RF-11)."""
    model = Transaccion
    template_name = 'ventas/historial_ventas.html'
    context_object_name = 'transacciones'
    paginate_by = 20

    def get_queryset(self):
        qs = Transaccion.objects.select_related('pedido').order_by('-fecha')
        fecha_desde = self.request.GET.get('desde')
        fecha_hasta = self.request.GET.get('hasta')
        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['desde'] = self.request.GET.get('desde', '')
        context['hasta'] = self.request.GET.get('hasta', '')
        context['total_periodo'] = sum(t.total for t in self.get_queryset())
        # Adjuntar items a cada transacción para mostrarlos en el template
        for t in context['transacciones']:
            t.items_pedido = t.pedido.items.select_related('producto').all()
        return context


class ExportarHistorialCSVView(LoginRequiredMixin, View):
    """Exporta el historial de ventas filtrado por fecha en formato CSV (RF-11).
    Acepta los mismos parámetros ?desde= y ?hasta= que HistorialVentasView.
    Genera un archivo descargable con una fila por producto vendido.
    """
    def get(self, request, *args, **kwargs):
        qs = Transaccion.objects.select_related('pedido').order_by('-fecha')
        fecha_desde = request.GET.get('desde')
        fecha_hasta = request.GET.get('hasta')
        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="historial_ventas.csv"'
        # BOM para compatibilidad con Excel
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Pedido', 'Mesa/Cliente', 'Producto', 'Cantidad', 'Total pedido'])

        for t in qs:
            items = t.pedido.items.select_related('producto').all()
            for item in items:
                writer.writerow([
                    t.fecha.strftime('%d/%m/%Y %H:%M'),
                    f'#{t.pedido.id}',
                    t.pedido.mesa_o_online,
                    item.producto.nombre,
                    item.cantidad,
                    t.total,
                ])

        return response
