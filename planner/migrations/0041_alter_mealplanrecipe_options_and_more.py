# Generated by Django 5.1.3 on 2025-01-24 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0040_alter_mealplan_uuid_alter_shoppinglist_uuid"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mealplanrecipe",
            options={},
        ),
        migrations.AlterUniqueTogether(
            name="mealplanrecipe",
            unique_together=set(),
        ),
        migrations.AlterOrderWithRespectTo(
            name="mealplanrecipe",
            order_with_respect_to="meal_group",
        ),
    ]
