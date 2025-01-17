# Generated by Django 5.1.3 on 2025-01-17 21:39

from django.db import migrations
import uuid 

def gen_uuid(apps, schema_editor):
    MealPlan = apps.get_model('planner', 'MealPlan')
    for row in MealPlan.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])

    ShoppingList = apps.get_model('planner', 'ShoppingList')
    for row in ShoppingList.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])

class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0037_mealplan_uuid_shoppinglist_uuid_alter_recipe_uuid"),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
