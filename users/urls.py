from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import me_view

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

from .api_views import me_view

urlpatterns = [
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/nuevo/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/editar/', views.RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/eliminar/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('api/auth/me/', me_view, name='me_view'),
    path('api/', include(router.urls)),
    path('api/me/', me_view, name='api_me'),
]