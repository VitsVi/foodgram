import base64
import uuid

from core.models import Subscribe
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator, validate_email
# from django.db.models import Count
from recipe.models import (FavoriteRecipes, Ingredient, IngredientRecipe,
                           Recipe, ShoppingList, Tag)
from rest_framework import serializers

User = get_user_model()

MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
AMOUNT_MIN = 0


class UserRequiredFieldsSerializerMixin(serializers.ModelSerializer):
    """Миксин для сериалайзеров с использованием модели юзера."""

    username = serializers.CharField(
        max_length=MAX_LENGTH,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=('Поле может содержать буквы, '
                     'цифры, и символы: @/./+/-/_ .')
        )]
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        validators=[validate_email],
        required=True
    )


class UserProfileSerializer(
    UserRequiredFieldsSerializerMixin,
    serializers.ModelSerializer
):
    """Сериалайзер для работы с запросами к страницам пользователей."""

    first_name = serializers.CharField(max_length=MAX_LENGTH, required=True)
    last_name = serializers.CharField(max_length=MAX_LENGTH, required=True)
    password = serializers.CharField(max_length=MAX_LENGTH, required=True)
    avatar = serializers.ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'last_name',
            'first_name',
            'password',
            'email',
            'avatar',
            'is_subscribed'
        ]

    def validate(self, data):

        view = self.context['view']
        obj_pk = view.kwargs.get('pk')
        if obj_pk:
            # при запросе отдельной страницы
            if obj_pk == 'me':
                user_object = User.objects.get(id=self.id)
            else:
                user_object = User.objects.get(id=obj_pk)
            return user_object
        # при создании нового пользователя
        username = data.get('username')
        user_email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username': [
                    ('Логин уже занят.')
                ]
            })
        if User.objects.filter(email=user_email).exists():
            raise serializers.ValidationError({
                'email': ['Введенный адрес уже занят.']
            })
        return data

    def create(self, validated_data):
        user_object = User.objects.create_user(**validated_data)
        return user_object

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            subscriber = request.user
            return Subscribe.objects.filter(
                subscriber=subscriber, author=obj
            ).exists()
        return False

    def to_representation(self, instance):
        """Исключить поле 'password','avatar' из ответа."""
        representation = super().to_representation(instance)
        representation.pop('password', None)
        request = self.context.get('request')
        if request and 'users' in request.path:
            if request.method == 'POST':
                representation.pop('avatar', None)
                representation.pop('is_subscribed', None)
        return representation


class ChangeProfilePasswordSerializer(serializers.ModelSerializer):
    """Смена пароля профиля."""

    new_password = serializers.CharField(
        max_length=MAX_LENGTH,
        required=True
    )
    current_password = serializers.CharField(
        max_length=MAX_LENGTH,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'password',
        ]

    def validate(self, data):
        current_pass = data.get("current_password")
        new_pass = data.get("new_password")
        if new_pass == current_pass:
            raise serializers.ValidationError({
                'new_password': [
                    'Новый пароль не может быть равен старому.',
                ],
            })
        return data

    def create(self, validated_data):
        User.objects.update(
            id=self.id,
            password=validated_data['new_password']
        )
        return super().create(validated_data)


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""

    def to_internal_value(self, data):
        """Метод преобразования картинки."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            if ext not in ["jpeg", "jpg", "png"]:
                raise serializers.ValidationError(
                    "Неподдерживаемый формат изображения."
                )
            random_name = uuid.uuid4().hex
            data = ContentFile(
                base64.b64decode(imgstr), name=f'{random_name}.' + ext
            )

        return super().to_internal_value(data)


class ProfleAvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер работы с аватарами пользователей."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = [
            'avatar',
        ]


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Tag."""

    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'slug',
        ]


class IngredientInputSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных ингредиентов."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']

    def validate_amount(self, value):

        amount = value
        if amount <= AMOUNT_MIN:
            raise serializers.ValidationError(
                "Количество должно быть больше 0."
            )
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = IngredientInputSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    image = Base64ImageField(use_url=True)
    cooking_time = serializers.IntegerField(min_value=1)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserProfileSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'author',
            'id',
            'tags',
            'name',
            'image',
            'text',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        ]

    def validate(self, data):
        """Проверка наличия полей в запросе."""
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        if not tags:
            raise serializers.ValidationError(
                {"tags": "Поле обязательно для заполнения."}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Поле обязательно для заполнения."}
            )

        return data

    def validate_ingredients(self, value):
        """Проверка получаемых данных в поле ингедиентов."""
        if not value:
            raise serializers.ValidationError(
                {"ingredients": "Поле не может быть пустым."}
            )
        ids = []
        for item in value:
            id = item.get("id")
            amount = int(item.get('amount'))
            if not Ingredient.objects.filter(id=id).exists():
                raise serializers.ValidationError(
                    {"ingredients": f"Ингредиента с id {id} не существует."}
                )
            if amount <= AMOUNT_MIN or amount is None:
                raise serializers.ValidationError(
                    {"ingredients": (
                        f"""Количество ингредиента
                         должно быть больше {AMOUNT_MIN}"""
                    )}
                )
            if id in ids:
                raise serializers.ValidationError(
                    {"ingredients": (
                        """Поле не может содержать
                         повторяющиеся id ингредиентов."""
                    )}
                )
            ids.append(id)
        ids = []

        return value

    def validate_tags(self, value):
        """Валидация для поля тегов."""
        if not value:
            raise serializers.ValidationError(
                {'tags': "Поле не может быть пустым."}
            )
        ids = []
        for id in value:
            if id in ids:
                raise serializers.ValidationError(
                    {"tags": "id не могут повторяться."}
                )
            ids.append(id)
        ids = []

        return value

    def validate_image(self, value):
        """Валидация для поля изображения."""
        if not value:
            raise serializers.ValidationError(
                {"image": "Поле не может быть пустым."}
            )

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        recipe.tags.set(tags_data)
        return recipe

    def get_ingredients(self, obj):
        """Возвращает список ингредиентов."""
        ingredient_recipes = IngredientRecipe.objects.filter(recipe=obj)
        return [
            {
                'id': ingredient_recipe.ingredient.id,
                'name': ingredient_recipe.ingredient.name,
                'measurement_unit': (
                    ingredient_recipe.ingredient.measurement_unit
                ),
                'amount': ingredient_recipe.amount
            }
            for ingredient_recipe in ingredient_recipes
        ]

    def update(self, instance, validated_data):
        """Метод обновления модели."""
        # Удаляем старые связи
        instance.ingredients.clear()
        instance.tags.clear()

        # Обновляем ингредиенты
        ingredients_data = validated_data.pop('ingredients', [])

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.filter(
                id=ingredient_data["id"]
            ).first()
            IngredientRecipe.objects.get_or_create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data["amount"]
            )

        # Обновляем теги
        tags_data = validated_data.pop('tags', [])
        tags = []
        for tag_id in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_id)
            tags.append(tag)
        instance.tags.set(tags)

        # Обновляем остальные поля рецепта
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Преобразование id тегов и ингредиентов в объекты."""
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        representation['ingredients'] = self.get_ingredients(instance)
        representation['image'] = str(representation['image'])
        return representation

    def get_is_favorited(self, obj):
        """Метод проверки на добавление в избранное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(
            user=request.user, recipes=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки на присутствие в корзине."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipes=obj
        ).exists()


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Списка покупок."""

    recipes = RecipeSerializer(many=True, read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ShoppingList
        fields = [
            'user',
            'recipes',
        ]


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Ибранных рецептов."""

    recipes = RecipeSerializer(many=True, read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ShoppingList
        fields = [
            'user',
            'recipes',
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для подписок пользователя."""

    author = UserProfileSerializer(read_only=True)
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Subscribe
        fields = [
            'author',
            'recipes_count',
            'recipes',
        ]

    def validate(self, data):
        # Извлекаем ID пользователя из URL
        obj_id = self.context['view'].kwargs.get('pk')

        if obj_id is None:
            raise serializers.ValidationError(
                {"detail": "Пользователь не указан."}
            )

        # Проверяем, существует ли такой пользователь
        if not User.objects.filter(id=obj_id).exists():
            raise serializers.ValidationError(
                {"detail": "Пользователь не существует."}
            )

        # Проверка, не пытается ли пользователь подписаться на себя
        if self.request.user.id == int(obj_id):
            raise serializers.ValidationError(
                {"detail": "Вы не можете подписаться на себя."}
            )

        return data

    # def get_recipes_count(self, instance):
    #     """Подсчет количества рецептов автора."""
    #     return Recipe.objects.filter(author=instance.author).aggregate(
    #         total_recipes=Count('id')
    #     )['total_recipes']
    def get_recipes_count(self, instance):
        """Метод для получения количества рецептов"""

        return Recipe.objects.filter(id=instance.author.id).count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        recipes = Recipe.objects.filter(id=instance.author.id)
        data['recipes'] = RecipeSerializer(recipes, many=True).data
        return data
    # def get_recipes(self, instance):
    #     """Получение списка рецептов автора."""
    #     recipes = Recipe.objects.filter(author=instance.author)
    #     return RecipeSerializer(recipes, many=True).data
