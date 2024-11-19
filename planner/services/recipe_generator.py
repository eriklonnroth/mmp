from openai import OpenAI
from pydantic import BaseModel, Field
import os

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
    dish_name: str
    description: str
    servings: int
    ingredients: list[Ingredient]  # List of ingredient items with their quantities
    instructions: list[InstructionSection]  # List of instruction sections, each containing ordered steps


# OpenAI API function
def generate_recipe(dish_idea, servings, notes="", dietary_preferences="", units="metric"):
    """
    Generates a recipe in JSON format. See https://platform.openai.com/docs/guides/structured-outputs
    """
    user_input = f"""
    Make me a recipe based on the following guidelines:

    Dish idea: {dish_idea}
    Servings: {servings}
    {f'Notes: {notes}' if notes else ''}
    {f'Dietary preferences: {dietary_preferences}' if dietary_preferences else ''}
    Provide quantities in {units} units, but teaspoons and tablespoonss are acceptable
    """

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            response_format=Recipe,
            messages=[
                {"role": "system", "content": "You are an experienced home cook. Generate a detailed recipe in JSON format."},
                {"role": "user", "content": user_input}
            ],
        )
        
        recipe_str = completion.choices[0].message.content
        return recipe_str
    except Exception as e:
        print(f"Error generating recipe: {e}")
        raise e
