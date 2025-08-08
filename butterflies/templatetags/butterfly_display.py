from django import template
from ..utils import dot_if_none as utils_dot_if_none

register = template.Library()

@register.filter(name='dot_if_none')
def dot_if_none_filter(value, use_dot=True):
    """
    Returns a period (.) if the value is None, empty string, or "None" string.
    Otherwise returns the original value.
    
    Args:
        value: The value to check
        use_dot: Boolean indicating whether to return a dot (True) or empty string (False)
                 for empty values. Default is True.
    
    Usage: 
        {{ value|dot_if_none }}           # Returns "." for empty values
        {{ value|dot_if_none:False }}     # Returns "" for empty values
    """
    if use_dot:
        return utils_dot_if_none(value)
    elif value is None or value == "" or value == "None":
        return ""
    return value
