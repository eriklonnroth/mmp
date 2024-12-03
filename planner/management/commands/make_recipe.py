from django.core.management.base import BaseCommand
from planner.services.recipe_generator import generate_recipe
from planner.services.recipe_parser import parse_recipe_string
from planner.services.recipe_repository import save_recipe_to_db
from planner.services.recipe_to_file import save_recipe_to_file

class Command(BaseCommand):
    help = 'Generates a recipe using OpenAI and saves it to database and/or file.'

    def add_arguments(self, parser):
        parser.add_argument('dish_idea', type=str, help='Description of the dish')
        parser.add_argument('--notes', type=str, default='', help='Additional notes or requirements')
        parser.add_argument('--preferences', type=str, default='', help='Dietary preferences')
        parser.add_argument('--servings', type=int, default=4, help='Number of servings')
        parser.add_argument('--units', type=str, default='metric', choices=['metric', 'imperial'], 
                          help='Measurement units to use')
        parser.add_argument('--db', action='store_true', help='Save recipe to database')
        parser.add_argument('--file', action='store_true', help='Save recipe as JSON to static files')


    def handle(self, *args, **options):
        recipe_str = generate_recipe(
            dish_idea=options['dish_idea'],
            notes=options['notes'],
            dietary_preferences=options['preferences'],
            servings=options['servings'],
            units=options['units']
        )

        parsed_recipe = parse_recipe_string(recipe_str)
        
        # Print the generated dish name
        self.stdout.write(self.style.SUCCESS(f"Generated recipe: {parsed_recipe.dish_name}"))
        
        # Save to database if requested
        if options['db']:                               
            db_recipe = save_recipe_to_db(parsed_recipe, status='published')
            self.stdout.write(self.style.SUCCESS(
                f"Saved recipe to database with ID: {db_recipe.id}"
            ))              


        # Save to file if requested
        if options['file']:                            
            file_path = save_recipe_to_file(parsed_recipe)
            self.stdout.write(self.style.SUCCESS(
                f"Saved recipe to file at {file_path}"
            ))                    