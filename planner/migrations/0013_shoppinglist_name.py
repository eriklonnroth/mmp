# Generated by Django 5.1.3 on 2024-12-14 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0012_shoppingitem_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppinglist",
            name="name",
            field=models.CharField(default="Shopping List", max_length=20),
        ),
    ]
