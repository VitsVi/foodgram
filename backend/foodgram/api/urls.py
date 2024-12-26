from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewset,
    ProfileAvatarViewset,
    GetTokenViewset,
    ChangeProfilePasswordViewset,
    TagViewset,
    RecipeViewset,
    IngredientViewset,
    ShoppingListViewset,
    FavoriteRecipesViewset,
)

router = DefaultRouter(trailing_slash=True)

# пользователи
router.register('users', UserProfileViewset, basename='users')

router.register(
    r'users/me/avatar',
    ProfileAvatarViewset,
    basename='avatar'
)
router.register(
    r'users/set_password',
    ChangeProfilePasswordViewset,
    basename='set_password'
)

router.register('tags', TagViewset, basename='tags')
router.register(
    'ingredients',
    IngredientViewset,
    basename='ingredients'
)
router.register('recipes', RecipeViewset, basename='recipes')
router.register(
    r'users/(?P<user_id>\d+)/shopping_cart',
    ShoppingListViewset,
    basename='shopping_cart'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteRecipesViewset,
    basename='favorite'
)
urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]