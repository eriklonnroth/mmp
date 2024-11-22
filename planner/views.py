from django.contrib.auth.models import User
from django.contrib.staticfiles.finders import find
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.views.generic import DetailView, ListView
from planner.services.recipe_generator import generate_recipe
from planner.services.recipe_parser import parse_recipe_string
from planner.services.recipe_repository import save_recipe_to_db
from planner.services.recipe_to_file import save_recipe_to_file
from planner.services.shopping_list_generator import generate_shopping_list
from planner import forms
from planner.models import Recipe, MyRecipe
import json


def index(request):
    return render(request, "planner/index.html")

def profile(request):
    return render(request, "planner/settings/profile.html")

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


def recipes(request):
    return render(request, "planner/recipes/index.html")

def shopping_list(request):
    return render(request, "planner/shopping-list.html")

def magic_recipe(request):
    # Initialize form
    form = forms.MagicRecipeForm()
    context = {'form': form}
    
    # Check for recipe ID in query params
    recipe_id = request.GET.get('id')
    if recipe_id:
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            # Add recipe to context and render it in the target div
            context['id_in_url'] = recipe
        except (Recipe.DoesNotExist, ValueError):
            # Silently ignore invalid IDs
            pass
    
    return render(request, "planner/recipes/magic.html", context)

@require_http_methods(['POST'])
def action_add_group(request):   
    return render(request, 'planner/plan.html#partial-recipe-group')

@require_http_methods(['POST'])
def action_generate_recipe(request):
    form = forms.MagicRecipeForm(request.POST)
    if form.is_valid():
        try:
            recipe_string = generate_recipe(
                dish_idea=form.cleaned_data['dish_idea'],
                notes=form.cleaned_data.get('notes', ''),
                servings=form.cleaned_data['servings'],
                dietary_preferences=form.cleaned_data.get('dietary_preferences', ''),
                units=form.cleaned_data.get('units', 'metric')
            )
            parsed_recipe = parse_recipe_string(recipe_string)
            save_recipe_to_file(parsed_recipe)
            saved_recipe = save_recipe_to_db(parsed_recipe, status='draft')
            response = render(request, 'planner/recipes/partial_recipe_detail.html', 
                            {'recipe': saved_recipe})
            response['HX-Push'] = f'?id={saved_recipe.id}'
            return response
        except Exception as e:
            return HttpResponseBadRequest(f"Error generating recipe: {str(e)}")
    else:
        return HttpResponseBadRequest("Invalid form data")

@require_http_methods(['POST'])
def action_save_to_my_recipes(request, recipe_id):
    try:
        user = request.user if request.user.is_authenticated else User.objects.get(username='admin')
        recipe = Recipe.objects.get(id=recipe_id)
        MyRecipe.objects.get_or_create(recipe=recipe, user=user)
        response = HttpResponse('Saved to My Recipes')
        response['HX-Trigger'] = 'recipeSaved'
        response['HX-Classes'] = 'recipe-saved'
        return response
    except Recipe.DoesNotExist:
        return HttpResponseBadRequest('Recipe not found')
    except IntegrityError:
        return HttpResponseBadRequest('Recipe already in My Recipes')
    except ValueError:
        return HttpResponseBadRequest('Invalid recipe ID')

@method_decorator(csrf_exempt, name='dispatch')
class GenerateRecipeView(View):
    def post(self, request, *args, **kwargs):
        # Parse user input from Magic Recipe generator
        data = json.loads(request.body.decode('utf-8'))
        dish_idea = data.get("dish_idea")
        notes = data.get("notes", "")
        dietary_preferences = data.get("dietary_preferences", "")
        servings = data.get("servings")
        units = data.get("units", "")

        try:
            # Pass user input to OpenAI to generate the recipe
            recipe = generate_recipe(dish_idea, notes, servings, units, dietary_preferences)
            try:
                parsed_recipe = parse_recipe_string(recipe)
                return JsonResponse(parsed_recipe.model_dump())
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
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

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'planner/recipes/detail.html'
    context_object_name = 'recipe'

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'ingredients',
            'instruction_sections',
            'instruction_sections__steps'
        )


class RecipeCardListView(ListView):
    model = Recipe
    template_name = 'planner/recipes/partial_recipe_card_list.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        queryset = Recipe.objects.all()
        
        # Get sort parameter (default to -created_at if not specified)
        sort_by = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort_by)
        
        # Get limit parameter
        try:
            limit = int(self.request.GET.get('limit', 10))
            queryset = queryset[:limit]
        except ValueError:
            queryset = queryset[:10]  # Fallback to 10 if invalid limit
            
        return queryset
    

