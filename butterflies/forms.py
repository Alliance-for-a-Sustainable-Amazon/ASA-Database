# forms.py
# Defines Django ModelForm classes for butterfly collections with fields organized into logical groups.
# This is the consolidated forms file that uses the organized form layout for all forms.

from django import forms
from django.utils.functional import cached_property
from .models import Initials, Locality, Specimen
from datetime import time
import re

# Custom 24-hour time input widget
class MilitaryTimeInput(forms.TextInput):
    """
    A custom widget for entering time in 24-hour format or time ranges.
    This widget allows more flexible time formats, including ranges like "14:00-16:30".
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'placeholder': 'HH:MM or HH:MM-HH:MM', 
            'class': 'military-time-input',
            # Remove pattern restriction to allow time ranges
            'maxlength': '15'  # Allow for time ranges (e.g., "14:00-16:30")
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        """Format the time value - return as is since we now support ranges"""
        if isinstance(value, time):
            return value.strftime('%H:%M')
        return value or ''
    
    def value_from_datadict(self, data, files, name):
        """Extract the time value from the form data without strict validation"""
        value = super().value_from_datadict(data, files, name)
        if not value:
            return None
            
        # No validation - just return the value as entered
        return value

# Constants for reusable choices
DAY_CHOICES = [('', 'Day')] + [(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 32)]
MONTH_CHOICES_NAMED = [
    ('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'),
    ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'),
    ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')
]
MONTH_CHOICES_NUMERIC = [('', 'Month')] + [(str(m).zfill(2), str(m).zfill(2)) for m in range(1, 13)]
YEAR_CHOICES = [('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)]
BOOLEAN_CHOICES = [('', ''), ('TRUE', 'TRUE'), ('FALSE', 'FALSE')]

# --- Forms for Biological Specimen Database ---
class InitialsForm(forms.ModelForm):
    class Meta:
        model = Initials
        fields = '__all__'

class LocalityForm(forms.ModelForm):
    class Meta:
        model = Locality
        fields = '__all__'

# Organized SpecimenForm with fields grouped by category and ordered exactly as specified
def create_textarea_field(max_length=500, label=None, required=False):
    """Helper function to create a consistent textarea field"""
    return forms.CharField(
        max_length=max_length,
        required=required,
        label=label,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'textarea-field',
            'style': 'width: 100%; min-height: 80px;'
        })
    )

def compile_date_components(cleaned_data, day_field, month_field, year_field, format_type="iso"):
    """
    Helper function to compile date components into a single string
    format_type: "iso" (YYYY-MM-DD) or "human" (DD Month YYYY)
    
    This function simply concatenates the components without complex formatting or conversion.
    It preserves the original dropdown values exactly as selected by the user.
    """
    day = cleaned_data.get(day_field)
    month = cleaned_data.get(month_field)
    year = cleaned_data.get(year_field)
    
    if not (day and month and year):
        return None
    
    if format_type == "iso":
        # Simple concatenation for ISO-like format
        return f"{year}-{month}-{day}"
    else:  # human format
        return f"{day} {month}, {year}"

def compile_log_entry(cleaned_data, day_field, month_field, year_field, 
                      initials_field, description_field):
    """Helper function to create a log entry from components"""
    day = cleaned_data.get(day_field)
    month = cleaned_data.get(month_field)
    year = cleaned_data.get(year_field)
    initials = cleaned_data.get(initials_field)
    description = cleaned_data.get(description_field)
    
    if not (day and month and year and initials and description):
        return None
        
    return f"{day} {month} {year}, {initials}, {description}".strip()

class SpecimenForm(forms.ModelForm):
    # ----------------------------------
    # 1. Record-level Fields
    # ----------------------------------
    # 1. modified field
    mod_day = forms.ChoiceField(
        choices=DAY_CHOICES,
        required=False,
        label="Modified Day"
    )
    mod_month = forms.ChoiceField(
        choices=MONTH_CHOICES_NAMED,
        required=False,
        label="Modified Month"
    )
    mod_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        label="Modified Year"
    )
    mod_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Modified Initials"
    )
    mod_description = forms.CharField(
        max_length=255,
        required=False,
        label="Modification Description"
    )
    
    # ----------------------------------
    # 3. Occurrence Fields - Disposition Mini-fields (not part of model)
    # ----------------------------------
    disp_day = forms.ChoiceField(
        choices=DAY_CHOICES,
        required=False,
        label="Disposition Day"
    )
    disp_month = forms.ChoiceField(
        choices=MONTH_CHOICES_NAMED,
        required=False,
        label="Disposition Month"
    )
    disp_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        label="Disposition Year"
    )
    disp_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Disposition Initials"
    )
    disp_description = forms.CharField(
        max_length=255,
        required=False,
        label="Disposition Description"
    )

    # ----------------------------------
    # 2. Location Fields
    # ----------------------------------
    # 2. locality
    locality = forms.ModelChoiceField(
        queryset=Locality.objects.all(),
        required=False,
        label="Locality"
    )
    # 3. decimalLatitude
    decimalLatitude = forms.CharField(
        max_length=20,
        required=False,
        label="Decimal Latitude"
    )
    
    # 4. decimalLongitude
    decimalLongitude = forms.CharField(
        max_length=20,
        required=False,
        label="Decimal Longitude"
    )
    
    # 5. exact_loc?
    exact_loc = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        required=False,
        label="Exact Location?"
    )
    # 6. coordinateUncertaintyInMeters
    coordinateUncertaintyInMeters = forms.CharField(
        max_length=100,
        required=False,
        label="Coordinate Uncertainty (meters)"
    )
    
    # 7. georeferencedBy
    georeferencedBy = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Georeferenced By"
    )
    
    # 8. georeferencedDate
    georef_day = forms.ChoiceField(
        choices=DAY_CHOICES,
        required=False,
        label="Georeferenced Day"
    )
    georef_month = forms.ChoiceField(
        choices=MONTH_CHOICES_NAMED,
        required=False,
        label="Georeferenced Month"
    )
    georef_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        label="Georeferenced Year"
    )
    
    # 9. georeferenceProtocol
    georeferenceProtocol = create_textarea_field(
        label="Georeference Protocol"
    )
    
    # 10. minimumElevationInMeters
    minimumElevationInMeters = forms.CharField(
        max_length=20,
        required=False,
        label="Minimum Elevation (meters)"
    )
    
    # 11. maximumElevationInMeters
    maximumElevationInMeters = forms.CharField(
        max_length=20,
        required=False,
        label="Maximum Elevation (meters)"
    )
    
    # No longer using mini-fields for LocalityDescriptionNotes

    # ----------------------------------
    # 3. Occurrence Fields
    # ----------------------------------
    # 12. specimenNumber
    specimenNumber = forms.CharField(
        max_length=100,
        required=False,
        label="Specimen Number"
    )
    
    # Field not in numbered list but needed for functionality
    catalogNumber = forms.CharField(
        max_length=100,
        required=False,
        label="Catalog Number"
    )
    
    # 13. recordedBy
    recordedBy = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Recorded By"
    )
    
    # 14. sex
    sex = forms.ChoiceField(
        choices=[('', ''), ('male', 'male'), ('female', 'female'), ('.', '.')],
        required=False,
        label="Sex"
    )
    
    # 15. behavior
    behavior = create_textarea_field(
        label="Behavior"
    )
    
    # 16. occurrenceRemarks
    occurrenceRemarks = create_textarea_field(
        label="Occurrence Remarks"
    )

    # ----------------------------------
    # 4. Event Fields
    # ----------------------------------
    # 18. year
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        label="Year"
    )
    # 19. month - using a custom widget to display named months but store as is
    month = forms.ChoiceField(
        choices=MONTH_CHOICES_NAMED,
        required=False,
        label="Month",
        widget=forms.Select(attrs={
            'class': 'month-field',
        })
    )
    
    # 20. day
    day = forms.ChoiceField(
        choices=DAY_CHOICES,
        required=False,
        label="Day"
    )
    
    # 21. eventTime (using 24-hour format with custom widget, now supporting ranges)
    eventTime = forms.CharField(
        required=False,
        label="Event Time",
        max_length=15,
        widget=MilitaryTimeInput(),
        help_text="Use 24-hour format. Can be a single time (14:30) or time range (14:00-16:30)"
    )
    
    # Not using separate EventDate mini-fields anymore - using main date fields instead
    
    # 22. habitatNotes
    habitatNotes = create_textarea_field(
        label="Habitat Notes"
    )
    
    # 23. samplingProtocol
    samplingProtocol = create_textarea_field(
        label="Sampling Protocol"
    )

    # ----------------------------------
    # 5. Taxon Fields
    # ----------------------------------
    # 24. family
    family = forms.CharField(
        max_length=100,
        required=False,
        label="Family"
    )
    # 25. subfamily
    subfamily = forms.CharField(
        max_length=100,
        required=False,
        label="Subfamily"
    )
    
    # 26. tribe
    tribe = forms.CharField(
        max_length=100,
        required=False,
        label="Tribe"
    )
    
    # 27. subtribe
    subtribe = forms.CharField(
        max_length=100,
        required=False,
        label="Subtribe"
    )
    
    # 28. genus
    genus = forms.CharField(
        max_length=100,
        required=False,
        label="Genus"
    )
    
    # 29. specificEpithet
    specificEpithet = forms.CharField(
        max_length=100,
        required=False,
        label="Specific Epithet"
    )
    
    # 30. infraspecificEpithet
    infraspecificEpithet = forms.CharField(
        max_length=100,
        required=False,
        label="Infraspecific Epithet"
    )

    # ----------------------------------
    # 6. Identification Fields
    # ----------------------------------
    # 31. identifiedBy
    identifiedBy = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Identified By"
    )
    
    # 32. dateIdentified - split into separate day/month/year fields
    dateIdentified_day = forms.ChoiceField(
        choices=DAY_CHOICES,
        required=False,
        label="Date Identified Day"
    )
    dateIdentified_month = forms.ChoiceField(
        choices=MONTH_CHOICES_NAMED,
        required=False,
        label="Date Identified Month"
    )
    dateIdentified_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        label="Date Identified Year"
    )
    
    # 33. identificationReferences
    identificationReferences = create_textarea_field(
        label="Identification References"
    )
    
    # 34. identificationRemarks
    identificationRemarks = create_textarea_field(
        label="Identification Remarks"
    )

    class Meta:
        model = Specimen
        exclude = [
            'modified', 'disposition',  
            'eventDate', 'georeferencedDate', 'dateIdentified', 'month'
            # We exclude 'month' to handle it specially in clean_month and save methods
            # We handle these dates through our custom form fields
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make catalogNumber field disabled and styled for display only
        if 'catalogNumber' in self.fields:
            self.fields['catalogNumber'].disabled = True
            self.fields['catalogNumber'].widget.attrs.update({
                'style': 'background-color: #eee; color: #888;',
                'placeholder': '(auto generated)'
            })
        
        # Define field groups
        field_groups = {
            'date_fields': [
                # All day/month/year field components
                'mod_day', 'mod_month', 'mod_year',
                'georef_day', 'georef_month', 'georef_year',
                'disp_day', 'disp_month', 'disp_year',
                'year', 'month', 'day',
                'dateIdentified_day', 'dateIdentified_month', 'dateIdentified_year',
            ],
            'textarea_fields': [
                'georeferenceProtocol', 'behavior', 'occurrenceRemarks',
                'habitatNotes', 'samplingProtocol', 
                'identificationReferences', 'identificationRemarks'
            ]
        }
        
        # Apply Select2 to all date fields
        for field_name in field_groups['date_fields']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'select2'
                
        # Add any additional attributes for textarea fields if needed
        for field_name in field_groups['textarea_fields']:
            if field_name in self.fields:
                # Nothing additional needed here as we already set attributes in create_textarea_field
                pass
    
    def clean_eventTime(self):
        """
        Specific clean method for eventTime field to save it as-is without conversion.
        This allows for flexible time formats including ranges like "14:00-16:30".
        """
        time_value = self.cleaned_data.get('eventTime')
        # Simply return the value as entered by the user without any validation or conversion
        # This permits both single times and time ranges
        return time_value
        
    def clean(self):
        """
        Clean all form fields at once
        This allows us to handle interdependent fields correctly
        """
        cleaned_data = super().clean()
        # No special event date processing needed anymore
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # ----------------------------------
        # 1. Record-level Fields (1)
        # ----------------------------------
        # Append-only logic for modified
        entry = compile_log_entry(
            self.cleaned_data, 'mod_day', 'mod_month', 'mod_year', 
            'mod_initials', 'mod_description'
        )
        if entry:
            if instance.modified:
                instance.modified = f"{instance.modified}; {entry}"
            else:
                instance.modified = entry
        
        # ----------------------------------
        # 2. Location Fields (2-11)
        # ----------------------------------
        # Process georeferencedDate as Python date object
        georef_day = self.cleaned_data.get('georef_day')
        georef_month = self.cleaned_data.get('georef_month') 
        georef_year = self.cleaned_data.get('georef_year')
        
        if georef_day and georef_month and georef_year:
            # Convert to a proper Python date object
            try:
                date_str = f"{georef_day} {georef_month}, {georef_year}"
                from butterflies.views import parse_date_value
                instance.georeferencedDate = parse_date_value(date_str)
            except Exception as e:
                import logging
                logging.error(f"Failed to convert georeferencedDate: {str(e)}")
            
        # georeferenceProtocol is now directly handled by the model field
        # No special processing needed as it's a direct text input
        # No longer using append-only logic for localityDescriptionNotes
        
        # ----------------------------------
        # 3. Occurrence Fields (12-17)
        # ----------------------------------
        # Append-only logic for disposition
        entry = compile_log_entry(
            self.cleaned_data, 'disp_day', 'disp_month', 'disp_year',
            'disp_initials', 'disp_description'
        )
        if entry:
            if instance.disposition:
                instance.disposition = f"{instance.disposition}; {entry}"
            else:
                instance.disposition = entry
        
        # behavior and occurrenceRemarks are now directly handled by the model fields
        # No special processing needed as they're direct text inputs
        
        # ----------------------------------
        # 4. Event Fields (18-23)
        # ----------------------------------
        # Set the month field directly from the dropdown value without any conversion
        month_value = self.cleaned_data.get('month')
        if month_value:
            # Store month exactly as selected from dropdown
            instance.month = month_value
            
        # Create eventDate from the day, month, year fields
        day_value = self.cleaned_data.get('day')
        month_value = self.cleaned_data.get('month')
        year_value = self.cleaned_data.get('year')
        if day_value and month_value and year_value:
            # Convert to a proper Python date object
            try:
                date_str = f"{day_value} {month_value}, {year_value}"
                from butterflies.views import parse_date_value
                instance.eventDate = parse_date_value(date_str)
            except Exception as e:
                import logging
                logging.error(f"Failed to convert eventDate: {str(e)}")
                
        # habitatNotes and samplingProtocol are now directly handled by the model fields
        # No special processing needed as they're direct text inputs
        
        # ----------------------------------
        # 5. Taxon Fields (24-30) - No special processing required
        # ----------------------------------
        
        # ----------------------------------
        # 6. Identification Fields (31-34)
        # ----------------------------------
        # Process dateIdentified as Python date object
        date_id_day = self.cleaned_data.get('dateIdentified_day')
        date_id_month = self.cleaned_data.get('dateIdentified_month')
        date_id_year = self.cleaned_data.get('dateIdentified_year')
        
        if date_id_day and date_id_month and date_id_year:
            # Convert to a proper Python date object
            try:
                date_str = f"{date_id_day} {date_id_month}, {date_id_year}"
                from butterflies.views import parse_date_value
                instance.dateIdentified = parse_date_value(date_str)
            except Exception as e:
                import logging
                logging.error(f"Failed to convert dateIdentified: {str(e)}")
            
        # identificationReferences and identificationRemarks are now directly handled by the model fields
        # No special processing needed as they're direct text inputs

        # No need for format validation or time conversion
        # All fields are saved as simple text without format enforcement
            
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SpecimenEditForm(SpecimenForm):
    """
    Form for editing existing Specimen records with special validation rules:
    1. By default, no fields are required
    2. If editing any field except in the 5. Taxon group and 6. Identification group, a new Modified entry is required
    3. If editing any 5. Taxon field, the 6. Identification group fields are required
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields non-required by default for editing
        for field_name, field in self.fields.items():
            field.required = False
            
        # Store the original field values to detect changes during validation
        if self.instance and self.instance.pk:
            self.initial_data = {
                field_name: getattr(self.instance, field_name, None) 
                for field_name in self.fields if hasattr(self.instance, field_name)
            }
            
    def clean(self):
        cleaned_data = super().clean()
        
        # Skip validation if this is a new instance (not editing)
        if not self.instance or not self.instance.pk:
            return cleaned_data
            
        # Define field groups
        taxon_fields = [
            'family', 'subfamily', 'tribe', 'subtribe', 
            'genus', 'specificEpithet', 'infraspecificEpithet'
        ]
        
        identification_fields = [
            'identifiedBy', 'dateIdentified_day', 'dateIdentified_month', 
            'dateIdentified_year', 'identificationReferences', 'identificationRemarks'
        ]
        
        # All fields that should be excluded from the "other changes" check
        excluded_from_other_changes = set(taxon_fields + identification_fields + ['catalogNumber'])
        
        # Check for changes in different field groups
        has_taxon_changes = any(
            field in cleaned_data and cleaned_data[field] != self.initial_data.get(field)
            for field in taxon_fields if field in cleaned_data
        )
        
        # Check for changes in fields that are NOT taxon or identification fields
        # Only check fields that actually exist on the model instance
        has_other_changes = any(
            field in cleaned_data and field not in excluded_from_other_changes and
            hasattr(self.instance, field) and
            cleaned_data[field] != self.initial_data.get(field)
            for field in cleaned_data
        )
        
        # Rule B: If editing any field except Taxon and Identification groups, require Modified entry
        if has_other_changes:
            mod_day = cleaned_data.get('mod_day')
            mod_month = cleaned_data.get('mod_month')
            mod_year = cleaned_data.get('mod_year')
            mod_initials = cleaned_data.get('mod_initials')
            mod_description = cleaned_data.get('mod_description')
            
            if not (mod_day and mod_month and mod_year and mod_initials and mod_description):
                self.add_error(None, "When editing fields outside the Taxon and Identification groups, "
                                    "you must add a new Modified entry with all fields (day, month, year, "
                                    "initials, and description).")
        
        # Rule C: If editing any Taxon field, require Identification fields
        if has_taxon_changes:
            identified_by = cleaned_data.get('identifiedBy')
            date_id_day = cleaned_data.get('dateIdentified_day')
            date_id_month = cleaned_data.get('dateIdentified_month')
            date_id_year = cleaned_data.get('dateIdentified_year')
            
            if not (identified_by and date_id_day and date_id_month and date_id_year):
                self.add_error(None, "When editing Taxon fields, you must provide Identification information "
                                    "(Identified By and Date Identified).")
        
        return cleaned_data
