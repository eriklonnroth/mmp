import pytest
from django.contrib.auth.models import User
from pathlib import Path
from planner.services.recipe_parser import parse_recipe_file, RecipeParser

# Mark all tests to allow database access
pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def recipe_path():
    return Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / 'korma.json'

def test_recipe_basic_info(recipe_path, user):
    recipe = parse_recipe_file(recipe_path, user)
    assert recipe.name == "Chicken Korma"
    assert recipe.servings == 3
    assert "creamy and aromatic Indian dish" in recipe.description
    assert recipe.created_by == user
    assert recipe.notes == ""
    assert recipe.ingredients_digest != ""

def test_recipe_ingredients(recipe_path, user):
    recipe = parse_recipe_file(recipe_path, user)
    ingredients = recipe.ingredients.all()
    
    assert len(ingredients) == 15
    
    # Test first ingredient
    chicken = ingredients.get(order=1)
    assert chicken.item == "Chicken breast"
    assert chicken.quantity == "500g, diced"
    
    # Test ingredient ordering
    ingredient_items = [ing.item for ing in ingredients.order_by('order')]
    assert ingredient_items[0] == "Chicken breast"
    assert ingredient_items[-1] == "Fresh coriander leaves"

def test_recipe_instructions(recipe_path, user):
    recipe = parse_recipe_file(recipe_path, user)
    sections = recipe.instruction_sections.all()
    
    assert len(sections) == 3
    
    # Test section ordering
    section_titles = [section.title for section in sections.order_by('order')]
    assert section_titles == ["Preparation", "Cooking", "Serving"]
    
    # Test section orders from JSON
    prep_section = sections.get(title="Preparation")
    assert prep_section.order == 1
    
    cooking_section = sections.get(title="Cooking")
    assert cooking_section.order == 2
    
    # Test steps in cooking section
    steps = cooking_section.steps.all().order_by('order')
    assert len(steps) == 6
    
    # Test first step content
    first_step = steps.first()
    assert "Heat the vegetable oil" in first_step.text
    assert first_step.order == 1

def test_recipe_validation_errors():
    # Test with invalid recipe data
    bad_recipe_data = {
        "recipe_name": "Bad Recipe",
        "servings": "not a number",  # Should be int
        "ingredients": [{"bad_field": "value"}]  # Missing required fields
    }
    
    with pytest.raises(ValueError) as exc_info:
        parser = RecipeParser(bad_recipe_data)
        parser.validate()
    
    assert "Invalid recipe format" in str(exc_info.value)