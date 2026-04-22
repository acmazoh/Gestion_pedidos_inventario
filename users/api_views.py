from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
import time

# Rate limiting: máximo 5 intentos fallidos por usuario/IP cada 15 minutos
MAX_ATTEMPTS = 5
BLOCK_TIME = 15 * 60  # 15 minutos en segundos

def get_cache_key(username, ip):
    return f"login_attempts:{username}:{ip}"

class AuthLoginAPIView(TokenObtainPairView):
    """Endpoint POST /api/auth/login con rate limiting y errores claros."""
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        ip = request.META.get('REMOTE_ADDR', '')
        cache_key = get_cache_key(username, ip)
        attempts = cache.get(cache_key, 0)
        if attempts >= MAX_ATTEMPTS:
            return Response({"error": "Demasiados intentos fallidos. Intenta en 15 minutos."}, status=429)
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            cache.set(cache_key, attempts + 1, BLOCK_TIME)
        else:
            cache.delete(cache_key)
        return response

class AuthLogoutAPIView(APIView):
    """Endpoint POST /api/auth/logout para blacklist de refresh token."""
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({"error": "Refresh token requerido."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Token inválido o ya bloqueado."}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from users.models import UserProfile

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    profile = getattr(user, 'userprofile', None)
    role = profile.role.name if profile and profile.role else None
    return Response({
        'username': user.username,
        'role': role,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    })
