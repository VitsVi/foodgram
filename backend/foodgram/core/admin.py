from core.models import Subscribe, User
from django.contrib import admin
from recipe.models import (FavoriteRecipes, Ingredient, Recipe, ShoppingList,
                           Tag)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        'username',
        'first_name',
        'last_name',
        'avatar',
        'email',
        'is_superuser',
        'password',
    ]


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):

    list_display = ['author', 'subscriber']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'author',
        'cooking_time',
        'text',
    ]
    filter_horizontal = ['tags', 'ingredients']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ['name', 'slug']


@admin.register(Ingredient)
class IngedientAdmin(admin.ModelAdmin):

    list_display = ['name', 'measurement_unit']


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):

    list_display = ['user']
    filter_horizontal = ['recipes']


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):

    list_display = ['user']
    filter_horizontal = ['recipes']
