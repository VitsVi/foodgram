from rest_framework.permissions import BasePermission

class IfMeAuthenticated(BasePermission):
    """
    Разрешает доступ только авторизованному пользователю, если в URL передано "me".
    """
    def has_object_permission(self, request, view, obj):
        if view.kwargs.get('pk') == 'me':
            if request.user.is_autenticated:
                return obj == request.user
            else:
                return False
        return True
