from openai import OpenAI
from pydantic import BaseModel, field_validator
from typing import ClassVar
import os
import argparse
import json
import glob
from planner.models import ShoppingCategory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Base models (maps to JSON response and models.py)
class Category(str):
    valid_categories: ClassVar[list[tuple[str, str]]] = ShoppingCategory.CATEGORIES

    @classmethod
    def categories_list(cls) -> list[str]:
        return [cat[0] for cat in cls.valid_categories]

    @classmethod
    def validate(cls, v):
        if v not in cls.categories_list():
            raise ValueError(f'Category must be one of: {cls.categories_list()}')
        return v
        
    @classmethod
    def __get_validators__(cls): # Pydantic method
        yield cls.validate
        

from pydantic import BaseModel, field_validator

class ShoppingItem(BaseModel):
    item: str
    quantity: str
    recipe_notes: str
    category: str

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [cat[1] for cat in ShoppingCategory.CATEGORIES] # Full category name, e.g. Fruit & Vegetables (not fruit_veg)
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v


class ShoppingList(BaseModel):
    shopping_list: list[ShoppingItem]

# Load recipes from static directory
def load_recipes():
    recipe_dir = "planner/static/planner/recipes"
    recipe_files = glob.glob(os.path.join(recipe_dir, "*.json"))
    
    recipes = []
    for recipe_file in recipe_files:
        with open(recipe_file, 'r') as f:
            recipe = json.load(f)
            # Strip away unnecessary fields from recipe
            stripped_recipe = {
                "dish_name": recipe["dish_name"],
                "servings": recipe["servings"],
                "description": recipe["description"],
                "ingredients": recipe["ingredients"]
            }
            recipes.append(stripped_recipe)
    return recipes

# OpenAI API function
def generate_shopping_list(recipe_files: list[str], preferred_units: str = "metric") -> ShoppingList:
    """
    Generates a shopping list in JSON format. See https://platform.openai.com/docs/guides/structured-outputs
    """
    recipes = load_recipes()
        
    user_input = f"""
    Make me a JSON shopping list using shopping-appropriate quantities by grouping similar ingredients from the recipes below. 
    Mention underlying recipes in recipe_notes using format "For <dish_name>". 
    Also add recipe_notes where recipe quantities have been combined or adapted for shopping, e.g. 5 cloves of garlic -> 1 head of garlic.
    Use {preferred_units} units for all quantities, converting where necessary.
    Categorize each item into one of the following categories: {[cat[1] for cat in ShoppingCategory.CATEGORIES]}.

    {recipes}
    """

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            response_format=ShoppingList,
            messages=[
                {"role": "system", "content": "Generate a shopping list in JSON format."},
                {"role": "user", "content": user_input}
            ],
        )
        
        shopping_list = completion.choices[0].message.parsed
        return shopping_list
    except Exception as e:
        print(f"Error generating shopping list: {e}")
        raise e


# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a shopping list')
    parser.add_argument(
        '--recipes',
        required=True,
        help='Comma-separated list of filenames (e.g., korma.json,lasagna.json)',
        type=lambda x: [s.strip() for s in x.split(',')]
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    shopping_list = generate_shopping_list(args.recipes)
    return shopping_list

if __name__ == "__main__":
    shopping_list = main()
    print(shopping_list.model_dump_json(indent=2))
