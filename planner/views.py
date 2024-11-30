from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
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
from planner.models import Recipe, MyRecipe, MealPlan, MealGroup, MealPlanRecipe
from planner.services.meal_plan_templates import TEMPLATES, get_default_meal_groups
import json


def index(request):
    return render(request, "planner/index.html")

def profile(request):
    return render(request, "planner/settings/profile.html")

def meal_plan(request):
    user = request.user if request.user.is_authenticated else None
    if not user:
        admin_user = User.objects.get(username='admin')
        user = admin_user

    recent_meal_plan = MealPlan.objects.filter(user=user).order_by('-modified_at').first()

    if recent_meal_plan:
        return redirect('meal_plan_detail', pk=recent_meal_plan.id)

    return redirect('new_meal_plan')

class MealPlanDetailView(DetailView):
    model = MealPlan
    template_name = 'planner/meal-plan/detail.html'
    context_object_name = 'meal_plan'

    def get_queryset(self):
        # Add prefetch_related to optimize queries
        queryset = MealPlan.objects.prefetch_related(
            'groups',
            'groups__mprs', # MealPlanRecipes
            'groups__mprs__recipe'  # Underlying recipe
        )
        
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            admin_user = User.objects.get(username='admin')
            user = admin_user
        #     return JsonResponse({
        #     'error': 'Authentication required'
        # }, status=401)
        
        # Filter queryset to only show user's meal plans
        return queryset.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create a list of groups with their recipes
        groups = []
        for group in self.object.groups.all():
            groups.append({
                'id': group.id,
                'name': group.name,
                'mprs': [{
                    'id': mpr.id,
                    'name': mpr.recipe.dish_name,
                    'recipe_id': mpr.recipe.id
                } for mpr in group.mprs.all()]
            })
        
        context['groups'] = groups
        return context

def new_meal_plan(request):
    return render(request, 'planner/meal-plan/new.html', {'templates': TEMPLATES})

def add_recipe_modal(request, group_id):
    meal_group = get_object_or_404(MealGroup, id=group_id)
    # Verify the user has access to this group
    if request.user.is_authenticated:
        if not meal_group.meal_plan.user == request.user:
            return HttpResponseForbidden("You don't have access to this group")
    
    context = {
        'meal_group': meal_group,
    }
    return render(request, "planner/meal-plan/add-recipe-to-group-modal.html", context)

def recipes(request):
    return render(request, "planner/recipes/index.html")

def shopping_list(request):
    return render(request, "planner/shopping-list/index.html")

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
            response = render(request, 'planner/recipes/partial_recipe.html', 
                            {'recipe': saved_recipe})
            response['HX-Push'] = f'?id={saved_recipe.id}'
            return response
        except Exception as e:
            return HttpResponseBadRequest(f"Error generating recipe: {str(e)}")
    else:
        return HttpResponseBadRequest("Invalid form data")

