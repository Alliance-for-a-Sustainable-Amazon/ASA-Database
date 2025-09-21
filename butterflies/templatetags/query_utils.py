"""
Template tags for query string manipulation.
"""

from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    """
    Returns the URL-encoded querystring for the current page, 
    updated with the provided keyword arguments.
    
    Args:
        request: Django request object
        **kwargs: Key-value pairs to update in the query string
        
    Returns:
        str: Updated URL-encoded query string
    """
    updated = request.GET.copy()
    
    for key, value in kwargs.items():
        updated[key] = value
            
    return updated.urlencode()

@register.simple_tag
def update_query_param(query_dict, key, value):
    """
    Update a query parameter in the query string.
    
    Args:
        query_dict: The query dictionary (e.g., request.GET)
        key: The parameter to update
        value: The new value
        
    Returns:
        String: The updated query string
    """
    # Convert to mutable QueryDict
    updated_dict = query_dict.copy()
    updated_dict[key] = value
    
    return urlencode(updated_dict, doseq=True)

@register.simple_tag
def remove_query_param(query_dict, key):
    """
    Remove a query parameter from the query string.
    
    Args:
        query_dict: The query dictionary (e.g., request.GET)
        key: The parameter to remove
        
    Returns:
        String: The updated query string
    """
    # Convert to mutable QueryDict
    updated_dict = query_dict.copy()
    if key in updated_dict:
        del updated_dict[key]
    
    return urlencode(updated_dict, doseq=True)

@register.simple_tag
def preserve_query_params(query_dict, *exclude_args):
    """
    Generate hidden inputs for all query parameters except those specified.
    
    Args:
        query_dict: The query dictionary (e.g., request.GET)
        *exclude_args: Keys to exclude from the hidden inputs. Can be individual strings
                      or lists/tuples of strings.
        
    Returns:
        String: HTML with hidden inputs for all preserved query parameters
    """
    # Process exclude_args and flatten any lists into individual items
    exclude_set = set()
    for arg in exclude_args:
        if isinstance(arg, (list, tuple)):
            # If it's a list or tuple, add each item to the exclude set
            for item in arg:
                exclude_set.add(item)
        else:
            # Otherwise add the single item
            exclude_set.add(arg)
    
    hidden_inputs = []
    for key, value_list in query_dict.lists():
        if key not in exclude_set:
            for value in value_list:
                hidden_inputs.append(f'<input type="hidden" name="{key}" value="{value}">')
    
    return '\n'.join(hidden_inputs)

@register.filter
def get_query_string(query_dict, exclude_keys=None):
    """
    Generate a query string from a dictionary, optionally excluding specific keys.
    
    Args:
        query_dict: The query dictionary (e.g., request.GET)
        exclude_keys: Optional comma-separated list of keys to exclude
        
    Returns:
        String: The query string
    """
    updated_dict = query_dict.copy()
    
    if exclude_keys:
        for key in exclude_keys.split(','):
            key = key.strip()
            if key in updated_dict:
                del updated_dict[key]
    
    return urlencode(updated_dict, doseq=True)
