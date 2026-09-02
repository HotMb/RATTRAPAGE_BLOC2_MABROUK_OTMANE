from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == User.Role.ADMIN


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )
