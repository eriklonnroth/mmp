from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import hashlib
import json

from .utils import scale_quantity

# Recipe models
class Recipe(models.Model):
    name = models.CharField(max_length=100)
    servings = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)
    ingredients_digest = models.CharField(max_length=64, blank=True)

    def get_scaled_ingredients(self, new_servings):
        """Returns a list of ingredients with quantities scaled but NOT saved."""
        scaled = []
        for ingredient in self.ingredients.all():
            scaled.append({
                'item': ingredient.item,
                'quantity': scale_quantity(ingredient.quantity, self.servings, new_servings),
                'order': ingredient.order
            })
        return scaled
    
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
        return f"{self.name} (for {self.servings})"

    class Meta:
        ordering = ['-modified_at']

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
        return f"{self.recipe.name} - {self.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['recipe', 'order']


class InstructionStep(models.Model):
    section = models.ForeignKey(InstructionSection, related_name='steps', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.section.recipe.name} - {self.section.title} - Step {self.order}"

    class Meta:
        ordering = ['order']
        unique_together = ['section', 'order']
        indexes = [
            models.Index(fields=['section', 'order']),
        ]

# Plan models
class Plan(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['-modified_at']


class Group(models.Model):
    plan = models.ForeignKey(Plan, related_name='groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Plan: {self.plan.name})"

    class Meta:
        ordering = ['order']
        unique_together = ['plan', 'order']


class GroupRecipe(models.Model):
    group = models.ForeignKey(Group, related_name='recipes', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    servings = models.PositiveIntegerField()

    @property
    def scaled_ingredients(self):
        """Returns the recipe's ingredients scaled to group servings count."""
        return self.recipe.get_scaled_ingredients(self.servings)

    @property
    def scaling_factor(self):
        """Returns the ratio of group servings to recipe servings."""
        return self.servings / self.recipe.servings

    def preview_scaled_recipe(self):
        """Returns dictionary with all recipe data scaled to group servings."""
        return {
            'title': self.recipe.title,
            'servings': self.servings,
            'notes': self.recipe.notes,
            'ingredients': self.scaled_ingredients,
            'instruction_sections': self.recipe.instruction_sections.all(),
        }

    def __str__(self):
        return f"{self.recipe.name} (for {self.servings}) - {self.group.name}"



# Shopping list models
class ShoppingCategory(models.Model):
    CATEGORIES = [
        ('fruit_veg', 'Fruit & Vegetables'),
        ('meat_fish', 'Meat & Fish'),
        ('dairy', 'Dairy & Refrigerated'),
        ('bakery', 'Bakery'),
        ('pantry', 'Pantry'),
        ('drinks', 'Drinks'),
        ('snacks', 'Snacks'),
        ('frozen', 'Frozen'),
        ('non_food', 'Non-food'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=50, choices=CATEGORIES, unique=True)
    order = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Categories'


class ShoppingList(models.Model):
    plan = models.OneToOneField('Plan', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
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
