from typing import Dict, Any
import json
from pathlib import Path
from pydantic import BaseModel, ValidationError

from planner.models import Recipe as DBRecipe
from planner.models import Ingredient as DBIngredient
from planner.models import InstructionSection as DBInstructionSection
from planner.models import InstructionStep as DBInstructionStep

# Use the same Pydantic models from recipe_generator for validation
from .recipe_generator import Recipe, Ingredient, InstructionSection, InstructionStep

class RecipeParser:
    def __init__(self, recipe_data: Dict[str, Any]):
        self.recipe_data = recipe_data
        
    @classmethod
    def from_json_file(cls, file_path: str | Path):
        """Create parser instance from a JSON file"""
        with open(file_path, 'r') as f:
            recipe_data = json.load(f)
        return cls(recipe_data)

    def validate(self) -> Recipe:
        """Validate recipe data against Pydantic models"""
        try:
            return Recipe(**self.recipe_data)
        except ValidationError as e:
            raise ValueError(f"Invalid recipe format: {e}")

    def save_to_db(self) -> DBRecipe:
        """Save validated recipe to database"""
        # First validate the data
        validated_recipe = self.validate()

        # Create the recipe
        recipe = DBRecipe.objects.create(
            name=validated_recipe.recipe_name,
            servings=validated_recipe.servings,
            description=validated_recipe.description
        )

        # Create ingredients
        for ing in validated_recipe.ingredients:
            DBIngredient.objects.create(
                recipe=recipe,
                item=ing.item,
                quantity=ing.quantity
            )

        # Create instruction sections and steps
        for section in validated_recipe.instructions:
            db_section = DBInstructionSection.objects.create(
                recipe=recipe,
                title=section.section_title
            )
            
            # Create steps for this section
            for i, step in enumerate(section.steps, 1):
                DBInstructionStep.objects.create(
                    section=db_section,
                    step_number=i,
                    instruction=step.step
                )

        return recipe

def parse_recipe_file(file_path: str | Path) -> DBRecipe:
    """Convenience function to parse and save a recipe file"""
    parser = RecipeParser.from_json_file(file_path)
    return parser.save_to_db()

def parse_recipe_directory(directory: str | Path) -> list[DBRecipe]:
    """Parse all JSON recipe files in a directory"""
    directory = Path(directory)
    recipes = []
    
    for recipe_file in directory.glob('*.json'):
        try:
            recipe = parse_recipe_file(recipe_file)
            recipes.append(recipe)
        except Exception as e:
            print(f"Error parsing {recipe_file}: {e}")
            continue
            
    return recipes
