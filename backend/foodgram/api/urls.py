from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewset,
    ProfileAvatarViewset,
    ChangeProfilePasswordView,
    TagViewset,
    RecipeViewset,
    IngredientViewset,
    ShoppingListViewset,
    FavoriteRecipesViewset,
    SubscribeReadViewset,
    SubscribeWriteViewset
)

router = DefaultRouter(trailing_slash=True)

# пользователи
router.register('users', UserProfileViewset, basename='users')

# теги
router.register('tags', TagViewset, basename='tags')

# ингредиенты
router.register(
    'ingredients',
    IngredientViewset,
    basename='ingredients'
)
# рецепты
router.register('recipes', RecipeViewset, basename='recipes')

# список покупок
router.register(
    r'users/(?P<user_id>\d+)/shopping_cart',
    ShoppingListViewset,
    basename='shopping_cart'
)

# избранное
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteRecipesViewset,
    basename='favorite'
)

# подписки
router.register(
    'users/subscriptions',
    SubscribeReadViewset,
    basename='subscriptions',
    )
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeWriteViewset,
    basename='subscribe'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/set_password/', ChangeProfilePasswordView.as_view(), name='password'),
    path('', include(router.urls)),
    path('users/me/avatar/', ProfileAvatarViewset.as_view(
        {'put': 'update', 'delete': 'destroy'}
    ), name='avatar'),
]