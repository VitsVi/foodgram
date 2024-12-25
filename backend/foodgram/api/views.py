from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, status, viewsets
from .permissions import IfMeAuthenticated
from .serializers import (
    TokenObtainByCodeSerializer,
    UserProfileSerializer,
    ProfleAvatarSerializer,
    ChangeProfilePasswordSerializer
)

User = get_user_model()


class GetTokenViewset(viewsets.ModelViewSet):
    serializer_class = TokenObtainByCodeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post')


class UserProfileViewset(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    http_method_names = ('get', 'post')

    def get_permissions(self):
        """
        Разрешаем всем доступ для POST-запроса (создание пользователя),
        но проверка аутентификации для всех других действий.
        """

        if self.action == 'create' and self.kwargs.get('pk') == None:
            return []
        else:
            return [IfMeAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        if user_id == 'me':
            raise IsAuthenticated()
        return get_object_or_404(User, id=user_id)


class ChangeProfilePasswordViewset(viewsets.ModelViewSet):
    serializer_class = ChangeProfilePasswordSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post')


class ProfileAvatarViewset(viewsets.ModelViewSet):
    serializer_class = ProfleAvatarSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('put','delete')

    def update(self, request, *args, **kwargs):
        User.objects.update(id=self.id, avatar=request.data["avatar"])
        return super().update(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        User.objects.update(id=self.id, avatar=None)
        return super().perform_destroy(instance)