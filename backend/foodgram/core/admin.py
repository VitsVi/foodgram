from django.contrib import admin

# Register your models here.
from recipe.models import FavoriteRecipes, Recipe, ShoppingList

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    filter_horizontal = ['tags']

@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):

    list_display = ['user']
    filter_horizontal = ['recipes']

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):

    list_display = ['user']
    filter_horizontal = ['recipes']