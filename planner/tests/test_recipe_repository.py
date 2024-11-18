import pytest
from django.contrib.auth.models import User
from django.conf import settings
from pathlib import Path
from planner.services.recipe_parser import RecipeParser, parse_recipe_file, parse_recipe_string
from planner.services.recipe_repository import RecipeRepository, save_recipe_to_db

pytestmark = pytest.mark.django_db

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_mmp',
        'USER': 'admin',  # superuser
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'SERIALIZE': False  # Optional: can speed up tests
        }
    }

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def recipe_path():
    def _get_recipe_path(recipe_file: str) -> Path:
        return Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / recipe_file
    return _get_recipe_path

class TestRecipeRepository:
    def test_save_recipe_to_db(self, recipe_path, user):
        # First parse the recipe
        recipe = parse_recipe_file(recipe_path('lasagna.json'))
        
        # Then save it to DB
        db_recipe = save_recipe_to_db(recipe, user)
        
        # Test basic info was saved correctly
        assert db_recipe.name == recipe.recipe_name
        assert db_recipe.servings == recipe.servings
        assert db_recipe.description == recipe.description
        assert db_recipe.created_by == user
        
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
        assert "bake for an additional 10-15 minutes" in steps.get(order=3).step