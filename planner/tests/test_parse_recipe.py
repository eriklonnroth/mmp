import pytest
from django.contrib.auth.models import User
from django.conf import settings
from pathlib import Path
from planner.services.recipe_parser import RecipeParser, parse_recipe_file, parse_recipe_string
from planner.services.recipe_repository import RecipeRepository, save_recipe_to_db

@pytest.fixture
def recipe_path():
    def _get_recipe_path(recipe_file: str) -> Path:
        return Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / recipe_file
    return _get_recipe_path

class TestRecipeParser:
    def test_parse_basic_info(self, recipe_path):
        recipe = parse_recipe_file(recipe_path('lasagna.json'))
        assert recipe.recipe_name == "Gluten-Free Beef Lasagna"
        assert recipe.servings == 3
        assert "delicious and hearty gluten-free beef lasagna" in recipe.description

    def test_parse_ingredients(self, recipe_path):
        recipe = parse_recipe_file(recipe_path('lasagna.json'))
        
        assert len(recipe.ingredients) == 14
        
        # Test first ingredient
        beef = recipe.ingredients[0]
        assert beef.item == "Ground beef"
        assert beef.quantity == "1 pound"
        
        # Test last ingredient
        seasoning = recipe.ingredients[-1]
        assert seasoning.item == "Italian seasoning"

    def test_parse_instructions(self, recipe_path):
        recipe = parse_recipe_file(recipe_path('lasagna.json'))
        
        assert len(recipe.instructions) == 4
        
        # Test section titles
        section_titles = [section.section_title for section in recipe.instructions]
        assert section_titles == ["Prepare the Meat Sauce", "Prepare the Cheese Mixture", 
                                "Assemble the Lasagna", "Bake"]
        
        # Test steps in baking section
        bake_section = recipe.instructions[3]  # Last section
        assert len(bake_section.steps) == 4
        assert "bake for an additional 10-15 minutes" in bake_section.steps[2].step
        assert "Allow the lasagna to rest" in bake_section.steps[-1].step

    def test_validation_errors(self):
        # Test missing required fields first
        missing_fields_data = {
            "recipe_name": "Bad Recipe",
            "servings": 4,
            # Missing required fields: description, ingredients, instructions
        }
        
        with pytest.raises(ValueError) as exc_info:
            parser = RecipeParser(missing_fields_data)
            parser.validate()
        assert "Missing required fields: description, ingredients, instructions" in str(exc_info.value)
        
        # Test invalid ingredient format
        bad_ingredients_data = {
            "recipe_name": "Bad Recipe",
            "servings": 4,
            "description": "A test recipe",
            "ingredients": [
                {"quantity": "1 cup"}  # Missing 'item' field
            ],
            "instructions": []
        }
        
        with pytest.raises(ValueError) as exc_info:
            parser = RecipeParser(bad_ingredients_data)
            parser.validate()
        assert "Invalid ingredient format" in str(exc_info.value)
        
        # Test invalid instruction format
        bad_instructions_data = {
            "recipe_name": "Bad Recipe",
            "servings": 4,
            "description": "A test recipe",
            "ingredients": [
                {"item": "test", "quantity": "1 cup"}
            ],
            "instructions": [
                {"steps": []}  # Missing 'section_title'
            ]
        }
        
        with pytest.raises(ValueError) as exc_info:
            parser = RecipeParser(bad_instructions_data)
            parser.validate()
        assert "Missing required field: 'section_title'" in str(exc_info.value)