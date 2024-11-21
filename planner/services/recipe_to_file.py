import json
from unidecode import unidecode
from pathlib import Path
from .recipe_parser import parse_recipe_string, Recipe


def save_recipe_to_file(recipe: Recipe):
    recipes_dir = Path("planner/static/planner/recipes")
    filename = unidecode(recipe.dish_name).lower().replace(" ", "_").replace("'", "").replace('&', 'and') + ".json"
    file_path = recipes_dir / filename

    try:
        # Save recipe to JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(recipe.model_dump(), f, indent=2, ensure_ascii=False)
            return file_path
    except IOError as e:
        raise IOError(f"Error saving recipe to file: {str(e)}")