from django.urls import path

from . import views

urlpatterns= [
    path("", views.index, name="index"),
    path("plan", views.plan, name="plan"),
    path("action_add_group", views.action_add_group, name="action_add_group"),
    path("recipes", views.recipes, name="recipes"),
    path("shopping-list", views.shopping_list, name="shopping_list"),
]
