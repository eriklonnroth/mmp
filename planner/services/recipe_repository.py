from django.contrib.auth.models import User
from planner.models import Recipe as DBRecipe
from planner.models import Ingredient as DBIngredient
from planner.models import InstructionSection as DBInstructionSection
from planner.models import InstructionStep as DBInstructionStep
from .recipe_generator import Recipe

class RecipeRepository:
    @staticmethod
    def admin_user():
        return User.objects.get(username='admin')

    @staticmethod
    def save_recipe(recipe: Recipe, user=admin_user) -> DBRecipe:
        """Save Recipe object to database"""
        # Create the recipe
        db_recipe = DBRecipe.objects.create(
            dish_name=recipe.dish_name,
            servings=recipe.servings,
            description=recipe.description,
            created_by=user,
        )

        # Create ingredients with order
        for i, ing in enumerate(recipe.ingredients, 1):
            DBIngredient.objects.create(
                recipe=db_recipe,
                item=ing.item,
                quantity=ing.quantity,
                order=i
            )

        # Create instruction sections and steps
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
                    step=step.step,
                    order=j
                )

        # Update ingredients digest
        db_recipe.update_ingredients_digest()
        
        return db_recipe

# Helper functions
def save_recipe_to_db(recipe: Recipe, user=RecipeRepository.admin_user) -> DBRecipe:
    """Helper function to save a Recipe to the database"""
    service = RecipeRepository()
    return service.save_recipe(recipe, user)