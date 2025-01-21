from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='Template',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=255)),
        #         ('template_type', models.CharField(choices=[('weekday', 'Weekday'), ('meal_type', 'Meal Type'), ('custom', 'Custom')], max_length=20)),
        #         ('created_at', models.DateTimeField(auto_now_add=True)),
        #         ('modified_at', models.DateTimeField(auto_now=True)),
        #         ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
        #     ],
        # ),
        # migrations.CreateModel(
        #     name='MealPlan',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=100)),
        #         ('created_at', models.DateTimeField(auto_now_add=True)),
        #         ('modified_at', models.DateTimeField(auto_now=True)),
        #         ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='planner.template')),
        #         ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
        #     ],
        #     options={
        #         'ordering': ['-modified_at'],
        #     },
        # ),
        # migrations.CreateModel(
        #     name='Group',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=100)),
        #         ('order', models.IntegerField(default=0)),
        #         ('created_at', models.DateTimeField(auto_now_add=True)),
        #         ('modified_at', models.DateTimeField(auto_now=True)),
        #         ('meal_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='planner.mealplan')),
        #     ],
        #     options={
        #         'ordering': ['order'],
        #     },
        # ),
        # migrations.CreateModel(
        #     name='ShoppingCategory',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(choices=[('fruit_veg', 'Fruit & Vegetables'), ('meat_fish', 'Meat & Fish'), ('dairy', 'Dairy & Deli'), ('bakery', 'Bakery'), ('pantry', 'Pantry'), ('drinks', 'Drinks'), ('snacks', 'Snacks'), ('frozen', 'Frozen'), ('non_food', 'Non-food')], max_length=50, unique=True)),
        #         ('order', models.PositiveIntegerField(unique=True)),
        #     ],
        #     options={
        #         'verbose_name_plural': 'Categories',
        #         'ordering': ['order'],
        #     },
        # ),
        # migrations.CreateModel(
        #     name='ShoppingList',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('created_at', models.DateTimeField(auto_now_add=True)),
        #         ('modified_at', models.DateTimeField(auto_now=True)),
        #         ('content_digest', models.CharField(blank=True, max_length=64)),
        #         ('meal_plan', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='planner.mealplan')),
        #         ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
        #     ],
        # ),
        # migrations.CreateModel(
        #     name='ShoppingItem',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('item', models.CharField(max_length=200)),
        #         ('quantity', models.CharField(max_length=100)),
        #         ('is_checked', models.BooleanField(default=False)),
        #         ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='planner.shoppingcategory')),
        #         ('shopping_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='planner.shoppinglist')),
        #     ],
        #     options={
        #         'ordering': ['category__order', 'item'],
        #     },
        # ),
        migrations.AddConstraint(
            model_name='group',
            constraint=models.UniqueConstraint(fields=('meal_plan', 'order'), name='unique_meal_plan_group_order'),
        ),
    ] 