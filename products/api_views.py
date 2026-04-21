from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Producto, Categoria, Ingrediente
from .serializers import ProductoSerializer, CategoriaSerializer, IngredienteSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para Productos del menú.
    RF-01: gestión admin | RF-02: catálogo POS
    """
    queryset = Producto.objects.select_related('categoria').prefetch_related(
        'ingredientes', 'productoingrediente_set__ingrediente'
    ).order_by('categoria__nombre', 'nombre')
    serializer_class = ProductoSerializer

    def get_queryset(self):
        """
        Devuelve solo productos activos (disponible=True) y cuyos ingredientes tienen stock suficiente
        según la cantidad requerida en la receta (ProductoIngrediente).
        RF-02: Visualizar solo productos realmente disponibles en POS.
        """
        qs = super().get_queryset().filter(disponible=True)
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)

        # Filtrar productos por stock suficiente de ingredientes según la receta
        # Solo productos con receta y todos los ingredientes con stock >= cantidad requerida
        from django.db.models import F, OuterRef, Subquery, Exists
        from .models import ProductoIngrediente, Ingrediente

        # Solo productos con al menos una receta
        qs = qs.filter(productoingrediente__isnull=False).distinct()

        # Subconsulta: para cada producto, ¿existe algún ingrediente de la receta cuyo stock < cantidad requerida?
        pi_sub = ProductoIngrediente.objects.filter(
            producto=OuterRef('pk'),
            ingrediente__stock__lt=F('cantidad')
        )
        # Solo productos donde NO existe ningún ingrediente insuficiente
        qs = qs.annotate(
            tiene_faltante=Exists(pi_sub)
        ).filter(tiene_faltante=False)
        return qs

    @action(detail=True, methods=['post'], url_path='toggle-disponible')
    def toggle_disponible(self, request, pk=None):
        """Activar/desactivar producto sin pasar por el formulario completo."""
        producto = self.get_object()
        producto.disponible = not producto.disponible
        producto.save(update_fields=['disponible'])
        return Response({'id': producto.pk, 'disponible': producto.disponible})


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de categorías (solo lectura)."""
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer


class IngredienteViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de ingredientes con stock actual."""
    queryset = Ingrediente.objects.all().order_by('nombre')
    serializer_class = IngredienteSerializer
