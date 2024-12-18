from openai import OpenAI
import os
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from planner.models import Recipe

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_recipe_image(prompt: str) -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd", # "hd" costs twice as much as "standard", see https://openai.com/api/pricing/
    )
    return response.data[0].url # Temporary URL valid for 60 minutes

def save_recipe_image(temp_url: str, recipe: Recipe) -> str:
    # Download the image from OpenAI temporary URL
    response = requests.get(temp_url)
    response.raise_for_status()  # Raises an HTTPError if the status is 4xx, 5xx
    
    image_content = ContentFile(response.content)
    
    recipe_title_slug = slugify(recipe.title, allow_unicode=False).replace("-", "_")
    file_name = f"{recipe_title_slug}.png"
    
    recipe.image.save(file_name, image_content, save=True)
    return recipe.image

def get_or_create_recipe_image(recipe: Recipe) -> str:
    if recipe.image:
        return recipe.image
    else:
        prompt = f"""
        An abstract watercolor illustration of this dish on a white background:
        {recipe.title}: {recipe.description}
        """

        temp_url = generate_recipe_image(prompt)
        saved_image = save_recipe_image(temp_url, recipe)
        return saved_image