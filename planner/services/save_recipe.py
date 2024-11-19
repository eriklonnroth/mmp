from recipe_parser import parse_recipe_file
from recipe_repository import save_recipe_to_db
from django.contrib.auth.models import User
from pathlib import Path

admin_user = User.objects.get(username='admin')

def recipe_path():
    def _get_recipe_path(recipe_file: str) -> Path:
        return Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / recipe_file
    return _get_recipe_path

recipe = parse_recipe_file(recipe_path('classic_beef_lasagna.json'))
save_recipe_to_db(recipe, admin_user)