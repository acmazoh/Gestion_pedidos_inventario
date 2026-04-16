from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Role, UserProfile

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    role = RoleSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'is_active']

class UserCreateSerializer(serializers.ModelSerializer):
    role_id = serializers.IntegerField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'role_id']

    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        role = Role.objects.get(id=role_id)
        UserProfile.objects.create(user=user, role=role)
        return user

class UserUpdateSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()

    def update(self, instance, validated_data):
        role_id = validated_data['role_id']
        role = Role.objects.get(id=role_id)
        profile = instance.userprofile
        profile.role = role
        profile.save()
        return instance