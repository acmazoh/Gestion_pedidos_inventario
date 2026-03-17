from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoVentaListView.as_view(), name='venta_list'),
    path('pedidos/', views.PedidoListView.as_view(), name='pedido_list'),
    path('pedidos/nuevo/', views.PedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detail'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/incrementar/', views.PedidoProductoQuantityUpdateView.as_view(), name='pedido_item_increment'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/disminuir/', views.PedidoProductoQuantityUpdateView.as_view(), name='pedido_item_decrement'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/eliminar/', views.PedidoProductoDeleteView.as_view(), name='pedido_item_delete'),
]