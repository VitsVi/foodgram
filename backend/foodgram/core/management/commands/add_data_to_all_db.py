from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipe.models import (
    Ingredient,
    Recipe,
    Tag,
)
from core.models import (
    Subscribe,
)
from add_by_user.models import (
    ShoppingList,
    FavoriteRecipes
)

AVATAR = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="


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
                    #"avatar": AVATAR,
                    "first_name": "username_1",
                    "last_name": "last_username_1",
                },
                {
                    "username": "chef2",
                    "email": "chef2@example.com",
                    "password": "password123",
                    #"avatar": AVATAR,
                    "first_name": "username_2",
                    "last_name": "last_username_2",
                },        {
                    "username": "chef3",
                    "email": "chef3@example.com",
                    "password": "password123",
                    #"avatar": AVATAR,
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
                Tag.objects.create(name="Завтрак",slug='morning'),
                Tag.objects.create(name="Обед",slug='lunch'),
                Tag.objects.create(name="Ужин",slug='evening'),
            ]
            print(f"Создано тегов: {Tag.objects.count()}")
        except Exception as e:
            print('ТЕГИ.', e)
        
        try:
            # Создание тестовых ингредиентов
            ingredients = [
                {"name": "Картофель", "measurement_unit": "кг"},
                {"name": "Морковь", "measurement_unit": "шт"},
                {"name": "Сыр", "measurement_unit": "г"},
            ]
            ingredient_objects = [Ingredient(**ingredient) for ingredient in ingredients]
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
                    "ingredients": Ingredient.objects.get(name="Сыр"),
                    "tags": [tags[0]],
                    "cooking_time": 15,
                },
                {
                    "author": user_objects[1],
                    "name": "Картофельное пюре",
                    "image": "path/to/mashed_potatoes.jpg",
                    "text": "Идеальное картофельное пюре.",
                    "ingredients": Ingredient.objects.get(name="Картофель"),
                    "tags": [tags[1]],
                    "cooking_time": 10,
                },
                {
                    "author": user_objects[2],
                    "name": "Суп из моркови",
                    "image": "path/to/carrot_soup.jpg",
                    "text": "Полезный суп из моркови.",
                    "ingredients": Ingredient.objects.get(name="Морковь"),
                    "tags": [tags[2]],
                    "cooking_time": 5,
                },
            ]
            for recipe_data in recipes:
                tags_for_recipe = recipe_data.pop("tags")
                recipe = Recipe.objects.create(**recipe_data)
                recipe.tags.set(tags_for_recipe)
            print(f"Создано рецептов: {Recipe.objects.count()}")
        except Exception as e:
            print('РЕЦЕПТЫ. ', e)


        users = User.objects.all()
        for user1 in users:
            for user2 in users:
                if user1 != user2:
                    try:
                        Subscribe.objects.create(subscriber=user1, author=user2)
                    except Exception as e:
                        print('ОШИБКА ПОДПИСОК', e)
        print(f"Создано подписок: {Subscribe.objects.count()}")


        try:
            user_objects = User.objects.all()
            shopping_lists = [
                ShoppingList.objects.create(user=user_objects[0]),
                ShoppingList.objects.create(user=user_objects[1]),
                ShoppingList.objects.create(user=user_objects[2]),
            ]
            shopping_lists[0].recipes.add(Recipe.objects.get(name="Омлет с сыром"))
            shopping_lists[1].recipes.add(Recipe.objects.get(name="Картофельное пюре"))
            shopping_lists[2].recipes.add(Recipe.objects.get(name="Суп из моркови"))
            print(f"Создано списков покупок: {ShoppingList.objects.count()}")

            # Создание избранных рецептов
            favorite_recipes = [
                FavoriteRecipes.objects.create(user=user_objects[0]),
                FavoriteRecipes.objects.create(user=user_objects[1]),
                FavoriteRecipes.objects.create(user=user_objects[2]),
            ]
            favorite_recipes[0].recipes.add(Recipe.objects.get(name="Картофельное пюре"))
            favorite_recipes[1].recipes.add(Recipe.objects.get(name="Суп из моркови"))
            favorite_recipes[2].recipes.add(Recipe.objects.get(name="Омлет с сыром"))
            print(f"Создано избранных рецептов: {FavoriteRecipes.objects.count()}")
        
        except Exception as e:
            print('Не удалось ', e)



        self.stdout.write(self.style.SUCCESS(
            'Тестовые данные для всех приложений успешно добавлены!'
        ))