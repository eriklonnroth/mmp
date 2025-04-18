# Generated by Django 5.1.3 on 2024-12-16 10:46

import planner.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0029_alter_recipe_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=planner.models.recipe_image_path
            ),
        ),
    ]
