from rest_framework.permissions import SAFE_METHODS, BasePermission


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
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
