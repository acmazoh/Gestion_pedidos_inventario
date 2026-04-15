from django.urls import path
from .views import (
    ProductoListView, ProductoCreateView, ProductoUpdateView, ProductoDeleteView,
    IngredienteListView, IngredienteCreateView, IngredienteUpdateView, IngredienteDeleteView,
    MovimientoInventarioListView,
)

urlpatterns = [
    path('', ProductoListView.as_view(), name='producto_list'),
    path('create/', ProductoCreateView.as_view(), name='producto_create'),
    path('<int:pk>/update/', ProductoUpdateView.as_view(), name='producto_update'),
    path('<int:pk>/delete/', ProductoDeleteView.as_view(), name='producto_delete'),

    # Ingredientes (RF-15)
    path('ingredientes/', IngredienteListView.as_view(), name='ingrediente_list'),
    path('ingredientes/create/', IngredienteCreateView.as_view(), name='ingrediente_create'),
    path('ingredientes/<int:pk>/update/', IngredienteUpdateView.as_view(), name='ingrediente_update'),
    path('ingredientes/<int:pk>/delete/', IngredienteDeleteView.as_view(), name='ingrediente_delete'),

    # Historial de movimientos de inventario (RF-10)
    path('ingredientes/movimientos/', MovimientoInventarioListView.as_view(), name='movimiento_list'),
]