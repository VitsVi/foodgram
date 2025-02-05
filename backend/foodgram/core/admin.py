from core.models import Subscribe, User
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from recipe.models import (FavoriteRecipes, Ingredient, IngredientRecipe,
                           Recipe, ShoppingList, Tag)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_superuser'
    )
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = (
        ("Основная информация", {"fields": ('username', 'email')}),
        ("Персональные данные", {"fields": (
            'first_name',
            'last_name',
            'avatar'
        )}),
        ("Права доступа", {"fields": (
            'is_active',
            'is_staff',
            'is_superuser'
        )}),
    )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ('id', 'subscriber', 'author')
    list_filter = ('author',)
    search_fields = ('subscriber__username', 'author__username')


class IngredientRecipeInlineFormset(BaseInlineFormSet):
    """Форма для валидации ингредиентов в рецепте."""

    def clean(self):
        """Проверяем, что хотя бы один ингредиент добавлен."""
        super().clean()
        if not any(
            form.cleaned_data and not form.cleaned_data.get(
                "DELETE", False
            ) for form in self.forms
        ):
            raise ValidationError(
                "Рецепт должен содержать хотя бы один ингредиент."
            )


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    formset = IngredientRecipeInlineFormset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
        'favorites_count'
    )
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    filter_horizontal = ('tags',)
    ordering = ('id',)
    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        """Подсчет количества добавлений рецепта в избранное."""
        return obj.favorited.count()
    favorites_count.short_description = "В избранном"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    """Админка избранных рецептов."""

    list_display = ('id', 'user', 'recipes_count')
    filter_horizontal = ('recipes',)

    def recipes_count(self, obj):
        """Подсчет количества рецептов в избранном."""
        return obj.recipes.count()
    recipes_count.short_description = "Количество рецептов"


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = ('id', 'user', 'recipes_count')
    filter_horizontal = ('recipes',)

    def recipes_count(self, obj):
        """Подсчет количества рецептов в списке покупок."""
        return obj.recipes.count()
    recipes_count.short_description = "Количество рецептов"
