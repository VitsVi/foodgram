from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from foodgram import settings

class User(AbstractUser):
    """Расширенная модель пользователя."""

    avatar = models.ImageField(
        verbose_name='Фото профиля',
        null=True,
    )

    # # cмена related_name для полей
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='core_user_groups',
    #     blank=True,
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='core_user_permissions',
    #     blank=True,
    # )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Подписки пользователей."""

    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"