@require_http_methods(['POST'])
def action_toggle_my_recipes(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    user = request.user if request.user.is_authenticated else None
    if not user:
        admin_user = User.objects.get(username='admin')
        user = admin_user
    #     return JsonResponse({
    #         'error': 'Authentication required'
    # }, status=401)


    if user in recipe.saved_to_my_recipes_by.all():
        # Remove from My Recipes
        recipe.saved_to_my_recipes_by.remove(user)
        saved = False
    else:
        # Add to My Recipes
        recipe.saved_to_my_recipes_by.add(user)
        saved = True

    return JsonResponse({'saved': saved})

@require_http_methods(['POST'])
def action_create_meal_plan(request, template):
    
    user = request.user if request.user.is_authenticated else None
    if not user:
        admin_user = User.objects.get(username='admin')
        user = admin_user
    #     return JsonResponse({
    #         'error': 'Authentication required'
    # }, status=401)

    # Create the meal plan
    meal_plan = MealPlan.objects.create(
        name="New Meal Plan",
        user=user
    )

    # Create the meal groups
    meal_groups = get_default_meal_groups(template)
    for name in meal_groups:
        MealGroup.objects.create(
            name=name,
            meal_plan=meal_plan,
            order=MealGroup.objects.filter(meal_plan=meal_plan).count()
        )
    response = HttpResponse()
    response['HX-Redirect'] = f'/meal-plan/{meal_plan.id}'
    return response

@require_http_methods(['DELETE'])
def action_delete_meal_plan_recipe(request, mpr_id):
    meal_plan_recipe = get_object_or_404(MealPlanRecipe, id=mpr_id)
    meal_plan_recipe.delete()
    return HttpResponse('')

@require_http_methods(['POST'])
def action_add_meal_group(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    
    # Get the highest order value from existing groups
    highest_order = MealGroup.objects.filter(meal_plan=meal_plan).order_by('-order').values_list('order', flat=True).first()
    
    # If there are no existing groups, start with 0, otherwise increment
    next_order = 0 if highest_order is None else highest_order + 1
    
    group = MealGroup.objects.create(
        meal_plan=meal_plan,
        order=next_order
    )
    return render(request, 'planner/meal-plan/detail.html#partial-meal-group', {'group': group})

@require_http_methods(['DELETE'])
def action_delete_meal_group(request, group_id):
    meal_group = get_object_or_404(MealGroup, id=group_id)
    meal_group.delete()
    return HttpResponse('')

@require_http_methods(['POST'])
def action_update_meal_group_name(request, group_id):
    new_name = request.POST.get('meal_group_name')
    
    if not new_name:
        return HttpResponseBadRequest("Name required")
        
    try:
        group = get_object_or_404(MealGroup, id=group_id)
        group.name = new_name
        group.save()
        return HttpResponse('')
    except MealGroup.DoesNotExist:
        return HttpResponse(status=404)

@require_http_methods(['POST'])
def action_update_meal_plan_name(request, meal_plan_id):
    new_name = request.POST.get('meal_plan_name')
    
    if not new_name:
        return HttpResponseBadRequest("Name required")
        
    try:
        meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
        meal_plan.name = new_name
        meal_plan.save()
        return HttpResponse('')
    except MealPlan.DoesNotExist:
        return HttpResponse(status=404)


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
        queryset = Recipe.objects.prefetch_related(
            'ingredients',
            'instruction_sections',
            'instruction_sections__steps'
        )
        
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            admin_user = User.objects.get(username='admin')
            user = admin_user
        #     return JsonResponse({
        #     'error': 'Authentication required'
        # }, status=401)
            
        queryset = queryset.annotate(
            is_saved=Exists(
                MyRecipe.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
            )
        )
        
        return queryset


class RecipeListView(ListView):
    model = Recipe
    context_object_name = 'recipes'
    paginate_by = 12

    def get_queryset(self):
        queryset = Recipe.objects.all()
        
        # Get sort parameter (default to -created_at if not specified)
        sort_by = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort_by)

        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            admin_user = User.objects.get(username='admin')
            user = admin_user
        #     return JsonResponse({
        #         'error': 'Authentication required'
        # }, status=401)

        # Filter by My Recipes if requested
        my_recipes = self.request.GET.get('my_recipes') == 'true'
        if my_recipes:
            queryset = queryset.filter(saved_to_my_recipes_by=user)

        # For My Recipes toggle button, check if already saved
        queryset = queryset.annotate(
            is_saved=Exists(
                MyRecipe.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', '-created_at')
        context['my_recipes'] = self.request.GET.get('my_recipes') == 'true'
        return context

class RecipeCardsListView(RecipeListView):
    template_name = 'planner/recipes/partial_recipe_cards_list.html'

class RecipeCompactListView(RecipeListView):
    template_name = 'planner/recipes/partial_recipe_compact_list.html'

class RecipeCardsPageView(RecipeListView):
    template_name = 'planner/recipes/partial_recipe_cards_page.html'

class RecipeSearchView(RecipeCardsPageView):
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '').strip()
        
        if search_query:
            queryset = queryset.filter(
                Q(dish_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ingredients__item__icontains=search_query) |
                Q(instruction_sections__steps__step__icontains=search_query)
            ).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context
    

