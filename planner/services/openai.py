from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_recipe(dish_name, notes, servings, country, dietary_preferences):
    """
    Generates a recipe in JSON format based on the provided parameters using OpenAI API.
    """
    # Construct the structured prompt for a JSON response
    prompt = f"""
    Generate a detailed recipe in JSON format:
    Dish Name: {dish_name}
    Notes: {notes}
    Servings: {servings}
    Country: {country}
    Dietary Preferences: {dietary_preferences}

    Response format:
    {{
        "recipe_name": "string",
        "servings": int,
        "description": "string",
        "ingredients": [{{ "Item": "string", "Quantity": "string" }}],
        "instructions": [{{ "section_title": "string", "steps": [{{ "step": int, "instruction": "string" }}] }}]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates recipes in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Extract and parse the assistant's response
        recipe = json.loads(response['choices'][0]['message']['content'].strip())
        return recipe
    except Exception as e:
        print(f"Error generating recipe: {e}")
        raise e