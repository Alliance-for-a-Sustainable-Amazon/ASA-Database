
# butterfly_extras.py
# Custom template tags and filters for the butterflies app.
# Provides utility functions for use in Django templates.

from django import template

register = template.Library()

# Utility filter to check if a string starts with a given substring
@register.filter
def startswith(text, starts):
    """Return True if text starts with the given substring."""
    if not text:
        return False
    return str(text).startswith(starts)

@register.filter
def get_field_value(obj, field_name):
    """
    Template filter to dynamically access a field value from a model instance.
    Usage in template: {{ object|get_field_value:"field_name" }}
    """
    return getattr(obj, field_name)


# Utility filter to get a value from a dict-like object by key (for request.GET)
@register.filter
def get_item(dictionary, key):
    """
    Returns the value for a given key from a dictionary-like object.
    Usage: {{ request.GET|get_item:field.name }}
    """
    return dictionary.get(key, '')

@register.filter
def split_semi(value):
    """Split a string by semicolons and return a list."""
    if not value:
        return []
    return [v.strip() for v in value.split('; ') if v.strip()]
