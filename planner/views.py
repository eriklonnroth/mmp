from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponse

# Import or define your initial_data and recipes here
from .data import initial_data, recipes  # Assuming you have a data.py file with these variables

def index(request):
    return render(request, "planner/index.html")

def plan(request):
    context = {
        'initial_groups': initial_data['weekday'].values(),
        'initial_data': initial_data,
        'recipes': recipes
    }
    return render(request, "planner/plan.html", context)

def action_add_group(request):
    if request.method == 'POST':        
        html = render(request, 'planner/plan.html#partial-recipe-group').content.decode('utf-8')
        return HttpResponse(html)
    return HttpResponseNotAllowed(['POST'])