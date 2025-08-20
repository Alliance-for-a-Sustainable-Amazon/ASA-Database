
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
                    if field == 'specimenNumber' and obj.catalogNumber:
                        # Format specimen number with highlight if it's the primary key field
                        if value:
                            return format_html('<span style="font-weight: bold;">{}</span>', value)
                        return format_html('<span style="font-weight: bold;">.</span>')
                    return dot_if_none(value)
                display_method.__name__ = f"display_{field}"
                
                # Get field object to use its help_text as tooltip
                field_obj = None
                try:
                    field_obj = obj._meta.get_field(field)
                    if hasattr(field_obj, 'help_text') and field_obj.help_text:
                        display_method.help_text = field_obj.help_text
                except:
                    pass
                
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
    list_filter = ['country', 'region', 'province']
    list_display_links = ['display_localityCode']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate list_display based on model fields
        field_names = [field.name for field in Locality._meta.fields]
        self.list_display = self._get_list_display_custom(field_names)
        
    def get_list_display_links(self, request, list_display):
        """Make the localityCode the clickable link field"""
        return ['display_localityCode']

@admin.register(Initials)
class InitialsAdmin(DotForNoneModelAdmin):
    search_fields = ['initials', 'name']
    list_filter = ['relationshipOrTitle', 'yearAndTerm']
    list_display_links = ['display_initials']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate list_display based on model fields
        field_names = [field.name for field in Initials._meta.fields]
        self.list_display = self._get_list_display_custom(field_names)
        
    def get_list_display_links(self, request, list_display):
        """Make the initials the clickable link field"""
        return ['display_initials']

@admin.register(Specimen)
class SpecimenAdmin(DotForNoneModelAdmin):
    search_fields = ['specimenNumber', 'catalogNumber']
    list_filter = ['sex', 'locality', 'recordedBy', 'year']
    list_display_links = ['display_specimenNumber']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically generate list_display based on model fields
        # Use a subset of fields for specimens since there are many fields
        field_names = [
            'specimenNumber', 'catalogNumber', 'recordedBy', 'sex',
            'locality', 'year', 'family', 'genus', 'specificEpithet'
        ]
        self.list_display = self._get_list_display_custom(field_names)
    
    def get_list_display_links(self, request, list_display):
        """Make the specimenNumber the clickable link field instead of catalogNumber"""
        return ['display_specimenNumber']
        
    def display_specimenNumber(self, obj):
        """Custom display method to highlight specimenNumber as the visual primary key"""
        if obj.specimenNumber:
            return format_html('<strong style="color: #447e9b;">{}</strong>', obj.specimenNumber)
        return format_html('<strong style="color: #447e9b;">.</strong>')
    display_specimenNumber.short_description = "Specimen Number"
    display_specimenNumber.admin_order_field = 'specimenNumber'
