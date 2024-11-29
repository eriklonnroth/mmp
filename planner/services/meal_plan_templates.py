TEMPLATES = {
    'weekday': {
        'name': 'Weekday',
        'description': 'Organise meals by day of the week',
        'meal_groups': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    },
    'meal_type': {
        'name': 'Meal Type',
        'description': 'Organise meals by type: breakfasts, lunches, dinners, snacks',
        'meal_groups': ['Breakfasts', 'Lunches', 'Dinners', 'Snacks']
    },
    'blank': {
        'name': 'Blank',
        'description': 'Start with a blank plan and add your own meal groups',
        'meal_groups': []
    }
}

# Helper functions
def get_all_templates():
    return list(TEMPLATES.keys())
    
def get_template_name(template):
    return TEMPLATES[template]['name']

def get_description(template):
    return TEMPLATES[template]['description']
    
def get_default_meal_groups(template):
    return TEMPLATES[template]['meal_groups']
            
 