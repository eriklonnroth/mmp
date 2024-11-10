from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "planner/index.html")

def plan(request):
    return render(request, "planner/plan.html")