from django.urls import path
from .api_views import AuthLoginAPIView, AuthLogoutAPIView
from .views import UserViewSet

user_create = UserViewSet.as_view({'post': 'create_user'})
user_update_role = UserViewSet.as_view({'put': 'update_role'})
user_deactivate = UserViewSet.as_view({'delete': 'deactivate'})

urlpatterns = [
    path('login', AuthLoginAPIView.as_view(), name='api_auth_login'),
    path('logout', AuthLogoutAPIView.as_view(), name='api_auth_logout'),
    path('users/', user_create, name='api_user_create'),
    path('users/<int:pk>/role', user_update_role, name='api_user_update_role'),
    path('users/<int:pk>/deactivate', user_deactivate, name='api_user_deactivate'),
]
