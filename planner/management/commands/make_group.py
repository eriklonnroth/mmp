from django.core.management.base import BaseCommand
from planner.models import MealPlan, Group

class Command(BaseCommand):
    help = 'Creates a Group within a given mealplan'

    def handle(self, *args, **options):
        
        # Get the meal plan
        meal_plan = MealPlan.objects.get(id=3)

        # Create the group
        Group.objects.create(
            name='Boxing Day',
            meal_plan=meal_plan,
            order=2
        )

        for group in meal_plan.groups.all():
            self.stdout.write(f'- {group.name}')