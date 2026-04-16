from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductoViewSet, CategoriaViewSet, IngredienteViewSet

router = DefaultRouter()
router.register(r'products', ProductoViewSet, basename='product')
router.register(r'categories', CategoriaViewSet, basename='category')
router.register(r'ingredients', IngredienteViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
