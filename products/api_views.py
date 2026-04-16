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
        qs = super().get_queryset()
        # Filtro ?disponible=true|false para RF-02 (POS solo muestra activos)
        disponible = self.request.query_params.get('disponible')
        if disponible is not None:
            qs = qs.filter(disponible=disponible.lower() == 'true')
        # Filtro por categoría
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
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
