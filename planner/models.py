import uuid
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dietary_preferences = models.CharField(max_length=255, blank=True, null=True)
    default_servings = models.IntegerField(default=4)
    preferred_units = models.CharField(max_length=10, default='metric')


# Meal Plan models

class MealPlan(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('meal_plan_detail', kwargs={'uuid': self.uuid})

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

def recipe_image_path(instance, filename):
    return f'recipes/{instance.id}/{filename}'

class Recipe(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=100)
    servings = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    image = models.ImageField(upload_to=recipe_image_path, blank=True, null=True)
    image_thumb = ImageSpecField(
        source='image',
        processors=[ResizeToFill(128, 128)],
        format='JPEG',
        options={'quality': 70}
    )
    image_medium = ImageSpecField(
        source='image',
        processors=[ResizeToFill(512, 512)],
        format='JPEG',
        options={'quality': 70}
    )
    saved_to_my_recipes_by = models.ManyToManyField(
        User,
        through='MyRecipe',
        related_name='my_recipes'
    )

    def get_absolute_url(self):
        title_slug = slugify(self.title)
        return f"/recipes/{title_slug}-{self.uuid}/"
    
    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['-modified_at']
        indexes = [
            models.Index(fields=['created_by', 'created_at', 'status']),
        ]


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} {self.name}"

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
    text = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.text}"

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
        return f"{self.recipe.title}"


# Recipe added to Meal Plan Group by user
class MealPlanRecipe(models.Model):
    meal_group = models.ForeignKey(MealGroup, related_name='mprs', on_delete=models.CASCADE) # Deletes the meal plan recipe if the parent group is deleted
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT) # Prevents deletion of underlying recipe if it's used in a meal plan
    modified_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField()

    class Meta:
        order_with_respect_to = 'meal_group'

    def __str__(self):
        return f"{self.recipe.title}"


# Shopping list models

class ShoppingList(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=40, default='Shopping List')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    last_viewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('shopping_list_detail', kwargs={'uuid': self.uuid})

class ShoppingItem(models.Model):
    CATEGORIES = [
        ('fruit_veg', 'Fruit & Vegetables'),
        ('meat_fish', 'Meat & Fish'),
        ('dairy', 'Dairy & Deli'),
        ('bakery', 'Bakery'),
        ('pantry', 'Pantry'),
        ('snacks', 'Snacks'),
        ('frozen', 'Frozen'),
        ('drinks', 'Drinks'),
        ('non_food', 'Non-food')
    ]
    shopping_list = models.ForeignKey(ShoppingList, related_name='items', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100, blank=True, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} {self.name}"
    
    class Meta:
        ordering = ['category', 'name']











# SIGNALS
@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        Preferences.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    instance.preferences.save()

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