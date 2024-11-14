from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponse
import json

def index(request):
    return render(request, "planner/index.html")

def plan(request):
    with open('planner/static/data/groupings.json') as f:
        groupings = json.load(f)
    with open('planner/static/data/recipes.json') as f:
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
