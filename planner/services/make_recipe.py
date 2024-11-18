import json
from pathlib import Path
from recipe_generator import generate_recipe

dish_idea = "Simple Shoryu Ramen"
notes = "Make it easy to cook"
dietary_preferences = None
servings = 4
units = "metric"

recipe = generate_recipe(dish_idea, notes, dietary_preferences, servings, units)


recipes_dir = Path("planner/static/planner/recipes")
recipe_name = recipe.recipe_name.lower().replace(" ", "_").replace("'", "")
filename = recipe_name + ".json"
file_path = recipes_dir / filename

# Save recipe to JSON file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(recipe.model_dump(), f, indent=2, ensure_ascii=False)

print(f"Recipe saved to: {file_path}")