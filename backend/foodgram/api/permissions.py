from rest_framework.permissions import BasePermission, SAFE_METHODS


class IfMeAuthenticated(BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.kwargs.get('pk') == 'me':
            return (
                not request.user.is_authenticated
                or obj == request.user
            )
        return True


class IsAuthor(BasePermission):
    """Проверка авторских прав на изменение."""

    def has_object_permission(self, request, view, obj):
        """Проверка прав на объект (рецепт)."""
        return request.user == obj.author


class RecipePermission(BasePermission):
    """Проверка доступов к рецептам."""

    def has_permission(self, request, view):
        """Проверка доступа на уровне запроса."""
        return (
            request.method == "GET"
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверка доступа на уровне объекта (рецепта)."""
        return (
            (request.method in ['PATCH', 'PUT']
            and obj.author == request.user)
            or request.method in SAFE_METHODS
        )
