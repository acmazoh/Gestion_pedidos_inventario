from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Role, UserProfile
from .serializers import UserCreateSerializer, UserUpdateSerializer, UserProfileSerializer, RoleSerializer
from .permissions import IsAdmin

class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_role(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            profile_serializer = UserProfileSerializer(user.userprofile)
            return Response(profile_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def deactivate(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            profile = user.userprofile
            profile.is_active = False
            profile.save()
            return Response({'message': 'User deactivated'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
