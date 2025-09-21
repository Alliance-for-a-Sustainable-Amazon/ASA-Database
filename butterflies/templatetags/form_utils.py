"""
Template filters for handling GET parameters in templates.
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get(dictionary, key):
    """
    Gets a value from a dictionary by key.
    
    Args:
        dictionary: Dictionary object (like request.GET)
        key: Key to look up
        
    Returns:
        Value from dictionary or empty string
    """
    return dictionary.get(key, '')
