from rest_framework.permissions import BasePermission
from recipe.models import Recipe

class IfMeAuthenticated(BasePermission):
    """
    Разрешает доступ только авторизованному пользователю, если в URL передано "me".
    """
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
        # Проверка, что пользователь авторизован и является автором рецепта
        if request.user == obj.author:
            return True
        return False