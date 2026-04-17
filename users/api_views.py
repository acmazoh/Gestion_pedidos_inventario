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
