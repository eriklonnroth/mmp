from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from planner.services.recipe_parser import parse_recipe_file
from planner.services.recipe_repository import save_recipe_to_db
from pathlib import Path
from planner.models import Recipe

class Command(BaseCommand):
    help = 'Saves all static recipes to the database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = color_style()

    def get_recipe_dir(self) -> Path:
        return Path(__file__).parent.parent.parent / 'static' / 'planner' / 'recipes'

    def handle(self, *args, **options):
        recipe_dir = self.get_recipe_dir()
        
        # Get all .json files in the recipes directory
        recipe_files = recipe_dir.glob('*.json')
        
        for recipe_file in recipe_files:
            # Skip spoonacular files for now as they have a different format
            if recipe_file.name.startswith('spoonacular_'):
                self.stdout.write(f"Skipping spoonacular recipe: {recipe_file.name}")
                continue
            
            recipe = parse_recipe_file(recipe_file)
            
            # Check if recipe already exists
            if Recipe.objects.filter(title=recipe.title).exists():
                self.stdout.write(f"Skipping existing recipe: {recipe.title}")
                continue
            
            save_recipe_to_db(recipe, status='published')
            self.stdout.write(
                self.style.SUCCESS(f"Successfully saved recipe: {recipe_file.name}")
            )
