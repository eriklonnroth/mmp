from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import hashlib
import json

from .utils import scale_quantity


# Plan models
class Plan(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['-modified_at']

class Grouping(models.Model):
    GROUPING_TYPES = [
        ('weekday', 'Weekday'),
        ('meal_type', 'Meal Type'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=255)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user'],
                condition=models.Q(plan__isnull=True),
                name='unique_template_name'
            ),
            models.UniqueConstraint(
                fields=['name', 'plan'],
                name='unique_plan_name'
            )
        ]

class Group(models.Model):
    grouping = models.ForeignKey(Grouping, related_name='groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.order == 0:  # If order not explicitly set
            last_order = Group.objects.filter(
                grouping=self.grouping
            ).aggregate(
                models.Max('order')
            )['order__max'] or 0
            self.order = last_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Grouping: {self.grouping.name})"

    class Meta:
        ordering = ['order']
        unique_together = ['grouping', 'order']


# Recipe models
class Recipe(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    dish_name = models.CharField(max_length=100)
    servings = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    ingredients_digest = models.CharField(max_length=64, blank=True)
    saved_to_my_recipes_by = models.ManyToManyField(
        User,
        through='MyRecipe',
        related_name='my_recipes'
    )

    def get_scaled_recipe(self, new_servings: int) -> dict:
        """Returns a complete scaled version of the recipe."""
        scaled_ingredients = []
        for ingredient in self.ingredients.all():
            new_quantity, new_item = scale_quantity(
                ingredient.quantity,
                ingredient.item,
                self.servings,
                new_servings
            )
            scaled_ingredients.append({
                'quantity': new_quantity,
                'item': new_item,
                'order': ingredient.order
            })
        
        return {
            'dish_name': self.dish_name,
            'servings': new_servings,
            'notes': self.notes,
            'ingredients': scaled_ingredients,
            'instruction_sections': self.instruction_sections.all(),
        }

    def scale_and_save(self, new_servings):
        """Permanently scales the recipe to a new serving size."""
        old_servings = self.servings
        self.servings = new_servings
        
        # Batch all ingredient updates
        ingredients_to_update = []
        for ingredient in self.ingredients.all():
            ingredient.quantity = scale_quantity(
                ingredient.quantity,
                old_servings,
                new_servings
            )
            ingredients_to_update.append(ingredient)
        
        # Bulk update ingredients without triggering individual saves
        Ingredient.objects.bulk_update(ingredients_to_update, ['quantity'])
        
        # Update the digest once after all changes
        self.update_ingredients_digest()
        self.save()

    def update_ingredients_digest(self):
        """Create a digest of all ingredients data including servings count"""
        ingredients_data = list(self.ingredients.order_by('order').values('item', 'quantity'))
        data_string = json.dumps({
            'servings': self.servings,
            'ingredients': ingredients_data
        }, sort_keys=True)
        self.ingredients_digest = hashlib.sha256(data_string.encode()).hexdigest()
        self.save(update_fields=['ingredients_digest'])

    def __str__(self):
        return f"{self.dish_name}"

    class Meta:
        ordering = ['-modified_at']
        indexes = [
            models.Index(fields=['created_by', 'created_at', 'status']),
        ]

@receiver(post_save, sender='planner.Ingredient')
def update_recipe_digest(sender, instance, **kwargs):
    instance.recipe.update_ingredients_digest()


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} {self.item}"

    class Meta:
        ordering = ['order']
        unique_together = ['recipe', 'order']


class InstructionSection(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='instruction_sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['recipe', 'order']


class InstructionStep(models.Model):
    section = models.ForeignKey(InstructionSection, related_name='steps', on_delete=models.CASCADE)
    step = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.step}"

    class Meta:
        ordering = ['order']
        unique_together = ['section', 'order']
        indexes = [
            models.Index(fields=['section', 'order']),
        ]

# Recipe saved to My Recipes by user
class MyRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.recipe.dish_name}"



# Scaled recipe for specific meal plan
class ScaledRecipe(models.Model):
    group = models.ForeignKey(Group, related_name='recipes', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    servings = models.PositiveIntegerField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ['group', 'order']
        db_table = 'planner_scaledrecipe'  # Optional: keep old table name if preserving data


# Shopping list models
class ShoppingList(models.Model):
    plan = models.OneToOneField('Plan', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)
    content_digest = models.CharField(max_length=64, blank=True)  # SHA-256 hash

    def update_content_digest(self):
        # Collect all recipe digests and servings counts
        digest_data = []
        for group in self.plan.groups.all():
            for group_recipe in group.recipes.all():
                digest_data.append({
                    'recipe_digest': group_recipe.recipe.ingredients_digest,
                    'servings': group_recipe.servings
                })

        # Create a digest of the entire shopping list state
        data_string = json.dumps(digest_data, sort_keys=True)
        self.content_digest = hashlib.sha256(data_string.encode()).hexdigest()
        self.save(update_fields=['content_digest'])

    def is_out_of_sync(self):
        # Recalculate what the digest should be
        old_digest = self.content_digest
        self.update_content_digest()
        return old_digest != self.content_digest


    def __str__(self):
        return f"Shopping List for {self.plan.name}"


class ShoppingCategory(models.Model):
    CATEGORIES = [
        ('fruit_veg', 'Fruit & Vegetables'),
        ('meat_fish', 'Meat & Fish'),
        ('dairy', 'Dairy & Deli'),
        ('bakery', 'Bakery'),
        ('pantry', 'Pantry'),
        ('drinks', 'Drinks'),
        ('snacks', 'Snacks'),
        ('frozen', 'Frozen'),
        ('non_food', 'Non-food')
    ]

    name = models.CharField(max_length=50, choices=CATEGORIES, unique=True)
    order = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Categories'


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, related_name='items', on_delete=models.CASCADE)
    category = models.ForeignKey(ShoppingCategory, related_name='items', on_delete=models.PROTECT)
    item = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} {self.item}"

    class Meta:
        ordering = ['category__order', 'item']

