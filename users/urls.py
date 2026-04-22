from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import me_view

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/me/', me_view, name='api_me'),
]