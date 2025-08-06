
# butterfly_extras.py
# Custom template tags and filters for the butterflies app.
# Provides utility functions for use in Django templates.

from django import template
import re

register = template.Library()

# Utility filter to check if a string starts with a given substring
@register.filter
def startswith(text, starts):
    """Return True if text starts with the given substring."""
    if not text:
        return False
    return str(text).startswith(starts)
    
@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the key.
    Returns the value for a given key from a dictionary-like object.
    Usage: {{ request.GET|get_item:field.name }}
          {{ item.data|get_item:field }}
    """
    if dictionary is None:
        return ''
    return dictionary.get(key, '')

@register.filter
def get_field_value(obj, field_name):
    """
    Template filter to dynamically access a field value from a model instance.
    Usage in template: {{ object|get_field_value:"field_name" }}
    """
    return getattr(obj, field_name)

@register.filter
def split_semi(value):
    """Split a string by semicolons (with optional space) and return a list."""
    if not value:
        return []
    return [v.strip() for v in re.split(r';\s*', value) if v.strip()]

@register.filter
def contains(value, arg):
    """Check if a string contains a substring."""
    if not value:
        return False
    return str(value).lower().find(str(arg).lower()) != -1

@register.filter
def attr(value, attrs):
    """
    Adds HTML attributes to a form widget.
    Usage: {{ form.field|attr:"data-field-type:value,class:special-input" }}
    """
    if not attrs:
        return value
    
    attrs_dict = {}
    for attr_pair in attrs.split(','):
        if ':' in attr_pair:
            key, val = attr_pair.split(':')
            attrs_dict[key.strip()] = val.strip()
    
    if hasattr(value, 'field') and hasattr(value, 'as_widget'):
        return value.as_widget(attrs=attrs_dict)
    return value
    return str(arg).lower() in str(value).lower()
