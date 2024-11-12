from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponse

# Create your views here.
def index(request):
    return render(request, "planner/index.html")

def plan(request):
    return render(request, "planner/plan.html")

def action_add_group(request):
    if request.method == 'POST':        
        html = render(request, 'planner/plan.html#partial-recipe-group').content.decode('utf-8')
        return HttpResponse(html)
    return HttpResponseNotAllowed(['POST'])