from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

class MealPlan(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-modified_at']

class MealGroup(models.Model):
    name = models.CharField(max_length=20, default='New Group')
    meal_plan = models.ForeignKey(MealPlan, related_name='groups', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['order']
        constraints = [
            # Ensure unique ordering within a meal plan
            models.UniqueConstraint(
                fields=['meal_plan', 'order'],
                name='unique_meal_plan_group_order'
            )
        ]

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
    saved_to_my_recipes_by = models.ManyToManyField(
        User,
        through='MyRecipe',
        related_name='my_recipes'
    )

    def __str__(self):
        return f"{self.dish_name}"

    class Meta:
        ordering = ['-modified_at']
        indexes = [
            models.Index(fields=['created_by', 'created_at', 'status']),
        ]



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


# Recipe added to Meal Plan Group by user
class MealPlanRecipe(models.Model):
    meal_group = models.ForeignKey(MealGroup, related_name='mprs', on_delete=models.CASCADE) # Deletes the meal plan recipe if the parent group is deleted
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT) # Prevents deletion of underlying recipe if it's used in a meal plan
    modified_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ['meal_group', 'recipe']
        ordering = ['meal_group', 'order']

    def __str__(self):
        return f"{self.recipe.dish_name}"


# Shopping list models
class ShoppingList(models.Model):
    meal_plan = models.OneToOneField('MealPlan', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shopping List for {self.meal_plan.name}"


class ShoppingItem(models.Model):
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
    shopping_list = models.ForeignKey(ShoppingList, related_name='items', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    item = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} {self.item}"
    
    def get_category_order(self):
        # Return index of this item's category in CATEGORIES list
        return next(i for i, (cat, _) in enumerate(self.CATEGORIES) if cat == self.category)

    class Meta:
        ordering = ['category', 'item']








# Signals to update parent modified_at timestamps
@receiver(post_save, sender=MealPlanRecipe)
def update_group_modified(sender, instance, **kwargs):
    """Update the parent MealGroup's modified_at when a MealPlanRecipe changes"""
    if instance.meal_group:
        instance.meal_group.modified_at = timezone.now()
        instance.meal_group.save(update_fields=['modified_at'])

@receiver(post_save, sender=MealGroup)
def update_meal_plan_modified(sender, instance, **kwargs):
    """Update the parent MealPlan's modified_at when a Group changes"""
    if instance.meal_plan:
        instance.meal_plan.modified_at = timezone.now()
        instance.meal_plan.save(update_fields=['modified_at'])

@receiver(post_save, sender=ShoppingItem)
def update_shopping_list_modified(sender, instance, **kwargs):
    """Update the parent ShoppingList's modified_at when a ShoppingItem changes"""
    if instance.shopping_list:
        instance.shopping_list.modified_at = timezone.now()
        instance.shopping_list.save(update_fields=['modified_at'])

@receiver(post_save, sender=MealPlanRecipe)
def reorder_on_delete(sender, instance, **kwargs):
    """
    When a MealPlanRecipe is deleted, reorder the remaining recipes in the same group
    to ensure consecutive ordering without gaps
    """
    # Get all recipes in the same group with a higher order than the deleted one
    recipes = MealPlanRecipe.objects.filter(
        meal_group=instance.meal_group,
        order__gt=instance.order
    ).order_by('order')
    
    # Decrease their order by 1
    for i, recipe in enumerate(recipes):
        new_order = instance.order + i
        if recipe.order != new_order:
            recipe.order = new_order
            recipe.save(update_fields=['order'])
