from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя."""

    avatar = models.ImageField(
        verbose_name='Фото профиля',
        upload_to='users/',
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Подписки пользователей."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='prevent_self_subscription'
            )
        ]
        unique_together = ('subscriber', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        """Запрещаем подписку на самого себя."""
        if self.subscriber == self.author:
            raise ValidationError("Нельзя подписаться на самого себя.")

    def save(self, *args, **kwargs):
        """Вызываем валидацию перед сохранением."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
