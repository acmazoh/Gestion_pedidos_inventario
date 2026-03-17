from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoVentaListView.as_view(), name='venta_list'),
    path('nuevo/', views.PedidoCreateView.as_view(), name='pedido_create'),
]