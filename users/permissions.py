from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    def has_permission(self, request, view):
        required_roles = getattr(view, "allowed_roles", None)
        if required_roles is None:
            return True  # default open
        return request.user.is_authenticated and request.user.role in required_roles