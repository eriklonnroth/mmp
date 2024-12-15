from django.contrib.auth.models import User
from planner.models import Recipe as DBRecipe
from planner.models import Ingredient as DBIngredient
from planner.models import InstructionSection as DBInstructionSection
from planner.models import InstructionStep as DBInstructionStep
from .recipe_generator import Recipe

class RecipeRepository:
    @staticmethod
    def save_recipe(recipe: Recipe, user=None, status='published') -> DBRecipe:
        """Save Recipe object to database"""
        # Create the recipe
        db_recipe = DBRecipe.objects.create(
            status=status,
            title=recipe.title,
            servings=recipe.servings,
            description=recipe.description,
            created_by=user,
        )

        # Create ingredients with order
        for i, ing in enumerate(recipe.ingredients, 1):
            DBIngredient.objects.create(
                recipe=db_recipe,
                name=ing.name,
                quantity=ing.quantity,
                order=i
            )

        # Create instruction sections
        for i, section in enumerate(recipe.instructions, 1):
            db_section = DBInstructionSection.objects.create(
                recipe=db_recipe,
                title=section.section_title,
                order=i
            )
            
            # Create steps for this section
            for j, step in enumerate(section.steps, 1):
                DBInstructionStep.objects.create(
                    section=db_section,
                    text=step.text,
                    order=j
                )

        # Update ingredients digest
        db_recipe.update_ingredients_digest()
        
        return db_recipe

# Helper function
def save_recipe_to_db(recipe: Recipe, user=None, status='published') -> DBRecipe:
    service = RecipeRepository()
    return service.save_recipe(recipe, user, status)