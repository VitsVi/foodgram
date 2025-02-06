from rest_framework.permissions import BasePermission


class IfMeAuthenticated(BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.kwargs.get('pk') == 'me':
            return (
                obj == request.user
                if request.user.is_authenticated
                else True
            )
        return True


class IsAuthor(BasePermission):
    """Проверка авторских прав на изменение."""

    def has_object_permission(self, request, view, obj):
        """Проверка прав на объект (рецепт)."""
        return True if request.user == obj.author else False


class RecipePermission(BasePermission):
    """Проверка доступов к рецептам."""

    def has_permission(self, request, view):
        return True if request.method == "GET" else \
            IsAuthor().has_object_permission(
                request, view, view.get_object()
            ) \
            if request.method in ['PATCH', 'PUT'] else \
            (request.user and request.user.is_authenticated)
