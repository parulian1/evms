from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Owners of object or Admin
    TODO : Do check also for Admin user to allow permissions
    """
    def has_access(self, user, view, obj=None):
        if user and user.is_authenticated and (user.is_staff or user.is_superuser) and user.is_active:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_access(request.user, view, obj)

    def has_permission(self, request, view):
        return self.has_access(request.user, view)


class IsReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
        )
