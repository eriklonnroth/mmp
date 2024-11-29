from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from planner.models import MealPlan, MealGroup
from planner.services.meal_plan_templates import TEMPLATES

TEMPLATE_KEY = 'blank'

class Command(BaseCommand):
    help = 'Creates a MealPlan with a given template'

    def handle(self, *args, **options):
        user = User.objects.get(username='admin')


        
        # Create the meal plan
        meal_plan = MealPlan.objects.create(
            name='Christmas Menu 2024',
            user=user
        )

        # Create the groups
        for i, group_name in enumerate(TEMPLATES[TEMPLATE_KEY]['meal_groups']):
            MealGroup.objects.create(
                name=group_name,
                meal_plan=meal_plan,
                order=i
            )

        self.stdout.write(self.style.SUCCESS(f'Created MealPlan: {meal_plan.name}'))
        self.stdout.write(f'Number of groups: {meal_plan.groups.count()}')
        for group in meal_plan.groups.all():
            self.stdout.write(f'- {group.name}')