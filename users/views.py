from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Role
from .serializers import RoleSerializer
from django import forms

# Formulario para Role
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'permissions']

# Listar roles
class RoleListView(ListView):
    model = Role
    template_name = 'users/role_list.html'
    context_object_name = 'roles'

# Crear rol
class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'users/role_form.html'
    success_url = reverse_lazy('role_list')

# Editar rol
class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'users/role_form.html'
    success_url = reverse_lazy('role_list')

# Eliminar rol
class RoleDeleteView(DeleteView):
    model = Role
    template_name = 'users/role_confirm_delete.html'
    success_url = reverse_lazy('role_list')
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
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_active or not profile.role or profile.role.name != 'admin':
            return Response({'error': 'Solo el administrador puede crear usuarios.'}, status=403)
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_role(self, request, pk=None):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_active or not profile.role or profile.role.name != 'admin':
            return Response({'error': 'Solo el administrador puede cambiar roles.'}, status=403)
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
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_active or not profile.role or profile.role.name != 'admin':
            return Response({'error': 'Solo el administrador puede desactivar usuarios.'}, status=403)
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
