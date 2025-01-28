from core.models import Subscribe
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from recipe.models import (FavoriteRecipes, Ingredient, IngredientRecipe,
                           Recipe, ShoppingList, Tag)

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных объектами для тестов'

    def handle(self, *args, **options):
        try:
            users = [
                {
                    "username": "chef1",
                    "email": "chef1@example.com",
                    "password": "password123",

                    "first_name": "username_1",
                    "last_name": "last_username_1",
                },
                {
                    "username": "chef2",
                    "email": "chef2@example.com",
                    "password": "password123",

                    "first_name": "username_2",
                    "last_name": "last_username_2",
                },
                {
                    "username": "chef3",
                    "email": "chef3@example.com",
                    "password": "password123",

                    "first_name": "username_3",
                    "last_name": "last_username_3",
                },
            ]
            user_objects = [User.objects.create_user(**user) for user in users]
            print(f"Создано пользователей: {User.objects.count()}")

        except Exception as e:
            print('USERS. ', e)

        try:
            # Создание тестовых тегов
            tags = [
                Tag.objects.create(name="Завтрак", slug='morning'),
                Tag.objects.create(name="Обед", slug='lunch'),
                Tag.objects.create(name="Ужин", slug='evening'),
            ]
            print(f"Создано тегов: {Tag.objects.count()}")
        except Exception as e:
            print('ТЕГИ.', e)

        try:
            # Создание тестовых ингредиентов с measurement_unit
            ingredients = [
                {"name": "Картофель", "measurement_unit": "кг"},
                {"name": "Морковь", "measurement_unit": "шт"},
                {"name": "Сыр", "measurement_unit": "г"},
            ]

            # Создаем объекты ингредиентов
            ingredient_objects = [
                Ingredient(**ingredient) for ingredient in ingredients
            ]
            Ingredient.objects.bulk_create(ingredient_objects)
            print(f"Создано ингредиентов: {Ingredient.objects.count()}")
        except Exception as e:
            print('ИНГРЕДИЕНТЫ. ', e)

        try:
            # Создание тестовых рецептов
            recipes = [
                {
                    "author": user_objects[0],
                    "name": "Омлет с сыром",
                    "image": "path/to/omelet.jpg",
                    "text": "Простой и вкусный омлет с сыром.",
                    "ingredients": [("Сыр", 100)],
                    "tags": [tags[0]],
                    "cooking_time": 15,
                },
                {
                    "author": user_objects[1],
                    "name": "Картофельное пюре",
                    "image": "path/to/mashed_potatoes.jpg",
                    "text": "Идеальное картофельное пюре.",
                    "ingredients": [("Картофель", 500)],
                    "tags": [tags[1]],
                    "cooking_time": 10,
                },
                {
                    "author": user_objects[2],
                    "name": "Суп из моркови",
                    "image": "path/to/carrot_soup.jpg",
                    "text": "Полезный суп из моркови.",
                    "ingredients": [("Морковь", 300)],
                    "tags": [tags[2]],
                    "cooking_time": 5,
                },
            ]

            for recipe_data in recipes:
                tags_for_recipe = recipe_data.pop("tags")
                ingredients_data = recipe_data.pop("ingredients")

                recipe = Recipe.objects.create(**recipe_data)

                # Связываем ингредиенты с рецептом через промежуточную модель
                for ingredient_name, amount in ingredients_data:
                    ingredient = Ingredient.objects.get(name=ingredient_name)

                    IngredientRecipe.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=amount
                    )

                recipe.tags.set(tags_for_recipe)

            print(f"Создано рецептов: {Recipe.objects.count()}")
        except Exception as e:
            print('РЕЦЕПТЫ. ', e)

        users = User.objects.all()
        for user1 in users:
            for user2 in users:
                if user1 != user2:
                    try:
                        Subscribe.objects.create(
                            subscriber=user1,
                            author=user2
                        )
                    except Exception as e:
                        print('ОШИБКА ПОДПИСОК', e)
        print(f"Создано подписок: {Subscribe.objects.count()}")

        try:
            user_objects = User.objects.all()

            ShoppingList.objects.create(
                user=user_objects[0]).recipes.add(
                    Recipe.objects.get(name="Омлет с сыром")
            ),
            ShoppingList.objects.create(
                user=user_objects[1]).recipes.add(
                    Recipe.objects.get(name="Картофельное пюре")
            ),
            ShoppingList.objects.create(
                user=user_objects[2]).recipes.add(
                    Recipe.objects.get(name="Суп из моркови")
            ),

            print(f"Создано списков покупок: {ShoppingList.objects.count()}")

        except Exception as e:
            print('Не удалось ', e)
        try:
            user_objects = User.objects.all()
            favorite_recipe_1 = FavoriteRecipes.objects.create(
                user=user_objects[0]
            )
            favorite_recipe_2 = FavoriteRecipes.objects.create(
                user=user_objects[1]
            )
            favorite_recipe_3 = FavoriteRecipes.objects.create(
                user=user_objects[2]
            )

            favorite_recipe_1.recipes.add(
                Recipe.objects.get(name="Картофельное пюре")
            )
            favorite_recipe_2.recipes.add(
                Recipe.objects.get(name="Суп из моркови")
            )
            favorite_recipe_3.recipes.add(
                Recipe.objects.get(name="Омлет с сыром")
            )
            print(
                "Создано избранных рецептов: ",
                f"{FavoriteRecipes.objects.count()}",
            )

        except Exception as e:
            print('Не удалось ', e)

        self.stdout.write(self.style.SUCCESS(
            'Тестовые данные для всех приложений успешно добавлены!'
        ))
