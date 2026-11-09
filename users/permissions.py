from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        # Проверка для Course и Lesson
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        # Проверка для User
        if hasattr(obj, "email"):
            return obj == request.user
        return False


class IsOwnerOrModerator(BasePermission):
    """Проверяет, является ли пользователь владельцем ИЛИ модератором."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Модераторы могут редактировать любые объекты
        if request.user.groups.filter(name="Модераторы").exists():
            return True
        # Обычные пользователи могут редактировать только свои объекты
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "email"):
            return obj == request.user
        return False


class IsNotModerator(BasePermission):
    """Проверяет, что пользователь НЕ является модератором."""

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Модераторы").exists()
