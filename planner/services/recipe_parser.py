from typing import Dict, Any, List
import json
from pathlib import Path
from pydantic import BaseModel, ValidationError

from planner.models import Recipe as DBRecipe
from planner.models import Ingredient as DBIngredient
from planner.models import InstructionSection as DBInstructionSection
from planner.models import InstructionStep as DBInstructionStep

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
        try:
            # Validate ingredients first
            validated_ingredients = self.validate_ingredients()
            
            # Then validate instruction sections and their steps
            validated_instructions = self.validate_instructions()
            
            # Finally, create the complete recipe with validated components
            return Recipe(
                recipe_name=self.recipe_data['recipe_name'],
                servings=self.recipe_data['servings'],
                description=self.recipe_data['description'],
                ingredients=validated_ingredients,
                instructions=validated_instructions
            )
        except ValidationError as e:
            raise ValueError(f"Invalid recipe format: {e}")

    def save_to_db(self, user) -> DBRecipe:
        """Save validated recipe to database"""
        # Validate everything before saving anything
        validated_recipe = self.validate()

        # Create the recipe
        recipe = DBRecipe.objects.create(
            name=validated_recipe.recipe_name,
            servings=validated_recipe.servings,
            description=validated_recipe.description,
            created_by=user,
            notes=""  # Optional field
        )

        # Create ingredients with order
        for i, ing in enumerate(validated_recipe.ingredients, 1):
            DBIngredient.objects.create(
                recipe=recipe,
                item=ing.item,
                quantity=ing.quantity,
                order=i
            )

        # Create instruction sections and steps
        for section_data in self.recipe_data.get('instructions', []):
            db_section = DBInstructionSection.objects.create(
                recipe=recipe,
                title=section_data['section_title'],
                order=section_data.get('section_order', 1)  # Get order from JSON
            )
            
            # Create steps for this section
            for i, step in enumerate(section_data['steps'], 1):
                DBInstructionStep.objects.create(
                    section=db_section,
                    text=step['instruction'],  # Changed from instruction to text
                    order=i
                )

        # Update ingredients digest
        recipe.update_ingredients_digest()
        
        return recipe

def parse_recipe_file(file_path: str | Path, user) -> DBRecipe:
    """Convenience function to parse and save a recipe file"""
    parser = RecipeParser.from_json_file(file_path)
    return parser.save_to_db(user)

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
