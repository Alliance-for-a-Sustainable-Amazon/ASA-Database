"""
Template tags for filtering functionality in the butterflies app.

These tags help with rendering filter inputs, applying proper classes,
and showing helpful hints for filter usage.
"""

from django import template

register = template.Library()

@register.simple_tag
def filter_field_info(field_name):
    """
    Returns filter field configuration and help text.
    
    Args:
        field_name: Name of the field to get info for
        
    Returns:
        dict: Field filter configuration
    """
    # Special filter configurations with help text
    special_filters = {
        'year': {
            'placeholder': 'e.g., 2023, 2020:2025',
            'help_text': 'Enter single year, range (2020:2025), or comma-separated values',
            'special_class': 'special-filter',
            'range_support': True
        },
        'specimenNumber': {
            'placeholder': 'e.g., 1, 5:10',
            'help_text': 'Enter single number, range (1:100), or comma-separated values',
            'special_class': 'special-filter',
            'range_support': True
        },
        'catalogNumber': {
            'placeholder': 'e.g., 2023-FLP-0001',
            'help_text': 'Enter catalog number or range (2023-FLP-0001:0010)',
            'special_class': 'special-filter',
            'range_support': True
        },
        'locality': {
            'placeholder': 'e.g., FLP, KL',
            'help_text': 'Enter locality code(s), comma-separated',
            'special_class': 'special-filter',
            'range_support': False
        }
    }
    
    # Default configuration for regular fields
    default_config = {
        'placeholder': f'Filter by {field_name}',
        'help_text': 'Enter search term',
        'special_class': '',
        'range_support': False
    }
    
    return special_filters.get(field_name, default_config)

@register.filter
def is_special_filter(field_name):
    """
    Returns whether a field has special filter handling.
    
    Args:
        field_name: Name of the field to check
        
    Returns:
        bool: True if it's a special filter field
    """
    special_filters = ['year', 'specimenNumber', 'catalogNumber', 'locality']
    return field_name in special_filters
