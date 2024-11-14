from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, url_name, section=None):
    """
    Determines if the current page matches the given URL name and optional section.
    Returns appropriate Tailwind classes.
    
    Usage:
    {% is_active 'recipes' %}
    {% is_active 'recipes' 'browse' %}
    """
    request = context['request']
    current_url_name = request.resolver_match.url_name
    current_section = request.GET.get('section')
    
    is_active = current_url_name == url_name
    if section and current_section:
        is_active = is_active and current_section == section
        
    if is_active:
        return 'border-indigo-500 text-gray-900'
    return 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
