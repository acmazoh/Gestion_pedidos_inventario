from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoVentaListView.as_view(), name='venta_list'),
    path('pedidos/', views.PedidoListView.as_view(), name='pedido_list'),
    path('pedidos/nuevo/', views.PedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detail'),
    path('pedidos/<int:pk>/confirmar/', views.PedidoConfirmarView.as_view(), name='pedido_confirm'),
    path('pedidos/cocina/', views.CocinaDashboardView.as_view(), name='cocina_dashboard'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/incrementar/', views.PedidoProductoQuantityUpdateView.as_view(), name='pedido_item_increment'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/disminuir/', views.PedidoProductoQuantityUpdateView.as_view(), name='pedido_item_decrement'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/eliminar/', views.PedidoProductoDeleteView.as_view(), name='pedido_item_delete'),

    # Nuevos estados de pedido (RF-09 / RF-11)
    path('pedidos/<int:pk>/listo/', views.PedidoMarcarListoView.as_view(), name='pedido_listo'),
    path('pedidos/<int:pk>/entregada/', views.PedidoMarcarEntregadaView.as_view(), name='pedido_entregada'),

    # Historial de ventas (RF-11)
    path('ventas/historial/', views.HistorialVentasView.as_view(), name='historial_ventas'),
    path('ventas/historial/exportar/', views.ExportarHistorialCSVView.as_view(), name='historial_ventas_csv'),
]