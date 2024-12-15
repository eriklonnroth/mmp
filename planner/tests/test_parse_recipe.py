import pytest
from django.contrib.auth.models import User
from pathlib import Path
from planner.services.recipe_parser import RecipeParser, parse_recipe_file, parse_recipe_string
import json

@pytest.fixture
def recipe_path():
    def _get_recipe_path(recipe_file: str) -> Path:
        return Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / recipe_file
    return _get_recipe_path

class TestRecipeParser:
    def test_parse_basic_info(self, recipe_path):
        recipe = parse_recipe_file(recipe_path('classic_beef_lasagna.json'))
        assert recipe.title == "Classic Beef Lasagna"
        assert recipe.servings == 3
        assert "delicious and hearty beef lasagna" in recipe.description

    def test_parse_ingredients(self, recipe_path):
        recipe = parse_recipe_file(recipe_path('classic_beef_lasagna.json'))
        
        assert len(recipe.ingredients) == 14
        
        # Test first ingredient
        beef = recipe.ingredients[0]
        assert beef.item == "Ground beef"
        assert beef.quantity == "1 pound"
        
        # Test last ingredient
        seasoning = recipe.ingredients[-1]
        assert seasoning.item == "Italian seasoning"

    def test_parse_instructions(self, recipe_path):
        recipe = parse_recipe_file(recipe_path('classic_beef_lasagna.json'))
        
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
            "title": "Bad Recipe",
            "servings": 4,
            # Missing required fields: description, ingredients, instructions
        }
        
        with pytest.raises(ValueError) as exc_info:
            parser = RecipeParser(missing_fields_data)
            parser.validate()
        assert "Missing required fields: description, ingredients, instructions" in str(exc_info.value)
        
        # Test invalid ingredient format
        bad_ingredients_data = {
            "title": "Bad Recipe",
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
            "title": "Bad Recipe",
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


    def test_parse_from_string(self, recipe_path):
        with open(recipe_path('classic_beef_lasagna.json'), 'r') as f:
            json_str = f.read()
        recipe_from_string = parse_recipe_string(json_str)
        assert recipe_from_string.title == "Classic Beef Lasagna"
        assert len(recipe_from_string.instructions) == 4
        assert "Return to the oven" in recipe_from_string.instructions[3].steps[2].text
        
    def test_json_decode_errors(self):
        # Test invalid JSON syntax (missing quotes around string)
        invalid_syntax = '''{
            title: "Test Recipe",
            "servings": 4
        }'''
        with pytest.raises(json.JSONDecodeError, match="Expecting property name enclosed in double quotes"):
            parse_recipe_string(invalid_syntax)
            
        # Test unclosed brackets
        unclosed_brackets = '''{
            "title": "Test Recipe",
            "servings": 4,
            "ingredients": [
                {"item": "test", "quantity": "1 cup"
        }'''
        with pytest.raises(json.JSONDecodeError, match="Expecting ',' delimiter"):
            parse_recipe_string(unclosed_brackets)
            
        # Test trailing comma
        trailing_comma = '''{
            "title": "Test Recipe",
            "servings": 4,
            "ingredients": [],
        }'''
        with pytest.raises(json.JSONDecodeError, match="Illegal trailing comma"):
            parse_recipe_string(trailing_comma)
            
        # Test single quotes instead of double quotes
        single_quotes = "{'title': 'Test Recipe'}"
        with pytest.raises(json.JSONDecodeError, match="Expecting property name enclosed in double quotes"):
            parse_recipe_string(single_quotes)