from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, status, viewsets
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
    """Вьюсет для смены пароля."""

    serializer_class = ChangeProfilePasswordSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post')


class ProfileAvatarViewset(viewsets.ModelViewSet):
    """Вьюсет для работы с аватаром пользователя."""

    serializer_class = ProfleAvatarSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('put','delete')

    def update(self, request, *args, **kwargs):
        User.objects.update(id=self.id, avatar=request.data["avatar"])
        return super().update(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        User.objects.update(id=self.id, avatar=None)
        return super().perform_destroy(instance)
    

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
    search_fields = ('name',)
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


class SubscribeViewset(viewsets.ModelViewSet):
    """Вьюсет для подписок пользователей."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get','post','delete')

    def get_queryset(self):
        return Subscribe.objects.filter(subscriber=self.request.user)