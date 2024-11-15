from pathlib import Path
from planner.services.recipe_parser import parse_recipe_file

def test_korma_recipe():
    # Get the absolute path to the recipe file
    recipe_path = Path(__file__).parent.parent / 'static' / 'planner' / 'recipes' / 'korma.json'
    
    try:
        # Parse and save the recipe
        recipe = parse_recipe_file(recipe_path)
        
        # Print basic validation
        print(f"\nRecipe parsed successfully!")
        print(f"Name: {recipe.name}")
        print(f"Servings: {recipe.servings}")
        print(f"\nIngredients count: {recipe.ingredient_set.count()}")
        print(f"First 3 ingredients:")
        for ing in recipe.ingredient_set.all()[:3]:
            print(f"- {ing.item}: {ing.quantity}")
            
        print(f"\nInstruction sections: {recipe.instructionsection_set.count()}")
        for section in recipe.instructionsection_set.all():
            print(f"\n{section.title}:")
            for step in section.instructionstep_set.all():
                print(f"{step.step_number}. {step.instruction[:50]}...")
                
    except Exception as e:
        print(f"Error parsing recipe: {e}")

if __name__ == "__main__":
    test_korma_recipe()