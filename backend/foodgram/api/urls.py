from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ChangeProfilePasswordView, IngredientViewset,
                    ProfileAvatarViewset, RecipeViewset, SubscribeReadViewset,
                    SubscribeWriteViewset, TagViewset, UserProfileViewset)

router_v1 = DefaultRouter(trailing_slash=True)

# пользователи
router_v1.register('users', UserProfileViewset, basename='users')

# теги
router_v1.register('tags', TagViewset, basename='tags')

# ингредиенты
router_v1.register(
    'ingredients',
    IngredientViewset,
    basename='ingredients'
)
# рецепты
router_v1.register('recipes', RecipeViewset, basename='recipes')

router_v1.register(
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
    path('', include(router_v1.urls)),
    path('users/me/avatar/', ProfileAvatarViewset.as_view(
        {'put': 'update', 'delete': 'destroy'}
    ), name='avatar'),
]
