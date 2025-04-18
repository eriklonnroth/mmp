# Generated by Django 5.1.3 on 2025-01-17 20:37

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0035_populate_recipe_uuids"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
