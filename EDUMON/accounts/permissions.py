from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """Grants access only to authenticated teachers (R1c)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read; only the object's owner can write."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
