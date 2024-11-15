from django.contrib.staticfiles.finders import find
from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from planner.services.recipe_generator import generate_recipe
from planner.services.shopping_list_generator import generate_shopping_list

import json


def index(request):
    return render(request, "planner/index.html")


def plan(request):
    groupings_path = find('planner/data/groupings.json')
    recipes_path = find('planner/data/recipes.json')

    with open(groupings_path) as f:
        groupings = json.load(f)
    with open(recipes_path) as f:
        recipes = json.load(f)
        
    context = {
        'groupings': groupings,
        'recipes': recipes,
    }
    return render(request, "planner/plan.html", context)

def action_add_group(request):
    if request.method == 'POST':        
        html = render(request, 'planner/plan.html#partial-recipe-group').content.decode('utf-8')
        return HttpResponse(html)
    return HttpResponseNotAllowed(['POST'])

def recipes(request):
    return render(request, "planner/recipes.html")

def shopping_list(request):
    return render(request, "planner/shopping-list.html")

@method_decorator(csrf_exempt, name='dispatch')
class GenerateRecipeView(View):
    def post(self, request, *args, **kwargs):
        # Parse incoming data from the request
        data = json.loads(request.body.decode('utf-8'))
        dish_name = data.get("dish_name")
        notes = data.get("notes", "")
        servings = data.get("servings")
        country = data.get("country", "")
        dietary_preferences = data.get("dietary_preferences", "")

        try:
            # Call the OpenAI service to generate the recipe
            recipe = generate_recipe(dish_name, notes, servings, country, dietary_preferences)
            return JsonResponse(recipe)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerateShoppingListView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse incoming data from the request
            data = json.loads(request.body.decode('utf-8'))
            recipe_files = data.get("recipes", [])

            if not recipe_files:
                return JsonResponse({
                    "error": "No recipes provided"
                }, status=400)

            # Call the OpenAI service to generate the shopping list
            shopping_list = generate_shopping_list(recipe_files)
            
            # Convert Pydantic model to dict for JsonResponse
            return JsonResponse(shopping_list.model_dump())
            
        except FileNotFoundError as e:
            return JsonResponse({
                "error": f"Recipe file not found: {str(e)}"
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                "error": f"Error generating shopping list: {str(e)}"
            }, status=500)