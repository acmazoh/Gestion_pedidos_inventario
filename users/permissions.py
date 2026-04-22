from rest_framework.permissions import BasePermission

ROLE_PERMISSIONS = {
    'admin': [
        'full_access', 'manage_users', 'manage_orders', 'manage_payments',
        'view_orders', 'view_products', 'create_orders', 'edit_products', 'delete_products'
    ],
    'cashier': [
        'manage_payments', 'manage_orders', 'view_orders', 'view_products', 'create_orders'
    ],
    'kitchen': [
        'view_orders', 'update_order_status', 'view_products'
    ],
    'waiter': [
        'create_orders', 'manage_orders', 'view_orders', 'view_products'
    ],
}

class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.userprofile
            return profile.role and profile.role.name == 'admin' and profile.is_active
        except:
            return False

class HasRolePermission(BasePermission):
    """
    Check if user has specific permission based on role.
    """
    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.userprofile
            if not profile.is_active or not profile.role:
                return False
            permissions = ROLE_PERMISSIONS.get(profile.role.name, [])
            # Admin siempre puede todo
            if profile.role.name == 'admin':
                return True
            return self.required_permission in permissions
        except Exception as e:
            return False