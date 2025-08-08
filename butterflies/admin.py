
# admin.py
# Registers models with the Django admin site and customizes their display and search options.

from django.contrib import admin
from django.contrib.admin.helpers import AdminReadonlyField
from django.utils.html import format_html
from .models import Specimen, Locality, Initials
from .utils import dot_if_none

# Custom ModelAdmin that displays periods instead of None
class DotForNoneModelAdmin(admin.ModelAdmin):
    """
    A ModelAdmin that displays periods instead of None values in all table views.
    """
    
    def _get_list_display_custom(self, model_fields):
        """Generate dynamic methods for each field to display dot if None"""
        display_methods = []
        
        for field_name in model_fields:
            # Define a function that returns the field value or dot if None
            def make_display_method(field):
                def display_method(self, obj):
                    value = getattr(obj, field, None)
                    return dot_if_none(value)
                display_method.__name__ = f"display_{field}"
                display_method.short_description = field.replace('_', ' ').title()
                display_method.admin_order_field = field  # Allow sorting by this field
                return display_method
                
            method_name = f"display_{field_name}"
            setattr(DotForNoneModelAdmin, method_name, make_display_method(field_name))
            display_methods.append(method_name)
            
        return display_methods


@admin.register(Locality)
class LocalityAdmin(DotForNoneModelAdmin):
    search_fields = ['localityCode', 'siteName', 'siteDescription', 'habitat']
    list_filter = ['localityCode', 'country']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate list_display based on model fields
        field_names = [field.name for field in Locality._meta.fields]
        self.list_display = self._get_list_display_custom(field_names)

@admin.register(Initials)
class InitialsAdmin(DotForNoneModelAdmin):
    search_fields = ['initials', 'name']
    list_filter = ['initials']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate list_display based on model fields
        field_names = [field.name for field in Initials._meta.fields]
        self.list_display = self._get_list_display_custom(field_names)

@admin.register(Specimen)
class SpecimenAdmin(DotForNoneModelAdmin):
    search_fields = ['specimenNumber', 'catalogNumber']
    list_filter = ['uploaded_iNaturalist', 'sex', 'locality', 'recordedBy']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate list_display based on model fields
        # Use a subset of fields for specimens since there are many fields
        field_names = [
            'id', 'specimenNumber', 'catalogNumber', 'recordedBy', 'sex',
            'locality', 'family', 'genus', 'specificEpithet'
        ]
        self.list_display = self._get_list_display_custom(field_names)
