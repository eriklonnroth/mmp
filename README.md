
# User Journey
1. New user creates a profile with dietary preferences (e.g. "Household members: 3; Country: United Kingdom; Dietary preferences: vegetarian, peanut allergy, don't like onions")
2. User searches existing recipes from a database or uses Anthropic API to generate a new one based on input fields "name", "servings", and "notes", e.g.: "Recipe name: Chicken Korma, Servings: 3, Notes: not too spicy". This gets passed to the API along with the user profile data such as country and dietary preferences.
3. Recipe is generated, showing ingredients (a single table with item, quantity) and instructions (one or more sections, each containing steps). The data is received in JSON format for easy parsing and populating of the database.
4. User can edit the recipe then save it to My Recipes.
5. Repeat for more recipes, each time saving to My Recipes. Then, they can select recipes and Add to My Meal Plan.
6. My Meal Plan allows you to organise your recipes into a meal plan. First the user chooses what type of grouping to apply: by weekday (Monday-Sunday), by meal type (Breakfast, Lunch, Dinner, Snacks) or Custom (user can add groups and name them). After selecting which groupings to apply, recipes can be added to a given group (e.g. Monday in the weekday grouping). Recipe names are in the format "Mild Chicken Korma (for 3)", "Chicken Tikka Masala (for 4)", "Easy lentil salad (for 2)".
7. When the user is done organising recipes into groups, they click Save Meal Plan. That allows them retrieve it later from My Meal Plans. Once they're happy with a meal plan, they click Generate Shopping List. This sends another request to Anthropic API with all the recipes in My Meal Plan as a JSON, requesting that ingredients be combined into a shopping list suitable for the super market. e.g. if two recipes call for 3 garlic cloves each, these are added together into "1 head of garlic" rather than "6 garlic cloves", and small recipe quantities such as "2 tbsp garam masala" are turned into a suitable shopping quantity such as "1 pack garam masala".
8. The Shopping List is generated, populating a table with headings item, quantity, and notes (e.g. suitable substitutes). A checkbox column is also added, allowing the user to tick off items that they already have (this greys out the row in the shopping list). The full list can be copied to clipboard so the user can paste it into an other app.