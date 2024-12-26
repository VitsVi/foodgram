from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

MAX_LENGTH_TAG = 50
CHAR_MAX_LENGTH = 256 

class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='имя',
        max_length=MAX_LENGTH_TAG,
        unique=True
    )

    slug = models.SlugField(
        verbose_name='slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    
    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=CHAR_MAX_LENGTH,
        null=False
    )

    unit_measure = models.CharField(
        verbose_name='Единица измерения',
        max_length=CHAR_MAX_LENGTH,
        null=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self):
        return self.name
    

class Recipe(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор'
    )

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=CHAR_MAX_LENGTH,
    )

    image = models.ImageField(
        verbose_name='Изображение',
    )

    text = models.CharField(
        verbose_name='Описание',
        max_length=CHAR_MAX_LENGTH,
    )

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Ингредиенты',
    )

    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Теги',
    )

    coocking_time = models.TimeField(
        verbose_name='Время приготовления(мин)',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self):
        return self.name