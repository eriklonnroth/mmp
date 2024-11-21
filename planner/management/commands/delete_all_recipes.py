from django.db import connection
from planner.models import Recipe, InstructionSection, Ingredient, InstructionStep

def clear_all_recipe_data():
    # Delete all recipes (this should cascade to related models if set up properly)
    Recipe.objects.all().delete()
    
    # Reset the sequences for all related tables
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE planner_recipe_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE planner_instructionsection_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE planner_ingredient_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE planner_instructionstep_id_seq RESTART WITH 1")

# Run the cleanup
clear_all_recipe_data()

# Verify the results
recipes = Recipe.objects.all()
instruction_sections = InstructionSection.objects.all()
ingredients = Ingredient.objects.all()
instruction_steps = InstructionStep.objects.all()
print("Recipes:", recipes.count())
print("Instruction Sections:", instruction_sections.count())
print("Ingredients:", ingredients.count())
print("Instruction Steps:", instruction_steps.count())