from openai import OpenAI
from pydantic import BaseModel
import os
from planner.models import MealPlan as MealPlan, ShoppingItem as DBShoppingItem

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Base models (maps to JSON response and models.py)
class ShoppingItem(BaseModel):
    name: str
    quantity: str
    category: str
    recipe_id: int # Foreign key to recipe

class ShoppingList(BaseModel):
    items: list[ShoppingItem]

# Load underlying recipes from MealPlan
def load_preliminary_shopping_list(meal_plan: MealPlan):
    shopping_list = []

    for group in meal_plan.groups.all():
        for mpr in group.mprs.all():
            recipe = mpr.recipe
            ingredients = recipe.ingredients.all()
            for ing in ingredients:
                shopping_item = ShoppingItem(
                    name=ing.name,
                    quantity=ing.quantity,
                    category='TBD',
                    recipe_id=recipe.id
                )
                shopping_list.append(shopping_item)
    return shopping_list

# OpenAI API function
def generate_shopping_list(meal_plan: MealPlan, preferred_units: str = "metric") -> ShoppingList:
    """
    Generates a shopping list in JSON format. See https://platform.openai.com/docs/guides/structured-outputs
    """
    shopping_list = load_preliminary_shopping_list(meal_plan)
    
    if not shopping_list:
        raise ValueError("No recipes found in meal plan to generate shopping list")
        
    user_input = f"""
    For each ShoppingItem in the ShoppingList:
        1. Where necessary, adjust the item name to be shopping-appropriate, e.g. "carrots, julienned" becomes "carrots", "steamed rice" becomes "rice".
        2. Where necessary, adjust the quantity to be shopping-appropriate and ensure it is in {preferred_units} units.
        3. Update the category to be one of the following: {[cat[1] for cat in DBShoppingItem.CATEGORIES]}. Derived items like "lemon zest" should be in the "Fruit & Vegetables" category since they are made from fresh produce (lemons).
        4. Leave the recipe_id field unchanged.
        5. Remove the entire ShoppingItem if it is one of: water, salt, pepper, olive oil.
    
    ShoppingList:
    {shopping_list}
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
        shopping_list_with_name = shopping_list.model_copy(
            update={'name': f"Shopping List for '{meal_plan.name}'"}
        )
        return shopping_list_with_name

    except Exception as e:
        print(f"Error generating shopping list: {e}")
        raise e