from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
import os
import argparse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Base models (maps to JSON response and models.py)
class Ingredient(BaseModel):
    item: str
    quantity: str

class InstructionStep(BaseModel):
    step: str

class InstructionSection(BaseModel):
    section_title: str
    steps: list[InstructionStep]

class Recipe(BaseModel):
    recipe_name: str
    servings: int
    description: str
    ingredients: list[Ingredient]  # List of ingredient items with their quantities
    instructions: list[InstructionSection]  # List of instruction sections, each containing ordered steps


# Service functions
def generate_recipe(dish_name, servings, notes="", country="UK", dietary_preferences=""):
    """
    Generates a recipe in JSON format. See https://platform.openai.com/docs/guides/structured-outputs
    """
    user_input = f"""
    Make me a recipe based on the following guidelines:

    Dish name: {dish_name}
    Servings: {servings}
    {f'Notes: {notes}' if notes else ''}
    {f'Dietary preferences: {dietary_preferences}' if dietary_preferences else ''}
    Quantities should be in the measurement units of: {country}
    """

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            response_format=Recipe,
            messages=[
                {"role": "system", "content": "You are an experienced home cook. Generate detailed recipes in JSON format."},
                {"role": "user", "content": user_input}
            ],
        )
        
        recipe = completion.choices[0].message.parsed
        return recipe
    except Exception as e:
        print(f"Error generating recipe: {e}")
        raise e

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a recipe')
    parser.add_argument('--dish_name', required=True, help='Name of the dish')
    parser.add_argument('--notes', default='', help='Additional notes')
    parser.add_argument('--servings', type=int, required=True, help='Number of servings')
    parser.add_argument('--country', default='UK', help='Country for measurement units')
    parser.add_argument('--dietary_preferences', default='', help='Dietary preferences')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    recipe = generate_recipe(
        args.dish_name,
        args.notes,
        args.servings,
        args.country,
        args.dietary_preferences
    )
    
    print(recipe.model_dump_json(indent=2))

if __name__ == "__main__":
    main()