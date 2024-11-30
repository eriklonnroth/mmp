# # Recipe models
# class Recipe(models.Model):
#     STATUS_CHOICES = [
#         ('draft', 'Draft'),
#         ('published', 'Published'),
#     ]
#     dish_name = models.CharField(max_length=100)
#     servings = models.PositiveIntegerField()
#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     modified_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    
#     # ingredients_digest = models.CharField(max_length=64, blank=True)
#     saved_to_my_recipes_by = models.ManyToManyField(
#         User,
#         through='MyRecipe',
#         related_name='my_recipes'
#     )

#     def __str__(self):
#         return f"{self.dish_name}"

#     class Meta:
#         ordering = ['-modified_at']
#         indexes = [
#             models.Index(fields=['created_by', 'created_at', 'status']),
#         ]

#     def get_scaled_recipe(self, new_servings: int) -> dict:
#         """Returns a complete scaled version of the recipe."""
#         scaled_ingredients = []
#         for ingredient in self.ingredients.all():
#             new_quantity, new_item = scale_quantity(
#                 ingredient.quantity,
#                 ingredient.item,
#                 self.servings,
#                 new_servings
#             )
#             scaled_ingredients.append({
#                 'quantity': new_quantity,
#                 'item': new_item,
#                 'order': ingredient.order
#             })
        
#         return {
#             'dish_name': self.dish_name,
#             'servings': new_servings,
#             'notes': self.notes,
#             'ingredients': scaled_ingredients,
#             'instruction_sections': self.instruction_sections.all(),
#         }

#     def scale_and_save(self, new_servings: int):
#         """Saves the recipe and permanently scales it to a new serving size."""
#         if new_servings != self.servings:
#             # Get scaled recipe data
#             scaled_recipe = self.get_scaled_recipe(new_servings)
            
#             # Batch all ingredient updates
#             ingredients_to_update = []
#             for ingredient in self.ingredients.all():
#                 # Find corresponding scaled ingredient
#                 scaled_ing = next(i for i in scaled_recipe['ingredients'] if i['order'] == ingredient.order)
#                 ingredient.quantity = scaled_ing['quantity']
#                 ingredients_to_update.append(ingredient)
            
#             # Bulk update ingredients without triggering individual saves
#             Ingredient.objects.bulk_update(ingredients_to_update, ['quantity'])
            
#             # Update servings and digest
#             self.servings = new_servings
#             self.update_ingredients_digest()
#             self.save()

#     def update_ingredients_digest(self):
#         """Create a digest of all ingredients data including servings count"""
#         ingredients_data = list(self.ingredients.order_by('order').values('item', 'quantity'))
#         data_string = json.dumps({
#             'servings': self.servings,
#             'ingredients': ingredients_data
#         }, sort_keys=True)
#         self.ingredients_digest = hashlib.sha256(data_string.encode()).hexdigest()
#         self.save(update_fields=['ingredients_digest'])

#     @receiver(post_save, sender='planner.Ingredient')
#     def update_recipe_digest(sender, instance, **kwargs):
#         instance.recipe.update_ingredients_digest()



#     # Shopping list models
# class ShoppingList(models.Model):
#     meal_plan = models.OneToOneField('MealPlan', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     modified_at = models.DateTimeField(auto_now=True)
#     content_digest = models.CharField(max_length=64, blank=True)  # SHA-256 hash

#     def update_content_digest(self):
#         # Collect all recipe digests and servings counts
#         digest_data = []
#         for group in self.meal_plan.groups.all():
#             for group_recipe in group.recipes.all():
#                 digest_data.append({
#                     'recipe_digest': group_recipe.recipe.ingredients_digest,
#                     'servings': group_recipe.servings
#                 })

#         # Create a digest of the entire shopping list state
#         data_string = json.dumps(digest_data, sort_keys=True)
#         self.content_digest = hashlib.sha256(data_string.encode()).hexdigest()
#         self.save(update_fields=['content_digest'])

#     def is_out_of_sync(self):
#         # Recalculate what the digest should be
#         old_digest = self.content_digest
#         self.update_content_digest()
#         return old_digest != self.content_digest


#     def __str__(self):
#         return f"Shopping List for {self.meal_plan.name}"


# # Recipe added to Meal Plan Group by user
# class MealPlanRecipe(models.Model):
#     meal_group = models.ForeignKey(MealGroup, related_name='recipes', on_delete=models.CASCADE)
#     recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT) # Prevent deletion of underlying recipe if it's used in a meal plan
#     modified_at = models.DateTimeField(auto_now=True)
#     order = models.PositiveIntegerField()

#     class Meta:
#         unique_together = ['order']
#         ordering = ['meal_group', 'order']

#     def __str__(self):
#         return f"{self.recipe.dish_name}"