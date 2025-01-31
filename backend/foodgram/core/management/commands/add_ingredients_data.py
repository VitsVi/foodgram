import json
from recipe.models import Ingredient

with open("data/ingredients.json", "r", encoding="utf-8") as file:
    data = json.load(file)

ingredients = [
    Ingredient(name=item["name"],
    measurement_unit=item["measurement_unit"]) for item in data
]

Ingredient.objects.bulk_create(ingredients)

print("Загрузка завершена!")
