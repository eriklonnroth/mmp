from django.urls import path

from . import views

urlpatterns= [
    path("", views.index, name="index"),
    path("settings/profile", views.profile, name="profile"),
    path("meal-plan/", views.meal_plan, name="meal_plan"),
    path("meal-plan/add-recipe-modal/<int:group_id>", views.add_recipe_modal, name="add_recipe_modal"),
    path("action_add_group", views.action_add_group, name="action_add_group"),
    path("action_generate_recipe", views.action_generate_recipe, name="action_generate_recipe"),
    path("action_toggle_my_recipes/<int:recipe_id>", views.action_toggle_my_recipes, name="action_toggle_my_recipes"),
    path("recipes/", views.recipes, name="recipes"),
    path("recipes/<int:pk>", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path("recipes/cards", views.RecipeCardsListView.as_view(), name="recipe_cards_list"),
    path("recipes/compact", views.RecipeCompactListView.as_view(), name="recipe_compact_list"),
    path("recipes/cards/page", views.RecipeCardsPageView.as_view(), name="recipe_cards_page"),
    path("recipes/search", views.RecipeSearchView.as_view(), name="recipe_search"),
    path("recipes/magic", views.magic_recipe, name="magic_recipe"),
    path("shopping-list/", views.shopping_list, name="shopping_list"),
    path("api/generate-recipe/", views.GenerateRecipeView.as_view(), name="generate_recipe"),
    path("api/generate-shopping-list/", views.GenerateShoppingListView.as_view(), name="generate_shopping_list"),
]
