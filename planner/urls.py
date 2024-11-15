from django.urls import path

from . import views

urlpatterns= [
    path("", views.index, name="index"),
    path("plan", views.plan, name="plan"),
    path("action_add_group", views.action_add_group, name="action_add_group"),
    path("recipes", views.recipes, name="recipes"),
    path("shopping-list", views.shopping_list, name="shopping_list"),
    path('api/generate-recipe/', views.GenerateRecipeView.as_view(), name='generate_recipe'),
    path('api/generate-shopping-list/', views.GenerateShoppingListView.as_view(), name='generate_shopping_list'),
]
