from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Recipe, Ingredient, InstructionSection, InstructionStep, MealPlan, MealGroup, MealPlanRecipe, ShoppingList, ShoppingItem


# Recipe admin

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 0
    ordering = ['order']

class InstructionStepInline(admin.TabularInline):
    model = InstructionStep
    extra = 0
    ordering = ['order']

class InstructionSectionAdmin(admin.ModelAdmin):
    inlines = [InstructionStepInline]
    list_display = ('title', 'recipe', 'order')
    ordering = ['order']

class InstructionSectionInline(admin.TabularInline):
    model = InstructionSection
    extra = 0
    ordering = ['order']
    show_change_link = True  # This adds a link to edit the section's steps

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'servings', 'status', 'created_by', 'created_at', 'modified_at', 'get_image_preview')
    list_filter = ('status', 'created_at', 'modified_at', 'created_by')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'modified_at')
    date_hierarchy = 'created_at'
    ordering = ('-modified_at',)
    list_per_page = 50

    inlines = [IngredientInline, InstructionSectionInline]

    fieldsets = (
        ('Recipe Details', {
            'fields': ('title', 'description', 'servings', 'status', 'image')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;"/>', obj.image.url)
        return "No image"
    get_image_preview.short_description = 'Image'

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new recipe
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(InstructionSection)
class InstructionSectionAdmin(admin.ModelAdmin):
    inlines = [InstructionStepInline]
    list_display = ('title', 'recipe', 'order')
    list_filter = ('recipe',)
    ordering = ['recipe', 'order']


# Meal Plan admin


class MealPlanRecipeInline(admin.TabularInline):
    model = MealPlanRecipe
    extra = 0
    ordering = ['order']
    raw_id_fields = ['recipe']  # Adds a lookup widget for recipes
    readonly_fields = ['recipe_title', 'recipe_servings']

    def recipe_title(self, obj):
        if obj.recipe:
            return format_html('<a href="/admin/planner/recipe/{}/change/">{}</a>', 
                             obj.recipe.id, obj.recipe.title)
        return "-"
    recipe_title.short_description = "Recipe Title"

    def recipe_servings(self, obj):
        return obj.recipe.servings if obj.recipe else "-"
    recipe_servings.short_description = "Servings"

class MealGroupInline(admin.TabularInline):
    model = MealGroup
    extra = 0
    ordering = ['order']
    show_change_link = True
    readonly_fields = ['recipe_count']

    def recipe_count(self, obj):
        if obj.id:
            return obj.mprs.count()
        return 0
    recipe_count.short_description = "Number of Recipes"

@admin.register(MealGroup)
class MealGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal_plan', 'order', 'recipe_count')
    list_filter = ('meal_plan',)
    search_fields = ('name', 'meal_plan__name')
    ordering = ['meal_plan', 'order']
    inlines = [MealPlanRecipeInline]

    def recipe_count(self, obj):
        return obj.mprs.count()
    recipe_count.short_description = "Number of Recipes"

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'recipe_count', 'created_at', 'modified_at')
    list_filter = ('user', 'created_at', 'modified_at')
    search_fields = ('name', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'modified_at', 'recipe_count')
    ordering = ('-modified_at',)
    list_per_page = 50
    inlines = [MealGroupInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'recipe_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            recipe_count=Count('groups__mprs', distinct=True)
        )

    def recipe_count(self, obj):
        return obj.recipe_count
    recipe_count.admin_order_field = 'recipe_count'
    recipe_count.short_description = 'Number of Recipes'


# Shopping List admin

class ShoppingItemInline(admin.TabularInline):
    model = ShoppingItem
    extra = 0
    raw_id_fields = ['recipe']
    readonly_fields = ['recipe_title']
    fields = ('category', 'name', 'quantity', 'recipe', 'is_checked')
    ordering = ['category', 'name']

    def recipe_title(self, obj):
        if obj.recipe:
            return format_html('<a href="/admin/planner/recipe/{}/change/">{}</a>', 
                             obj.recipe.id, obj.recipe.title)
        return "-"
    recipe_title.short_description = "Recipe Title"

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'item_count', 'created_at', 'modified_at', 'last_viewed_at')
    list_filter = ('user', 'created_at', 'modified_at')
    search_fields = ('name', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'modified_at', 'last_viewed_at', 'item_count')
    ordering = ('-modified_at',)
    list_per_page = 50
    inlines = [ShoppingItemInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'item_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at', 'last_viewed_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            item_count=Count('items', distinct=True)
        )

    def item_count(self, obj):
        return obj.item_count
    item_count.admin_order_field = 'item_count'
    item_count.short_description = 'Number of Items'