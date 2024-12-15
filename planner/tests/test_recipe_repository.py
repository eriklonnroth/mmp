import pytest
from django.contrib.auth.models import User
from pathlib import Path
from planner.services.recipe_parser import parse_recipe_file
from planner.services.recipe_repository import save_recipe_to_db

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def recipe_path():
    def _get_recipe_path(recipe_file: str) -> Path:
        return Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / recipe_file
    return _get_recipe_path

class TestRecipeRepository:
    def test_save_recipe_to_db(self, recipe_path, user, status='draft'):
        # First parse the recipe
        recipe = parse_recipe_file(recipe_path('classic_beef_lasagna.json'))
        
        # Then save it to DB
        db_recipe = save_recipe_to_db(recipe, user, status)
        
        # Test basic info was saved correctly
        assert db_recipe.title == recipe.title
        assert db_recipe.servings == recipe.servings
        assert db_recipe.description == recipe.description
        assert db_recipe.created_by == user
        assert db_recipe.status == status

        # Test ingredients were saved
        ingredients = db_recipe.ingredients.all()
        assert len(ingredients) == len(recipe.ingredients)
        assert ingredients.first().item == recipe.ingredients[0].item
        
        # Test instruction sections were saved
        sections = db_recipe.instruction_sections.all()
        assert len(sections) == len(recipe.instructions)
        
        # Test steps were saved
        bake_section = sections.get(title="Bake")
        steps = bake_section.steps.all()
        assert len(steps) == 4
        assert "bake for an additional 10-15 minutes" in steps.get(order=3).text

        # Test the inherited status is the same as the recipe status
        assert steps.get(order=3).section.recipe.status == status
