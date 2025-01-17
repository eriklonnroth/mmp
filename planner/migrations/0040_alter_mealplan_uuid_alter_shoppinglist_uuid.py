# Generated by Django 5.1.3 on 2025-01-17 21:57

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0039_alter_mealplan_uuid_alter_shoppinglist_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mealplan",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="shoppinglist",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
