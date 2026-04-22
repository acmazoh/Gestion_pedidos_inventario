from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Producto, Categoria, Ingrediente
from .serializers import ProductoSerializer, CategoriaSerializer, IngredienteSerializer
from users.permissions import HasRolePermission
from rest_framework import serializers



# --- Versión limpia y fusionada de ProductoViewSet ---
from django.db.models import F, OuterRef, Exists
from .models import ProductoIngrediente

class ProductoViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para Productos del menú.
    RF-01: gestión admin | RF-02: catálogo POS
    """
    queryset = Producto.objects.select_related('categoria').prefetch_related(
        'ingredientes', 'productoingrediente_set__ingrediente'
    ).order_by('categoria__nombre', 'nombre')
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'toggle_disponible']:
            return [HasRolePermission('full_access')]
        return [HasRolePermission('view_products')]

    def get_queryset(self):
        qs = super().get_queryset()
        disponible = self.request.query_params.get('disponible')
        if disponible is not None:
            qs = qs.filter(disponible=disponible.lower() == 'true')
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        # Filtro productos cuyos ingredientes tienen stock suficiente según receta
        if disponible and disponible.lower() == 'true':
            qs = qs.filter(productoingrediente__isnull=False).distinct()
            pi_sub = ProductoIngrediente.objects.filter(
                producto=OuterRef('pk'),
                ingrediente__stock__lt=F('cantidad')
            )
            qs = qs.annotate(
                tiene_faltante=Exists(pi_sub)
            ).filter(tiene_faltante=False)
        return qs

    @action(detail=True, methods=['post'], url_path='toggle-disponible')
    def toggle_disponible(self, request, pk=None):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_active or not profile.role or profile.role.name != 'admin':
            return Response({'error': 'Solo el administrador puede activar/desactivar productos.'}, status=403)
        producto = self.get_object()
        producto.disponible = not producto.disponible
        producto.save(update_fields=['disponible'])
        return Response({'id': producto.pk, 'disponible': producto.disponible})


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de categorías (solo lectura)."""
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        return [HasRolePermission('view_products')]



# --- Versión limpia y avanzada de IngredienteViewSet ---
class IngredienteViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """CRUD de ingredientes. Solo admin puede crear, editar o eliminar."""
    queryset = Ingrediente.objects.all().order_by('nombre')
    serializer_class = IngredienteSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [HasRolePermission('full_access')]
        return [HasRolePermission('view_products')]

    def perform_create(self, serializer):
        nombre = serializer.validated_data['nombre']
        if Ingrediente.objects.filter(nombre__iexact=nombre).exists():
            raise serializers.ValidationError({'nombre': 'Ya existe un ingrediente con ese nombre.'})
        stock = serializer.validated_data.get('stock', 0)
        if stock < 0:
            raise serializers.ValidationError({'stock': 'La cantidad debe ser mayor o igual a 0.'})
        serializer.save()

    def perform_update(self, serializer):
        nombre = serializer.validated_data.get('nombre', None)
        if nombre and Ingrediente.objects.filter(nombre__iexact=nombre).exclude(pk=serializer.instance.pk).exists():
            raise serializers.ValidationError({'nombre': 'Ya existe un ingrediente con ese nombre.'})
        stock = serializer.validated_data.get('stock', 0)
        if stock < 0:
            raise serializers.ValidationError({'stock': 'La cantidad debe ser mayor o igual a 0.'})
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_active or not profile.role or profile.role.name != 'admin':
            return Response({'error': 'Solo el administrador puede eliminar ingredientes.'}, status=403)
        return super().destroy(request, *args, **kwargs)
