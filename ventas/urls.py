from .api_views import PedidoCreateAPIView
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ProductoVentaListView.as_view(), name='venta_list'),
    path('pedidos/', views.PedidoListView.as_view(), name='pedido_list'),
    path('pedidos/nuevo/', views.PedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detail'),
    path('pedidos/<int:pk>/confirmar/', views.PedidoConfirmarView.as_view(), name='pedido_confirm'),

    # API en tiempo real para cocina (RF-08)
    path('api/pedidos/activos/', views.PedidosActivosAPIView.as_view(), name='api_pedidos_activos'),

    # Endpoint API REST para crear órdenes (RF-03)
    path('api/orders/create/', PedidoCreateAPIView.as_view(), name='api_order_create'),

    path('pedidos/cocina/', views.CocinaDashboardView.as_view(), name='cocina_dashboard'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/incrementar/', views.PedidoProductoQuantityUpdateView.as_view(), name='pedido_item_increment'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/disminuir/', views.PedidoProductoQuantityUpdateView.as_view(), name='pedido_item_decrement'),
    path('pedidos/<int:pedido_pk>/items/<int:item_pk>/eliminar/', views.PedidoProductoDeleteView.as_view(), name='pedido_item_delete'),

    # Nuevos estados de pedido (RF-09 / RF-11)
    path('pedidos/<int:pk>/listo/', views.PedidoMarcarListoView.as_view(), name='pedido_listo'),
    path('pedidos/<int:pk>/entregada/', views.PedidoMarcarEntregadaView.as_view(), name='pedido_entregada'),
    path('pedidos/<int:pk>/pagado/', views.PedidoMarcarPagadoView.as_view(), name='pedido_pagado'),

    # Historial de ventas (RF-11)
    path('ventas/historial/', views.HistorialVentasView.as_view(), name='historial_ventas'),
    path('ventas/historial/exportar/', views.ExportarHistorialCSVView.as_view(), name='historial_ventas_csv'),

    # API REST endpoints
    path('api/', include('ventas.api_urls')),
]