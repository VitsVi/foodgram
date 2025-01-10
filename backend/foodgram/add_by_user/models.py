from django.db import models
from django.contrib.auth import get_user_model
from recipe.models import Recipe
User = get_user_model()

class ShoppingList(models.Model):
    """Список покупок пользователя"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_list',
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        unique_together = ('user',)


    def __str__(self):
        return f"Список покупок {self.user.username}"
    

class FavoriteRecipes(models.Model):
    """Модель избранных рецептов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='favorite',
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user',)

    def __str__(self):
        return f"Избранные рецепты {self.user.username}"