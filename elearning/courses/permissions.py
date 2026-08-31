from rest_framework import permissions


class IsTeacherOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read; only teachers can create courses (R1d)."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_teacher()


class IsCourseOwnerOrReadOnly(permissions.BasePermission):
    """Only the course's own teacher may update/delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher_id == request.user.id
