from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.JSONField(default=dict)  # Store permissions as JSON

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # For soft delete

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"

    class Meta:
        db_table = 'user_profiles'
