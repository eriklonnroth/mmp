import re
from fractions import Fraction
from django.template.defaultfilters import pluralize


def is_close_to_one(value: float) -> bool:
    """Check if a number is effectively one (handles floating point imprecision)."""
    return abs(value - 1.0) < 0.1

def scale_quantity(quantity: str, name: str, original_servings: int, new_servings: int) -> tuple[str, str]:
    """Scale a quantity and handle pluralization using Django's pluralize."""
    ratio = new_servings / original_servings
    pattern = r'(\d+(?:\.\d+)?|\d+/\d+|\d+\s+\d+/\d+)'
    
    def convert_to_new_quantity(match):
        original = match.group(0)
        
        if ' ' in original:  # mixed number like "2 1/2"
            whole, frac = original.split()
            value = float(whole) + float(Fraction(frac))
        elif '/' in original:  # fraction like "1/2"
            value = float(Fraction(original))
        else:  # decimal or integer
            value = float(original)
            
        new_value = value * ratio
        
        if new_value.is_integer():
            return str(int(new_value))
        elif new_value * 2 == int(new_value * 2):
            return str(Fraction(new_value).limit_denominator(8))
        else:
            return f"{new_value:.1f}".rstrip('0').rstrip('.')
    
    new_quantity = re.sub(pattern, convert_to_new_quantity, quantity)
    
    # Get the numeric value for pluralization check
    match = re.search(pattern, new_quantity)
    if match:
        value = float(Fraction(match.group(0)) if '/' in match.group(0) else match.group(0))
        # Add 's' to quantity units if needed
        words = new_quantity.split()
        if len(words) > 1:  # Has units like "cups", "tablespoons"
            words[1] = words[1] + pluralize(value)
            new_quantity = ' '.join(words)
        # Pluralize the name if needed
        new_name = name + pluralize(value)
        return new_quantity, new_name
    
    return new_quantity, name