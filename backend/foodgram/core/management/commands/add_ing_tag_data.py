import json

from django.core.management.base import BaseCommand

from recipe.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Load ingredients data from JSON file"

    def handle(self, *args, **kwargs):
        with open("data/ingredients.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        ingredients = [
            Ingredient(
                name=item["name"],
                measurement_unit=item["measurement_unit"]
            )
            for item in data
        ]

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)

        Tag.objects.create(name="Завтрак", slug='morning')
        Tag.objects.create(name="Обед", slug='lunch')
        Tag.objects.create(name="Ужин", slug='evening')
        print(f"Создано тегов: {Tag.objects.count()}")
        self.stdout.write(self.style.SUCCESS("Ингредиенты успешно загружены."))
