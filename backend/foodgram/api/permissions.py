from rest_framework.permissions import BasePermission


class IfMeAuthenticated(BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.kwargs.get('pk') == 'me':
            if request.user.is_authenticated:
                return obj == request.user
            else:
                return False
        return True


class IsAuthor(BasePermission):
    """Проверка авторских прав на изменение."""

    def has_object_permission(self, request, view, obj):
        """Проверка прав на объект (рецепт)."""
        if request.user == obj.author:
            return True
        return False
