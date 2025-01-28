from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ChangeProfilePasswordView, IngredientViewset,
                    ProfileAvatarViewset, RecipeViewset, SubscribeReadViewset,
                    SubscribeWriteViewset, TagViewset, UserProfileViewset)

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

router.register(
    r'users/(?P<author_id>\d+)/subscribe',
    SubscribeWriteViewset,
    basename='subscribe'
)

urlpatterns = [
    path('users/subscriptions/', SubscribeReadViewset.as_view(
        {'get': 'list'}
    ), name='subscriptions'),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/set_password/',
        ChangeProfilePasswordView.as_view(),
        name='password'
    ),
    path('', include(router.urls)),
    path('users/me/avatar/', ProfileAvatarViewset.as_view(
        {'put': 'update', 'delete': 'destroy'}
    ), name='avatar'),
]
