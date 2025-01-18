from rest_framework import filters
from django_filters import rest_framework as django_filters
from recipe.models import Recipe
from django.db.models import Q

class RecipeFilter(django_filters.FilterSet):
    """Фильтрация рецептов."""

    is_in_shopping_cart = django_filters.BooleanFilter(field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')
    tags = django_filters.CharFilter(field_name='tags__slug', method='filter_tags')
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags','is_in_shopping_cart', 'is_favorited']

    def filter_tags(self, queryset, name, value):
        """Фильтрация по тегам"""

        tag_slugs = self.request.GET.getlist('tags')

        if not tag_slugs:
            return queryset

        query = Q()
        for tag_slug in tag_slugs:
            query |= Q(tags__slug=tag_slug)

        return queryset.filter(query)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по полю is_in_shopping_cart."""

        if value:
            user = self.request.user
            return queryset.filter(shopping_list__user_id=user.id)
        return queryset
    
    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по полю is_favorited."""
        if value is not None:
            user = self.request.user
            if user.is_anonymous:
                return queryset
            if value:  # Если значение True, фильтруем по избранному
                return queryset.filter(favorited__user=user)
            else:  # Если значение False, фильтруем рецепты, которые не в избранном
                return queryset.exclude(favorited__user=user)
        return queryset