from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PedidoViewSet, PedidosActivosAPIView, RegistrarVentaAPIView

router = DefaultRouter()
router.register(r'orders', PedidoViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('pedidos/activos/', PedidosActivosAPIView.as_view(), name='api_pedidos_activos'),
    path('sales/register/', RegistrarVentaAPIView.as_view(), name='api_sales_register'),
]
