from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PedidoViewSet

router = DefaultRouter()
router.register(r'orders', PedidoViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
