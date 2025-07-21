# Add get_field_value template filter for dynamic field access
from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    return getattr(obj, field_name)
