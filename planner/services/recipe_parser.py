from typing import Dict, Any, List
import json
from pathlib import Path
from pydantic import ValidationError
from .recipe_generator import Recipe, Ingredient, InstructionSection, InstructionStep

class RecipeParser:
    def __init__(self, recipe_data: Dict[str, Any]):
        self.recipe_data = recipe_data
        
    @classmethod
    def from_file(cls, file_path: str | Path):
        """Create parser instance from a JSON file"""
        with open(file_path, 'r') as f:
            recipe_data = json.load(f)
        return cls(recipe_data)

    def validate_ingredients(self) -> List[Ingredient]:
        """Validate ingredients data"""
        ingredients = []
        for ing_data in self.recipe_data.get('ingredients', []):
            try:
                ingredient = Ingredient(**ing_data)
                ingredients.append(ingredient)
            except ValidationError as e:
                raise ValueError(f"Invalid ingredient format: {ing_data}\nError: {e}")
        return ingredients

    def validate_instruction_steps(self, steps_data: List[Dict]) -> List[InstructionStep]:
        """Validate instruction steps data"""
        steps = []
        for step_data in steps_data:
            try:
                step = InstructionStep(**step_data)
                steps.append(step)
            except ValidationError as e:
                raise ValueError(f"Invalid step format: {step_data}\nError: {e}")
        return steps

    def validate_instructions(self) -> List[InstructionSection]:
        """Validate instruction sections data"""
        sections = []
        
        for section_data in self.recipe_data.get('instructions', []):
            try:
                # Validate steps first
                validated_steps = self.validate_instruction_steps(section_data.get('steps', []))
                # Then create section with validated steps
                section = InstructionSection(
                    section_title=section_data['section_title'],
                    steps=validated_steps
                )
                sections.append(section)
            except ValidationError as e:
                raise ValueError(f"Invalid section format: {section_data}\nError: {e}")
        return sections

    def validate(self) -> Recipe:
        """Validate entire recipe data"""
        # Check for required fields first
        required_fields = ['dish_name', 'servings', 'description', 'ingredients', 'instructions']
        missing_fields = [field for field in required_fields if field not in self.recipe_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            # Validate ingredients first
            validated_ingredients = self.validate_ingredients()
            
            # Then validate instruction sections and their steps
            validated_instructions = self.validate_instructions()
            
            # Finally, create the complete recipe with validated components
            return Recipe(
                dish_name=self.recipe_data['dish_name'],
                servings=self.recipe_data['servings'],
                description=self.recipe_data['description'],
                ingredients=validated_ingredients,
                instructions=validated_instructions
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")

# Helper functions
def parse_recipe_file(file_path: str | Path) -> Recipe:
    """Parse a recipe from a JSON file"""
    parser = RecipeParser.from_file(file_path)
    return parser.validate()

def parse_recipe_string(json_str: str) -> Recipe:
    """Parse a recipe from a JSON string"""
    recipe_data = json.loads(json_str)
    parser = RecipeParser(recipe_data)
    return parser.validate()
