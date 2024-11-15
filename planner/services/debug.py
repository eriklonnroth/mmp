import os
import sys
import importlib.util

# Print current working directory
print("Current working directory:", os.getcwd())

# Print Python path
print("\nPython is looking for modules in these directories:")
for path in sys.path:
    print(f"- {path}")
    # Check if 'planner' exists in this path
    potential_planner = os.path.join(path, 'planner')
    if os.path.exists(potential_planner):
        print(f"  Found 'planner' here! Contains these files:")
        for item in os.listdir(potential_planner):
            print(f"    - {item}")

# Try to find the specific module
print("\nTrying to find planner.models specifically:")
try:
    spec = importlib.util.find_spec("planner.models")
    if spec:
        print(f"Found at: {spec.origin}")
    else:
        print("Could not find planner.models")
except Exception as e:
    print(f"Error while looking: {e}")

# Try the import
print("\nTrying import:")
try:
    from planner.models import ShoppingCategory
except ModuleNotFoundError as e:
    print(f"Import error: {e}")
    print(f"Error type: {type(e)}")