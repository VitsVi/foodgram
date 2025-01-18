from django.db import models
from django.core import validators
from django.contrib.auth import get_user_model

User = get_user_model()

MAX_LENGTH_TAG = 50
CHAR_MAX_LENGTH = 256
SLUG_LENGTH = 100

class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='имя',
        max_length=MAX_LENGTH_TAG,
        unique=True
    )

    slug = models.SlugField(
        verbose_name='slug',
        max_length=SLUG_LENGTH,
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
    measurement_unit = models.CharField(
        max_length=CHAR_MAX_LENGTH,
        verbose_name='Единица измерения',
        default='Не указано',
        null=False,
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

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipe',
        verbose_name='Ингредиенты',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Теги',
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(мин)',
        validators=[
            validators.MinValueValidator(
                1, message='Минимальное значение 1'
            ),
        ]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)
    
    def __str__(self):
        return self.name
    

class IngredientRecipe(models.Model):
    """Промежуточная модель для связи ингредиентов с рецептом."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_links'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_links'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            validators.MinValueValidator(1, message='Минимальное количество 1'),
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
    
    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
    

class TagInRecipe(models.Model):
    """Модель тегов для рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        related_name='tag_link',
        help_text='Выбор тега для рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_link',
        help_text='Выбор рецепта',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        return f"{self.tag} {self.recipe}"
    

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
        related_name='favorite_recipes',
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='favorited',
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user',)

    def __str__(self):
        return f"Избранные рецепты {self.user.username}"