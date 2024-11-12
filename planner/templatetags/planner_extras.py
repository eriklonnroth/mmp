import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(is_safe=True)
def json_script(value, element_id):
    """Serialize value as JSON and wrap it in a script tag."""
    json_str = json.dumps(value)
    return mark_safe(f'<script id="{element_id}" type="application/json">{json_str}</script>') 