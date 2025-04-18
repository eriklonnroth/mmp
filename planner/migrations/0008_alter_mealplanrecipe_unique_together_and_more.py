# Generated by Django 5.1.3 on 2024-12-03 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0007_alter_mealplanrecipe_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="mealplanrecipe",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="mealgroup",
            name="name",
            field=models.CharField(default="New Group", max_length=20),
        ),
        migrations.AlterField(
            model_name="mealplan",
            name="name",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="mealplanrecipe",
            name="meal_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mprs",
                to="planner.mealgroup",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="mealplanrecipe",
            unique_together={("meal_group", "recipe")},
        ),
    ]
