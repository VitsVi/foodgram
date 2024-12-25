from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewset,
    ProfileAvatarViewset,
    GetTokenViewset,
    ChangeProfilePasswordViewset
)

router = DefaultRouter(trailing_slash=True)
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

urlpatterns = [
    #path(f'auth/signup/', SignUpViewset.as_view(), name='signup'),
    path('auth/', include('djoser.urls.authtoken')),
    # path(
    #     f'auth/token/login/',
    #     GetTokenViewset,
    #     name='get_token'
    # ),
    path('', include(router.urls)),
]