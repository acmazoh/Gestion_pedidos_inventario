from django.urls import path
from .views import ProductoListView, ProductoCreateView, ProductoUpdateView, ProductoDeleteView

urlpatterns = [
    path('', ProductoListView.as_view(), name='producto_list'),
    path('create/', ProductoCreateView.as_view(), name='producto_create'),
    path('<int:pk>/update/', ProductoUpdateView.as_view(), name='producto_update'),
    path('<int:pk>/delete/', ProductoDeleteView.as_view(), name='producto_delete'),
]