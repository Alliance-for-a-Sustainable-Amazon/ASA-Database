
"""
Utilities for display formatting and common functions in the butterflies app.
"""
from django.http import Http404

def dot_if_none(value, use_dot=True):
    """
    Returns a period (.) if the value is None, empty string, or "None" string.
    Otherwise returns the original value.
    Args:
        value: The value to check
        use_dot: Boolean indicating whether to return a dot (True) or empty string (False)
                 for empty values. Default is True.
    """
    if value is None or value == "" or value == "None":
        return "." if use_dot else ""
    return value

def str_with_dots(func):
    """
    Decorator for __str__ methods to display periods instead of None or empty values.
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return dot_if_none(result)
    return wrapper
