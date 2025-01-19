from django.urls import path, re_path
from . import views

UUID = r'(?:[^/]*-)?(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'

# Core pages
core_patterns = [
    path("", views.index, name="index"),
    path("settings/preferences/", views.preferences, name="preferences"),
    path("settings/account/", views.account, name="account"),
    path("terms/", views.terms, name="terms"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
]

# Recipe routes
recipe_patterns = [
    path("recipes/", views.recipes, name="recipes"),
    # path("recipes/<int:pk>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    re_path(f'^recipes/{UUID}/?$', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path("recipes/cards/", views.RecipeCardsListView.as_view(), name="recipe_cards_list"),
    path("recipes/compact/", views.RecipeCompactListView.as_view(), name="recipe_compact_list"),
    path("recipes/cards/page/", views.RecipeCardsPageView.as_view(), name="recipe_cards_page"),
    path("recipes/compact/page/", views.RecipeCompactPageView.as_view(), name="recipe_compact_page"),
    path("recipes/search/cards/", views.RecipeSearchCards.as_view(), name="recipe_search_cards"),
    path("recipes/search/compact/", views.RecipeSearchCompact.as_view(), name="recipe_search_compact"),
    path("recipes/create/", views.create_recipe, name="create_recipe")
]

# Meal Plan routes
meal_plan_patterns = [
    path("meal-plan/", views.meal_plan, name="meal_plan"),
    path("meal-plan/new/", views.new_meal_plan, name="new_meal_plan"),
    # path("meal-plan/<int:pk>/", views.MealPlanDetailView.as_view(), name="meal_plan_detail"),
    re_path(f'^meal-plan/{UUID}/?$', views.MealPlanDetailView.as_view(), name='meal_plan_detail'),
    path("meal-plan/add-meal-modal/<int:meal_group_id>/", views.add_meal_modal, name="add_meal_modal"),
]

# Shopping List routes
shopping_list_patterns = [
    path("shopping-list/", views.shopping_list, name="shopping_list"),
    # path("shopping-list/<int:pk>/", views.ShoppingListDetailView.as_view(), name="shopping_list_detail"),
    re_path(f'^shopping-list/{UUID}/?$', views.ShoppingListDetailView.as_view(), name='shopping_list_detail'),
]

# HTMX Actions
action_patterns = [
    path("action_create_meal_plan/<str:template>/", views.action_create_meal_plan, name="action_create_meal_plan"),
    path("action_delete_meal_plan/<int:meal_plan_id>/", views.action_delete_meal_plan, name="action_delete_meal_plan"),
    path("action_generate_recipe/", views.action_generate_recipe, name="action_generate_recipe"),
    path("action_generate_recipe_image/<int:recipe_id>/", views.action_generate_recipe_image, name="action_generate_recipe_image"),
    path("action_toggle_my_recipes/<int:recipe_id>/", views.action_toggle_my_recipes, name="action_toggle_my_recipes"),
    path("action_toggle_mpr/<int:meal_group_id>/<int:recipe_id>/", views.action_toggle_mpr, name="action_toggle_mpr"),
    path("action_delete_meal_plan_recipe/<int:mpr_id>/", views.action_delete_meal_plan_recipe, name="action_delete_meal_plan_recipe"),
    path("action_add_meal_group/<int:meal_plan_id>/", views.action_add_meal_group, name="action_add_meal_group"),
    path("action_delete_meal_group/<int:group_id>/", views.action_delete_meal_group, name="action_delete_meal_group"),
    path("action_update_meal_group_name/<int:group_id>/", views.action_update_meal_group_name, name="action_update_meal_group_name"),
    path("action_update_meal_plan_name/<int:meal_plan_id>/", views.action_update_meal_plan_name, name="action_update_meal_plan_name"),
    path("action_update_mpr/<int:mpr_id>/<int:new_group_id>/", views.action_update_mpr, name="action_update_mpr"),
    path("action_generate_shopping_list/<int:meal_plan_id>/", views.action_generate_shopping_list, name="action_generate_shopping_list"),
    path("action_delete_shopping_list/<int:shopping_list_id>/", views.action_delete_shopping_list, name="action_delete_shopping_list"),
    path("action_update_shopping_list_name/<int:shopping_list_id>/", views.action_update_shopping_list_name, name="action_update_shopping_list_name"),
    path("action_add_shopping_item/<int:shopping_list_id>/", views.action_add_shopping_item, name="action_add_shopping_item"),
    path("action_delete_shopping_item/<int:item_id>/", views.action_delete_shopping_item, name="action_delete_shopping_item"),
    path("action_update_preferences/", views.action_update_preferences, name="action_update_preferences"),
    path("action_delete_account/", views.action_delete_account, name="action_delete_account"),
]

# API routes
api_patterns = [
    path("api/generate-recipe/", views.GenerateRecipeView.as_view(), name="generate_recipe"),
    path("api/generate-shopping-list/", views.GenerateShoppingListView.as_view(), name="generate_shopping_list"),
]

# URL patterns
urlpatterns = [
    *core_patterns,
    *recipe_patterns,
    *meal_plan_patterns,
    *shopping_list_patterns,
    *action_patterns,
    *api_patterns,
]