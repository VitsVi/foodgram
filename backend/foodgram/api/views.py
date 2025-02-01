from core.models import Subscribe
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (FavoriteRecipes, Ingredient, IngredientRecipe,
                           Recipe, ShoppingList, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .permissions import IfMeAuthenticated, IsAuthor
from .serializers import (IngredientSerializer, ProfleAvatarSerializer,
                          RecipeSerializer, SubscribeSerializer, TagSerializer,
                          UserProfileSerializer)

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

        if self.action == 'create' and self.kwargs.get('pk') is None:
            return []
        elif self.request.method == "GET" and self.kwargs.get('pk') != 'me':
            return []
        else:
            return super().get_permissions()

    def get_object(self):
        user_id = self.kwargs.get('pk')

        if user_id == 'me':
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
    http_method_names = ['put', 'delete']

    def update(self, request, *args, **kwargs):
        """Обновление аватара пользователя."""
        # if not request.data:
        #     return Response(
        #         {"avatar": "can't be empty."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # User.objects.filter(
        #     id=self.request.user.id
        # ).update(avatar=request.data["avatar"])
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('tags', 'author')
    filterset_fields = [
        'author',
        'tags',
        'is_in_shopping_cart',
        'is_favorited'
    ]
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_permissions(self):
        """Права доступа для рецептов."""
        if self.request.method == "GET":
            return []
        elif self.request.method in ['PATCH', 'PUT']:

            return [IsAuthor()]
        else:
            return super().get_permissions()

    def get_serializer_context(self):
        """Метод для передачи контекста."""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        return queryset

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Ссылка на рецепт."""
        try:
            recipe = self.get_object()
            link = request.build_absolute_uri(
                f"/api/recipes/{recipe.id}/get-link/"
            )
            return Response({"short-link": link}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Recipe not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def add_to_shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':

            shopping_list, created = ShoppingList.objects.get_or_create(
                user=user
            )

            if shopping_list.recipes.filter(id=recipe.id).exists():
                return Response(
                    {"detail": "Рецепт уже в корзине."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shopping_list.recipes.add(recipe)

            return Response({
                'id': recipe.id,
                'name': recipe.name,
                'image': request.build_absolute_uri(recipe.image.url),
                'cooking_time': recipe.cooking_time,
            }, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':

            shopping_list = ShoppingList.objects.filter(user=user).first()

            if not shopping_list:
                return Response(
                    {'detail': 'Список покупок пуст.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not shopping_list.recipes.filter(id=recipe.id).exists():
                return Response(
                    {'detail': 'Рецепта нет в корзине.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shopping_list.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Метод для объединения ингредиентов в список для загрузки."""
        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        return shopping_list

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Метод для загрузки ингредиентов."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return Response(shopping_list, content_type='text/plain')

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def add_or_remove_favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        # Получаем или создаем список покупок для пользователя
        if request.method == 'POST':
            favorite, created = FavoriteRecipes.objects.get_or_create(
                user=user
            )

            # Проверяем, есть ли уже рецепт в списке
            if favorite.recipes.filter(id=recipe.id).exists():
                return Response(
                    {"detail": "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Добавляем рецепт в список покупок
            favorite.recipes.add(recipe)

            return Response({
                'id': recipe.id,
                'name': recipe.name,
                'image': request.build_absolute_uri(recipe.image.url),
                'cooking_time': recipe.cooking_time,
            }, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':

            favorite = FavoriteRecipes.objects.filter(user=user).first()

            if not favorite:
                return Response(
                    {'detail': 'Список покупок пуст.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not favorite.recipes.filter(id=recipe.id).exists():
                return Response(
                    {'detail': 'Рецепта нет в корзине.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)


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


class SubscribeWriteViewset(viewsets.ModelViewSet):
    """Вьюсет для управлением подписками пользователя."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post', 'delete')

    def create(self, request, author_id=None):
        """Добавить рецепт в избранное."""
        author = get_object_or_404(User, id=author_id)
        user = request.user
        if Subscribe.objects.filter(subscriber=user, author=author).exists():
            return Response({'detail': 'Вы уже подписаны на этого автора.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription = Subscribe.objects.create(
            subscriber=user, author=author
        )

        serializer = SubscribeSerializer(subscription)
        serializer_data = serializer.data
        author_object = serializer_data.pop("author")
        recipes = serializer_data.pop('recipes')
        modify_recipes = []
        for recipe in recipes:
            modify_recipes.append({
                "id": recipe['id'],
                "name": recipe["name"],
                "image": recipe["image"],
                "cooking_time": recipe["cooking_time"],
            })
        serializer_data.update(author_object)
        serializer_data.update({"recipes": modify_recipes})

        return Response(serializer_data, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True, url_path='subscribe')
    def delete(self, request, author_id=None):
        """Удалить рецепт из избранного."""
        author = get_object_or_404(User, id=author_id)
        user = request.user

        subscribe = Subscribe.objects.filter(subscriber=user, author=author)
        if not subscribe.exists():
            return Response({'detail': 'Вы не подписаны на этого автора.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeReadViewset(viewsets.ModelViewSet):
    """Вьюсет вывода списка подписок."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    http_method_names = ('get')

    def get_queryset(self):

        return Subscribe.objects.filter(subscriber=self.request.user)

    def list(self, request, *args, **kwargs):
        """Вывод списка подписок."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            serialized_data = serializer.data
        for item in serialized_data:
            results_author = item.pop('author')
            results_recipes = item.pop('recipes')
            recipes = []
            for recipe in results_recipes:
                recipes.append({
                    "id": recipe['id'],
                    "name": recipe["name"],
                    "image": recipe["image"],
                    "cooking_time": recipe["cooking_time"],
                })
            item.update(results_author)
            item.update({"recipes": recipes})
        return self.get_paginated_response(serialized_data)
