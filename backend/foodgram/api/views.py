from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from .permissions import IfMeAuthenticated
from .serializers import (
    UserProfileSerializer,
    ProfleAvatarSerializer,
    ChangeProfilePasswordSerializer,
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    ShoppingListSerializer,
    FavoriteRecipesSerializer,
    SubscribeSerializer,
)
from recipe.models import Tag, Recipe, Ingredient
from add_by_user.models import ShoppingList, FavoriteRecipes
from core.models import Subscribe

User = get_user_model()


class UserProfileViewset(viewsets.ModelViewSet):
    """Вьюсет для работы со страницей пользователей."""

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    http_method_names = ('get', 'post',)
    permission_classes = [IsAuthenticated, IfMeAuthenticated]

    def get_permissions(self):
        """
        Разрешаем всем доступ для POST-запроса,
        но проверка аутентификации для всех других действий.
        """

        if self.action == 'create' and self.kwargs.get('pk') == None:
            return []
        elif self.request.method=="GET":
            return []
        else:
            return super().get_permissions()

    def get_object(self):
        user_id = self.kwargs.get('pk')

        if user_id == 'me':
            #raise IsAuthenticated()
            return self.request.user

        user = get_object_or_404(User, id=user_id)

        is_subscribed = Subscribe.objects.filter(
                subscriber=self.request.user.id,
                author=user_id).exists()
        user.is_subscribed = is_subscribed
        return user


class ChangeProfilePasswordView(APIView):
    """Вью для смены пароля."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        # Проверяем, что текущий пароль верный
        if not check_password(current_password, user.password):
            return Response(
                {"current_password": "Неверный пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileAvatarViewset(viewsets.GenericViewSet):
    """Вьюсет для работы с аватаром пользователя."""

    serializer_class = ProfleAvatarSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['put', 'delete',]

    def update(self, request, *args, **kwargs):
        """Обновление аватара пользователя."""

        if not request.data:
            return Response(
                {"avatar": "can't be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User.objects.filter(
            id=self.request.user.id
        ).update(avatar=request.data["avatar"])
        return Response(
            {"avatar": "Аватар успешно обновлен"},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Удаление аватара пользователя."""
        User.objects.filter(id=self.request.user.id).update(avatar=None)
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class TagViewset(viewsets.ModelViewSet):
    """Вьюсет для тегов."""

    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = ()
    http_method_names = ('get')
    queryset = Tag.objects.all()


class RecipeViewset(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get','post','patch','delete')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tags','author')
    queryset = Recipe.objects.all()


class IngredientViewset(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов."""

    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = ()
    http_method_names = ('get')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    queryset = Ingredient.objects.all()
    
    def get_object(self):
        id = self.kwargs.get('pk')
        return get_object_or_404(Ingredient, id=id)
    

class ShoppingListViewset(viewsets.ModelViewSet):
    """Вьюсет для списка покупок."""

    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get','post','delete')
    
    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user)


class FavoriteRecipesViewset(viewsets.ModelViewSet):
    """Вьюсет для избранных рецептов."""

    serializer_class = FavoriteRecipesSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post','del')

    def get_queryset(self):
        return FavoriteRecipes.objects.filter(user=self.request.user)


class SubscribeWriteViewset(viewsets.ModelViewSet):
    """Вьюсет для управлением подписками пользователя."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post','delete')


class SubscribeReadViewset(viewsets.ModelViewSet):
    """Вьюсет вывода списка подписок."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get')
    
    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)