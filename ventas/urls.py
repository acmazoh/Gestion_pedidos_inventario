from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoVentaListView.as_view(), name='venta_list'),
    path('pedidos/', views.PedidoListView.as_view(), name='pedido_list'),
    path('pedidos/nuevo/', views.PedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detail'),
]