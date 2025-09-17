# views.py
# Consolidated view functions for butterfly collections using the organized form approach.
# All forms now use the organized layout for better usability.
#
# Date Handling Strategy:
# - In the database: Dates are stored as strings in format "DD Month, YYYY" (e.g. "15 November, 2025")
# - During input: Various formats are accepted and automatically converted using format_date_value()
# - During display: Dates are shown in their string representation directly from the database
# - During sorting/filtering: Dates are parsed to datetime objects using dateutil.parser
# - The format_date_value() function is the central point for date standardization

# --- Imports ---
from django.apps import apps
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.http import Http404, HttpResponse
from django.forms import modelform_factory
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import csv
import io
import openpyxl
import pandas as pd
import re
import datetime
from dateutil import parser as date_parser
from operator import itemgetter
# App-specific imports
from .models import Specimen, Locality, Initials
from .forms import SpecimenForm, SpecimenEditForm, LocalityForm, InitialsForm
from .utils import dot_if_none
from butterflies.utils.image_utils import get_specimen_image_urls
from .auth_utils import admin_required


# --- Utility Functions ---
def model_list():
    """
    Return all models in the butterflies app.
    """
    return list(apps.get_app_config('butterflies').get_models())

def parse_date_value(value):
    """
    Parse a value into a date object.
    This is the complement to format_date_value() - use this when you need a date object
    for calculations, sorting, or comparisons.
    
    Parameters:
        value: Date value in any format (string, date, datetime)
    Returns:
        date object or None if parsing fails
    """
    if not value:
        return None
        
    try:
        # If already a datetime, convert to date
        if isinstance(value, datetime.datetime):
            return value.date()
        
        # If it's already a date object, return it
        elif isinstance(value, datetime.date):
            return value
            
        # Try direct parsing of standard format first (for string values from user input)
        standard_pattern = r"^\d{1,2} [A-Za-z]+,? \d{4}$"
        if isinstance(value, str) and re.match(standard_pattern, value):
            # Try a few variations of our standard format
            for fmt in ["%d %B, %Y", "%d %B %Y"]:
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except:
                    continue
                    
        # Use dateutil's flexible parser as a fallback for strings
        if isinstance(value, str):
            return date_parser.parse(value).date()
        
        # If we get here with a non-string, non-date value, try to convert
        return datetime.datetime.fromisoformat(str(value)).date()
            
    except Exception as e:
        import logging
        logging.warning(f"Date parsing error for '{value}' ({type(value)}): {str(e)}")
        return None

def format_date_value(value):
    """
    Format a date value to the standardized string format: DD Month, YYYY.
    Handles datetime objects, date objects, strings, and pandas Timestamp objects.
    
    This is the central date formatting function for the entire application.
    All dates should pass through this function for standardization when displaying.
    
    Parameters:
        value: A date value in any format (datetime, date, string, Timestamp, etc.)
    Returns:
        String in format "DD Month, YYYY" or None if conversion fails
    """
    if pd.isna(value) or value is None or value == '':
        return None
    
    try:
        # Function to format date consistently across platforms
        def format_date(dt):
            # Use %d and strip leading zero instead of %-d which doesn't work on Windows
            day = dt.strftime("%d").lstrip("0")
            if day == "": day = "1"  # Handle case where day is "01"
            month = dt.strftime("%B")  # Full month name
            year = dt.strftime("%Y")   # 4-digit year
            return f"{day} {month}, {year}"
        
        # If value is already a datetime or date object
        if isinstance(value, (datetime.datetime, datetime.date)):
            return format_date(value)
        
        # If value is a pandas Timestamp
        elif hasattr(value, 'to_pydatetime'):
            return format_date(value.to_pydatetime())
            
        # If value is a string, try to parse it
        elif isinstance(value, str):
            # First check if it's already in the correct format (DD Month, YYYY)
            date_pattern = r"^\d{1,2} [A-Za-z]+\.?,? \d{4}$"
            if re.match(date_pattern, value):
                # It's already in the right format, but standardize to ensure consistency
                try:
                    dt = date_parser.parse(value)
                    return format_date(dt)
                except:
                    # If parsing fails, return the original as it's close enough
                    return value
                
            # Next check for ISO format (YYYY-MM-DD)
            iso_pattern = r"^\d{4}-\d{2}-\d{2}$"
            if re.match(iso_pattern, value):
                try:
                    dt = datetime.datetime.strptime(value, "%Y-%m-%d")
                    return format_date(dt)
                except:
                    pass
                
            # Check for DD-MMM-YYYY format (from help text)
            dmm_pattern = r"^\d{1,2}-[A-Za-z]{3,9}-\d{4}$"
            if re.match(dmm_pattern, value):
                try:
                    # Replace abbreviated month names with standard ones if needed
                    value = value.replace(".", "")  # Remove periods from abbreviated months
                    # Try various formats with different separators and month formats
                    for fmt in ["%d-%b-%Y", "%d-%B-%Y"]:
                        try:
                            dt = datetime.datetime.strptime(value, fmt)
                            return format_date(dt)
                        except:
                            pass
                except:
                    pass
                    
            # Try some common date formats
            common_formats = [
                "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",  # Slash formats
                "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y",  # Dot formats
                "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y",  # Word month formats
                "%Y%m%d"  # No separator format
            ]
            
            for fmt in common_formats:
                try:
                    dt = datetime.datetime.strptime(value, fmt)
                    return format_date(dt)
                except:
                    continue
            
            # Last resort: Try dateutil's flexible parser
            try:
                dt = date_parser.parse(value, dayfirst=False)  # default to MM/DD/YYYY
                return format_date(dt)
            except:
                # Try again with day first
                try:
                    dt = date_parser.parse(value, dayfirst=True)  # Try DD/MM/YYYY
                    return format_date(dt)
                except:
                    pass
                
    except Exception as e:
        import logging
        logging.warning(f"Date conversion error for value '{value}': {str(e)}")
        
    # If all conversions fail, return the original value if it's a string
    return str(value) if value is not None else None

# --- Generic CRUD Views ---
@login_required
def dynamic_list(request, model_name):
    """
    Generic dynamic list view for any model.
    Displays all objects for the specified model with filtering capabilities.
    Requires user authentication.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to list
    Returns:
        Rendered template with filtered objects
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
    objects = model.objects.all()
    fields = [
        {'name': field.name, 'verbose_name': getattr(field, 'verbose_name', field.name)}
        for field in model._meta.fields
        if field.name != 'id'
    ]
    # Multi-field search for each model
    for field in fields:
        value = request.GET.get(field['name'])
        if value:
            objects = objects.filter(**{f"{field['name']}__icontains": value})
    obj_list = []
    for obj in objects:
        obj.model_name_internal = model._meta.model_name
        obj_list.append(obj)
    # Check for import errors in session
    import_errors = None
    import_complete = request.session.get('import_complete', False)
    
    if import_complete:
        import_errors = request.session.get('import_errors', [])
        # Add a summary message if there are errors
        if import_errors and len(import_errors) > 0:
            messages.warning(request, f'There were {len(import_errors)} errors during import. See details below.')
        
        # Clear the session variables after retrieving them
        request.session['import_complete'] = False
        if 'import_errors' in request.session:
            del request.session['import_errors']
        
        # Make sure changes are saved to session
        request.session.modified = True
    
    return render(request, 'butterflies/dynamic_list.html', {
        'objects': obj_list,
        'fields': fields,
        'model_name': model._meta.verbose_name.title(),
        'model_name_internal': model._meta.model_name,
        'request': request,
        'home_url': 'report_table',
        'import_errors': import_errors,  # Pass import errors to the template
    })

def dynamic_detail(request, model_name, object_id):
    """
    Generic detail view for any model.
    Shows detailed information for a specific object.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model
        object_id: Primary key of the object to display
    Returns:
        Rendered template with object details
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
    try:
        obj = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        raise Http404("Object not found")
    fields = [
        {'name': field.name, 'verbose_name': getattr(field, 'verbose_name', field.name)}
        for field in model._meta.fields
        if field.name != 'id'
    ]
    obj.model_name_internal = model._meta.model_name
    # If specimen, add image URLs
    image_urls = None
    if model._meta.model_name == 'specimen':
        image_urls = get_specimen_image_urls(obj.catalogNumber)
    return render(request, 'butterflies/_detail.html', {
        'object': obj,
        'fields': fields,
        'model_name': model._meta.verbose_name.title(),
        'image_urls': image_urls,
    })

@admin_required
def dynamic_delete(request, model_name, object_id):
    """
    Generic delete view for any model.
    Shows confirmation page before deleting an object.
    Requires admin privileges.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model
        object_id: Primary key of the object to delete
    Returns:
        Redirect to report_table on successful deletion
        or confirmation template
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
    try:
        obj = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        raise Http404("Object not found")
    if request.method == 'POST':
        obj.delete()
        from django.urls import reverse
        return redirect(reverse('report_table'))
    obj.model_name_internal = model._meta.model_name
    return render(request, 'butterflies/_detail.html', {
        'object': obj,
        'fields': [
            {'name': field.name, 'verbose_name': getattr(field, 'verbose_name', field.name)}
            for field in model._meta.fields
            if field.name != 'id'
        ],
        'model_name': model._meta.verbose_name.title(),
        'delete_confirm': True,
    })

@login_required
def dynamic_create_edit(request, model_name, object_id=None):
    """
    Generic create/edit view for any model using the organized form approach.
    Uses the organized form template for Specimen model.
    Requires user authentication.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to create or edit
        object_id: Optional primary key for edit mode
    Returns:
        Rendered form template or redirect to report_table after save
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
    
    # Check if restricted model (locality or initials) and user has admin permissions
    if model._meta.model_name in ['locality', 'initials']:
        # Check if user is admin or superuser
        if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
            return render(request, 'butterflies/auth/access_denied.html')
    
    # Use appropriate form class based on model
    if model._meta.model_name == 'specimen':
        # Use SpecimenEditForm for editing, SpecimenForm for creating
        if object_id:
            form_class = SpecimenEditForm
        else:
            form_class = SpecimenForm
    elif model._meta.model_name == 'locality':
        form_class = LocalityForm
    elif model._meta.model_name == 'initials':
        form_class = InitialsForm
    else:
        form_class = modelform_factory(model, exclude=['id'])
    
    instance = None
    if object_id:
        try:
            instance = model.objects.get(pk=object_id)
        except model.DoesNotExist:
            raise Http404("Object not found")
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            # Redirect to home after save
            return redirect(reverse('report_table'))
    else:
        form = form_class(instance=instance)
    
    # Use model-specific organized template if it's a specimen
    if model._meta.model_name == 'specimen':
        template_name = 'butterflies/specimen_form.html'
    else:
        # Use model-specific template if it exists
        template_name = f'butterflies/{model._meta.model_name}_form.html'
        try:
            from django.template.loader import get_template
            get_template(template_name)
        except:
            # Fall back to generic form template
            template_name = 'butterflies/_form.html'
    
    return render(request, template_name, {
        'form': form, 
        'model_name': model._meta.verbose_name.title()
    })

# --- Model-Specific Create Views ---

@login_required
def create_specimen(request):
    """
    Create a new specimen record.
    Uses a dedicated form for specimen creation.
    Requires user authentication.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered form template or redirect on success
    """
    form = SpecimenForm()
    if request.method == 'POST':
        form = SpecimenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Specimen added successfully!')
            form = SpecimenForm()
    return render(request, 'butterflies/specimen_form.html', {'form': form})

@admin_required
def create_locality(request):
    """
    Create a new locality record.
    Uses a form based on the Locality model.
    Requires admin privileges.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered form template or redirect on success
    """
    form = LocalityForm()
    if request.method == 'POST':
        form = LocalityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Locality added successfully!')
            form = LocalityForm()
    return render(request, 'butterflies/locality_form.html', {'form': form})

@admin_required
def create_initials(request):
    """
    Create a new Initials object.
    Handles both form display and processing.
    Requires admin privileges.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered form template with success message on submission
    """
    form = InitialsForm()
    if request.method == 'POST':
        form = InitialsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Initials added successfully!')
            form = InitialsForm()
    return render(request, 'butterflies/initials_form.html', {'form': form})



# --- Report Views ---

@login_required
def report_table(request):
    """
    Shows a table of the 20 most recent specimens based on eventDate and eventTime.
    This is the main dashboard view.
    Requires user authentication.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered template with the 20 most recent specimens
    """
    
    # Get all specimens with related objects
    all_specimens = Specimen.objects.select_related('locality', 'recordedBy', 'georeferencedBy', 'identifiedBy').all()
    
    # Prepare list for sorting
    specimens_with_dates = []
    for specimen in all_specimens:
        # Default to minimum date if missing date information
        parsed_date = datetime.datetime.min
        
        # Convert eventDate (now a DateField) to datetime for sorting
        if specimen.eventDate:
            # Convert the date to a datetime object
            parsed_date = datetime.datetime.combine(specimen.eventDate, datetime.time.min)
                
        # Add time if available (format: "14:37")
        if specimen.eventTime and isinstance(parsed_date, datetime.datetime):
            try:
                # Extract hours and minutes
                match = re.match(r'(\d{1,2}):(\d{2})', specimen.eventTime)
                if match:
                    hours, minutes = map(int, match.groups())
                    parsed_date = parsed_date.replace(hour=hours, minute=minutes)
            except (ValueError, AttributeError):
                # Keep date without time if parsing fails
                pass
                
        # Add to list for sorting
        specimens_with_dates.append((specimen, parsed_date))
    
    # Sort by datetime (most recent first) and take top 20
    specimens_with_dates.sort(key=itemgetter(1), reverse=True)
    specimens = [item[0] for item in specimens_with_dates[:20]]
    
    return render(request, 'butterflies/report_table.html', {
        'specimens': specimens,
        'export_csv_url': reverse('export_report_csv'),
        'export_excel_url': reverse('export_report_excel'),
    })

# --- Export Views ---

def export_model_csv(request, model_name):
    """
    Generic function to export any model data as a CSV file.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to export
    Returns:
        HttpResponse with CSV content for download
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    
    if not model:
        raise Http404("Model not found")
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'
    writer = csv.writer(response)
    
    fields = [f.name for f in model._meta.fields if f.name != 'id']
    writer.writerow(fields)
    
    for obj in model.objects.all():
        row = []
        for field in fields:
            value = getattr(obj, field)
            # Handle foreign key relations
            if hasattr(value, 'pk'):
                value = str(value)
            row.append(value)
        writer.writerow(row)
    
    return response

def export_model_excel(request, model_name):
    """
    Generic function to export any model data as an Excel file.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to export
    Returns:
        HttpResponse with Excel content for download
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    
    if not model:
        raise Http404("Model not found")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = model._meta.verbose_name_plural.title()
    
    fields = [f.name for f in model._meta.fields if f.name != 'id']
    ws.append(fields)
    
    for obj in model.objects.all():
        row = []
        for field in fields:
            value = getattr(obj, field)
            # Handle foreign key relations
            if hasattr(value, 'pk'):
                value = str(value)
            row.append(value)
        ws.append(row)
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.xlsx"'
    
    return response

def export_report_csv(request):
    """
    Export the full report table (specimens with all related fields) as a CSV file.
    
    Parameters:
        request: HTTP request object
    Returns:
        HttpResponse with CSV content for download
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="specimen_report.csv"'
    writer = csv.writer(response)
    
    # Define all the headers based on the organized form categories
    headers = [
        # 1. Record-level Fields
        'modified',
        
        # 2. Location Fields
        'locality', 'decimalLatitude', 'decimalLongitude', 'exact_loc', 
        'coordinateUncertaintyInMeters', 'georeferencedBy', 'georeferencedDate', 
        'georeferenceProtocol', 'minimumElevationInMeters', 'maximumElevationInMeters',
        'country', 'stateProvince', 'county', 'municipality',
        
        # 3. Occurrence Fields
        'specimenNumber', 'catalogNumber', 'recordedBy', 'sex', 
        'behavior', 'occurrenceRemarks', 'disposition',
        
        # 4. Event Fields
        'year', 'month', 'day', 'eventTime', 'eventDate', 'habitat',
        'habitatNotes', 'samplingProtocol',
        
        # 5. Taxon Fields
        'family', 'subfamily', 'tribe', 'subtribe', 'genus',
        'specificEpithet', 'binomial', 'infraspecificEpithet',
        
        # 6. Identification Fields
        'identifiedBy', 'dateIdentified', 'identificationReferences', 'identificationRemarks'
    ]
    
    writer.writerow(headers)
    
    # Get all specimens with related data
    specimens = Specimen.objects.select_related(
        'locality', 'recordedBy', 'georeferencedBy', 'identifiedBy'
    ).all()
    
    # Write each specimen row with all fields
    for specimen in specimens:
        row = [
            specimen.modified,
            specimen.specimenNumber,
            specimen.catalogNumber,
            specimen.recordedBy,
            specimen.sex,
            specimen.behavior,
            specimen.disposition,
            specimen.occurrenceRemarks,
            specimen.eventDate,
            specimen.eventTime,
            specimen.year,
            specimen.month,
            specimen.day,
            specimen.locality.habitat if specimen.locality else '',
            specimen.habitatNotes,
            specimen.samplingProtocol,
            specimen.locality.country if specimen.locality else '',
            specimen.locality.region if specimen.locality else '',
            specimen.locality.province if specimen.locality else '',
            specimen.locality.district if specimen.locality else '',
            str(specimen.locality) if specimen.locality else '',
            specimen.minimumElevationInMeters,
            specimen.maximumElevationInMeters,
            specimen.decimalLatitude,
            specimen.decimalLongitude,
            specimen.exact_loc,
            specimen.coordinateUncertaintyInMeters,
            str(specimen.georeferencedBy) if specimen.georeferencedBy else '',
            specimen.georeferencedDate,
            specimen.georeferenceProtocol,
            str(specimen.identifiedBy) if specimen.identifiedBy else '',
            specimen.dateIdentified,
            specimen.identificationReferences,
            specimen.identificationRemarks,
            specimen.family,
            specimen.subfamily,
            specimen.tribe,
            specimen.subtribe,
            specimen.genus,
            specimen.specificEpithet,
            specimen.binomial,
            specimen.infraspecificEpithet
        ]
        writer.writerow(row)
    
    return response

def export_report_excel(request):
    """
    Export the full report table (specimens with all related fields) as an Excel file.
    
    Parameters:
        request: HTTP request object
    Returns:
        HttpResponse with Excel content for download
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Specimen Report"
    
    # Define all the headers based on the organized form categories
    headers = [
        # 1. Record-level Fields
        'modified',
        
        # 2. Location Fields
        'locality', 'decimalLatitude', 'decimalLongitude', 'exact_loc', 
        'coordinateUncertaintyInMeters', 'georeferencedBy', 'georeferencedDate', 
        'georeferenceProtocol', 'minimumElevationInMeters', 'maximumElevationInMeters',
        'country', 'stateProvince', 'county', 'municipality',
        
        # 3. Occurrence Fields
        'specimenNumber', 'catalogNumber', 'recordedBy', 'sex', 'behavior', 'occurrenceRemarks', 'disposition',
        
        # 4. Event Fields
        'year', 'month', 'day', 'eventTime', 'eventDate', 'habitat',
        'habitatNotes', 'samplingProtocol',
        
        # 5. Taxon Fields
        'family', 'subfamily', 'tribe', 'subtribe', 'genus',
        'specificEpithet', 'binomial', 'infraspecificEpithet',
        
        # 6. Identification Fields
        'identifiedBy', 'dateIdentified', 'identificationReferences', 'identificationRemarks'
    ]
    
    ws.append(headers)
    
    # Get all specimens with related data
    specimens = Specimen.objects.select_related(
        'locality', 'recordedBy', 'georeferencedBy', 'identifiedBy'
    ).all()
    
    # Write each specimen row with all fields
    for specimen in specimens:
        row = [
            specimen.modified,
            specimen.specimenNumber,
            specimen.catalogNumber,
            str(specimen.recordedBy) if specimen.recordedBy else '',
            specimen.sex,
            specimen.behavior,
            specimen.disposition,
            specimen.occurrenceRemarks,
            specimen.eventDate,
            specimen.eventTime,
            specimen.year,
            specimen.month,
            specimen.day,
            specimen.locality.habitat if specimen.locality else '',
            specimen.habitatNotes,
            specimen.samplingProtocol,
            specimen.locality.country if specimen.locality else '',
            specimen.locality.region if specimen.locality else '',
            specimen.locality.province if specimen.locality else '',
            specimen.locality.district if specimen.locality else '',
            str(specimen.locality) if specimen.locality else '',
            specimen.minimumElevationInMeters,
            specimen.maximumElevationInMeters,
            specimen.decimalLatitude,
            specimen.decimalLongitude,
            specimen.exact_loc,
            specimen.coordinateUncertaintyInMeters,
            str(specimen.georeferencedBy) if specimen.georeferencedBy else '',
            specimen.georeferencedDate,
            specimen.georeferenceProtocol,
            str(specimen.identifiedBy) if specimen.identifiedBy else '',
            specimen.dateIdentified,
            specimen.identificationReferences,
            specimen.identificationRemarks,
            specimen.family,
            specimen.subfamily,
            specimen.tribe,
            specimen.subtribe,
            specimen.genus,
            specimen.specificEpithet,
            specimen.binomial,
            specimen.infraspecificEpithet
        ]
        ws.append(row)
    
    # Format the Excel file
    for column in ws.columns:
        max_length = 0
        column_letter = openpyxl.utils.get_column_letter(column[0].column)
        for cell in column:
            if cell.value:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = min(adjusted_width, 50)  # Cap width at 50
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="specimen_report.xlsx"'
    
    return response

# --- Import Views ---

# Helper function to validate and construct eventDate from components
def validate_and_construct_event_date(day, month, year, debug_mode=False):
    """
    Validates day, month, year components and attempts to construct a valid date.
    
    Returns:
        tuple: (date_obj, error_message, is_valid)
            - date_obj: datetime.date or None if invalid
            - error_message: String with error details or None if valid
            - is_valid: Boolean indicating if the date is valid
    """
    date_obj = None
    date_error = None
    
    # If not all components are provided, we can't validate
    if not (day and month and year):
        missing = []
        if not day: missing.append('day')
        if not month: missing.append('month')
        if not year: missing.append('year')
        components_str = ', '.join(missing)
        return None, f"Missing date components: {components_str}", False
    
    try:
        # Try numeric month parsing first
        if month.isdigit() and 1 <= int(month) <= 12:
            try:
                date_obj = datetime.date(int(year), int(month), int(day))
            except ValueError as e:
                date_error = f"Invalid date: {e}"
        else:
            # Try abbreviated and full month names
            temp_date_str = f"{year}-{month}-{day}"
            for fmt in ["%Y-%b-%d", "%Y-%B-%d"]:
                try:
                    date_obj = datetime.datetime.strptime(temp_date_str, fmt).date()
                    break
                except ValueError:
                    continue
        
        # If direct parsing failed, try string parsing as fallback
        if not date_obj:
            date_str = f"{day} {month}, {year}"
            try:
                parsed_date = parse_date_value(date_str)
                if parsed_date:
                    date_obj = parsed_date
            except Exception as e:
                if not date_error:
                    date_error = f"Could not parse date from components: {e}"
        
        # Return the results
        if date_obj:
            return date_obj, None, True
        else:
            error = date_error or "Could not construct a valid date from day, month, and year"
            return None, error, False
            
    except Exception as e:
        return None, f"Error validating date components: {str(e)}", False
        
# Helper function for processing date fields in a unified way
def process_date_fields_unified(row_data, request=None, row_index=None, context=None, debug_mode=False):
    """
    Process all date fields in a row, converting string dates to date objects.
    Can be used both for preview and import phases.
    
    Args:
        row_data (dict): The row data containing date fields
        request (HttpRequest): Optional request object for adding messages (import mode)
        row_index (int): Optional index of the current row for error messages (import mode)
        context (dict): Optional preview context for adding warnings/errors (preview mode)
        debug_mode (bool): Whether to enable additional debug messages
        
    Returns:
        dict: Dictionary of parse results by field (field_name -> date_obj) 
              or None if used in preview mode
    """
    # Define date fields to process
    date_fields = ['eventDate', 'dateIdentified', 'georeferencedDate']
    results = {}
    
    # Process each date field
    for field in date_fields:
        if field in row_data and row_data[field]:
            # Skip eventDate special handling for now - will be processed separately
            if field == 'eventDate':
                continue
                
            # Use our helper function to parse date fields
            date_obj, error_msg, is_valid = parse_date_field(row_data[field], debug_mode)
            
            if is_valid and date_obj:
                # Store the date object
                row_data[field] = date_obj
                results[field] = date_obj
                
                # Add info message in different modes
                if debug_mode:
                    if request:  # Import mode
                        messages.info(request, f"Converted date for {field} from '{row_data[field]}' to '{date_obj}'")
                    elif context:  # Preview mode
                        formatted = format_date_value(date_obj)
                        context['warnings'].append(
                            f"Date '{row_data[field]}' will be stored as '{date_obj}' and displayed as '{formatted}'"
                        )
            else:
                # Handle invalid date
                row_data[field] = None
                results[field] = None
                
                if debug_mode:
                    if request:  # Import mode
                        messages.warning(request, f"{error_msg} for {field}, set to None")
                    elif context:  # Preview mode
                        context['errors'].append(f"{error_msg} for {field}")
                        context['error_fields'].add(field)
    
    # Handle eventDate separately using the unified process_event_date function
    success, skip_row, event_date_obj = process_event_date(row_data, context, request, row_index, debug_mode)
    if event_date_obj:
        results['eventDate'] = event_date_obj
    
    return results if not context else None
    
# Helper function for processing foreign keys during import
def process_foreign_keys(row_data, row_index, request, debug_mode=False):
    """
    Process foreign key relationships for a specimen row.
    
    Args:
        row_data (dict): The row data containing foreign key fields
        row_index (int): The index of the current row for error messages
        request (HttpRequest): The request object for adding messages
        debug_mode (bool): Whether to enable additional debug messages
    """
    # Define foreign key fields and their related models
    fk_fields = {
        'locality': (Locality, 'localityCode'),
        'recordedBy': (Initials, 'initials'),
        'georeferencedBy': (Initials, 'initials'),
        'identifiedBy': (Initials, 'initials')
    }
    
    # Process each foreign key field
    for fk_field, (related_model, lookup_field) in fk_fields.items():
        if fk_field in row_data and row_data[fk_field]:
            lookup_value = row_data[fk_field]
            
            # Special case: allow "." as a placeholder for identifiedBy (treat as None/NULL)
            if fk_field == 'identifiedBy' and lookup_value == '.':
                if debug_mode:
                    messages.info(
                        request,
                        f"Found '.' placeholder for {fk_field} in row {row_index+1}. Setting to NULL."
                    )
                row_data[fk_field] = None
                continue
                
            # Normal case: look up the related object
            related_obj = related_model.objects.filter(**{lookup_field: lookup_value}).first()
            if related_obj:
                row_data[fk_field] = related_obj
            else:
                row_data[fk_field] = None
                messages.warning(
                    request, 
                    f"{related_model.__name__} '{lookup_value}' not found for {fk_field} in row {row_index+1}."
                )


# Helper function to parse a date field
def parse_date_field(date_value, debug_mode=False):
    """
    Attempts to parse a date string into a datetime.date object.
    
    Returns:
        tuple: (date_obj, error_message, is_valid)
            - date_obj: datetime.date or None if invalid
            - error_message: String with error details or None if valid
            - is_valid: Boolean indicating if the date is valid
    """
    if not date_value or date_value == '.':
        return None, None, True  # Empty or placeholder, not an error
    
    # Convert to string if not already
    if not isinstance(date_value, str):
        date_value = str(date_value)
    
    # If it has a time component (contains space), extract just the date part
    if ' ' in date_value:
        try:
            date_value = date_value.split(' ')[0]
        except Exception:
            pass
        
    try:
        # Try direct parsing with dateutil
        try:
            date_obj = date_parser.parse(date_value).date()
            return date_obj, None, True
        except Exception as dateutil_error:
            # If direct parsing fails, try our standard format
            try:
                date_obj = parse_date_value(date_value)
                if date_obj:
                    return date_obj, None, True
            except Exception:
                pass
            
            # Try ISO format specifically
            try:
                # Handle potential timezone information
                if 'T' in date_value:
                    date_value = date_value.split('T')[0]
                date_obj = datetime.date.fromisoformat(date_value)
                return date_obj, None, True
            except ValueError:
                pass
                
        # If we get here, all parsing attempts failed
        return None, f"Could not parse date '{date_value}'", False
    except Exception as e:
        return None, f"Invalid date format '{date_value}': {str(e)}", False
        

# (The process_date_fields function has been replaced by process_date_fields_unified)


# Helper function to build the cache of valid foreign key values for specimen validation
def build_fk_validation_cache():
    """
    Builds a cache of valid foreign key values for specimen validation.
    
    Returns:
        tuple: (fk_fields_validation, valid_values_cache)
            - fk_fields_validation: Dictionary mapping foreign key fields to their related models and fields
            - valid_values_cache: Dictionary mapping foreign key fields to sets of valid values
    """
    fk_fields_validation = {
        'locality': (Locality, 'localityCode', 'Locality'),
        'recordedBy': (Initials, 'initials', 'Initials'),
        'georeferencedBy': (Initials, 'initials', 'Initials'),
        'identifiedBy': (Initials, 'initials', 'Initials')
    }
    
    # Build a cache of valid values
    valid_values_cache = {}
    for fk_field, (related_model, lookup_field, display_name) in fk_fields_validation.items():
        valid_values_cache[fk_field] = set(
            related_model.objects.values_list(lookup_field, flat=True)
        )
    
    return fk_fields_validation, valid_values_cache
    
# Helper function for managing import errors
def handle_import_error(request, error_msg, row_index):
    """
    Add an import error to the session for display later.
    
    Args:
        request (HttpRequest): The request object
        error_msg (str): The error message
        row_index (int): The index of the row with the error
    """
    user_message = f"Error in row {row_index+1}: {error_msg}"
    messages.error(request, user_message)
    import_errors = request.session.get('import_errors', [])
    import_errors.append(user_message)
    request.session['import_errors'] = import_errors

# Helper function for validating specimen data - unified approach for preview and import
def validate_specimen_data(row_data, preview_item=None, common_errors=None, debug_mode=False):
    """
    Performs common validation for specimen data.
    
    Parameters:
        row_data: Dictionary containing the specimen data
        preview_item: Optional dictionary with preview metadata to update
                     If None, only returns errors without modifying preview_item
        common_errors: Dictionary of pre-identified common errors (optional)
        debug_mode: Boolean indicating whether to show detailed debug information
    
    Returns:
        Dictionary of errors by field (if preview_item is None)
        Otherwise, updates preview_item in place and returns None
    """
    # Use for collecting errors if preview_item is None
    collected_errors = {}
    collected_warnings = []
    collected_error_fields = set()
    
    # Get the foreign key fields validation info
    fk_fields_validation, valid_values_cache = build_fk_validation_cache()
    
    # Validate foreign key fields
    for fk_field, (related_model, lookup_field, display_name) in fk_fields_validation.items():
        if fk_field in row_data and row_data[fk_field]:
            lookup_value = row_data[fk_field]
            
            # Special case: allow "." as a placeholder for identifiedBy
            if fk_field == 'identifiedBy' and lookup_value == '.':
                # This is valid - it will be converted to NULL/None during import
                continue
                
            key = f"{fk_field}_invalid"
            
            # Check if this value is invalid using the common_errors or validation cache
            is_invalid = False
            
            # Use common_errors if available (faster than DB check)
            if common_errors and key in common_errors and lookup_value in common_errors[key]:
                is_invalid = True
                
            # Also check validation cache
            elif lookup_value not in valid_values_cache[fk_field]:
                is_invalid = True
            
            if is_invalid:
                error_msg = f"Invalid {display_name}: '{lookup_value}' does not exist in the database"
                if preview_item:
                    preview_item['errors'].append(error_msg)
                    preview_item['error_fields'].add(fk_field)
                else:
                    collected_errors[fk_field] = error_msg
                    collected_error_fields.add(fk_field)
    
    # Validate sex field
    if 'sex' in row_data and row_data['sex']:
        sex_invalid = False
        
        # First check common errors if available
        if common_errors and 'sex_values' in common_errors and row_data['sex'] in common_errors['sex_values']:
            sex_invalid = True
        # Always validate directly too
        elif row_data['sex'] not in ['male', 'female', '.']:
            sex_invalid = True
            
        if sex_invalid:
            error_msg = f"Invalid sex: '{row_data['sex']}'. Must be 'male', 'female', or '.'"
            if preview_item:
                preview_item['errors'].append(error_msg)
                preview_item['error_fields'].add('sex')
            else:
                collected_errors['sex'] = error_msg
                collected_error_fields.add('sex')
    
    # Validate dates
    date_fields = ['eventDate', 'dateIdentified', 'georeferencedDate']
    for date_field in date_fields:
        if date_field in row_data and row_data[date_field]:
            original_value = row_data[date_field]
            # Skip the "." placeholder, as it will be filled from components
            if original_value == '.':
                continue
            
            # Use our helper function to validate the date
            date_obj, error_msg, is_valid = parse_date_field(original_value, debug_mode)
            
            if is_valid and date_obj:
                # Only show conversion information in debug mode
                if debug_mode:
                    formatted = format_date_value(date_obj)
                    warning_msg = f"Date '{original_value}' will be stored as '{date_obj}' and displayed as '{formatted}'"
                    if preview_item:
                        preview_item['warnings'].append(warning_msg)
                    else:
                        collected_warnings.append(warning_msg)
            elif not is_valid:
                # Only show parsing failures as errors, not warnings
                error_msg = f"{error_msg} for {date_field}"
                if preview_item:
                    preview_item['errors'].append(error_msg)
                    preview_item['error_fields'].add(date_field)
                else:
                    collected_errors[date_field] = error_msg
                    collected_error_fields.add(date_field)
    
    # Check catalogNumber components
    if not row_data.get('catalogNumber'):
        missing_components = []
        
        if not row_data.get('specimenNumber'):
            missing_components.append('specimenNumber')
        
        if not row_data.get('year'):
            missing_components.append('year')
        
        if 'locality' not in row_data or not row_data['locality']:
            missing_components.append('locality')
        
        if missing_components:
            components_str = ', '.join(missing_components)
            error_msg = f"Missing required field(s): {components_str}. These are needed to generate catalogNumber."
            
            if preview_item:
                preview_item['errors'].append(error_msg)
                for field in missing_components:
                    preview_item['error_fields'].add(field)
            else:
                for field in missing_components:
                    collected_errors[field] = "Required for catalogNumber"
                    collected_error_fields.add(field)
    
    # Check boolean fields
    if 'exact_loc' in row_data and row_data['exact_loc']:
        value = str(row_data['exact_loc']).upper()
        if value not in ['TRUE', 'FALSE']:
            warning_msg = f"Value '{row_data['exact_loc']}' for exact_loc will be converted to TRUE/FALSE"
            if preview_item:
                preview_item['warnings'].append(warning_msg)
            else:
                collected_warnings.append(warning_msg)
    
    # Process eventTime to strip seconds (HH:MM:SS → HH:MM)
    if 'eventTime' in row_data and row_data['eventTime']:
        time_value = str(row_data['eventTime'])
        # Only strip seconds if it's a standard time format (not a range with hyphens or other special formats)
        if time_value.count(':') == 2 and '-' not in time_value and '/' not in time_value and ',' not in time_value:
            # Extract just the hours and minutes (HH:MM)
            try:
                hour_minute = ':'.join(time_value.split(':')[:2])
                row_data['eventTime'] = hour_minute
                
                # Add info message
                warning_msg = f"Stripped seconds from time value: '{time_value}' → '{hour_minute}'"
                if preview_item:
                    preview_item['warnings'].append(warning_msg)
                else:
                    collected_warnings.append(warning_msg)
            except Exception:
                # Continue with original value if stripping fails
                pass
                
    # Return collected errors if no preview_item was provided
    if not preview_item:
        return {
            'errors': collected_errors,
            'warnings': collected_warnings,
            'error_fields': collected_error_fields
        }
    
    return None

# Helper function for processing eventDate from components - unified for preview and import
def process_event_date(row_data, context=None, request=None, row_index=None, debug_mode=False):
    """
    Validates and processes eventDate from day, month, year components.
    Can be used both for preview display and for actual import.
    
    Parameters:
        row_data: Dictionary containing row data with day, month, year components
        context: Optional dictionary for preview metadata (warnings/errors)
        request: Optional HttpRequest object for import errors
        row_index: Optional row index for error messages during import
        debug_mode: Boolean indicating whether to show detailed debug information
        
    Returns:
        tuple: (success, skip_row, date_obj)
            - success: Boolean indicating if the date was successfully processed
            - skip_row: Boolean indicating if the row should be skipped (import only)
            - date_obj: The date object if successfully created, None otherwise
    """
    # Only process if eventDate is missing or "."
    if not row_data.get('eventDate') or row_data.get('eventDate') == '.':
        day = row_data.get('day')
        month = row_data.get('month')
        year = row_data.get('year')
        
        # Use our existing function to validate and construct the date
        date_obj, error_msg, is_valid = validate_and_construct_event_date(day, month, year, debug_mode)
        
        # At least one component exists but validation failed
        if (day or month or year) and not is_valid:
            # Handle validation failure differently for preview vs import
            if context:  # Preview mode
                context['errors'].append(error_msg)
                
                # Mark relevant fields as having errors
                if not day: context['error_fields'].add('day')
                if not month: context['error_fields'].add('month')
                if not year: context['error_fields'].add('year')
                context['error_fields'].add('eventDate')
                
                return False, False, None
            elif request:  # Import mode
                handle_import_error(request, error_msg, row_index)
                
                # If in debug mode, continue with None value rather than failing
                if debug_mode:
                    messages.warning(request, f"Row {row_index+1}: Using NULL for eventDate due to parsing error")
                    row_data['eventDate'] = None
                    return True, False, None
                else:
                    return False, True, None
            else:
                # Basic mode just returns the status
                return False, False, None
        
        # All components exist and validation succeeded
        elif is_valid and date_obj:
            # Handle success differently for preview vs import
            if context:  # Preview mode
                # Success! We'll add an informational message
                context['warnings'].append(
                    f"Will generate eventDate from components: {day} {month} {year} → {date_obj}"
                )
                # Update the preview data to show the generated eventDate
                row_data['eventDate'] = str(date_obj)
                context['data']['eventDate'] = str(date_obj)
                
                return True, False, date_obj
            else:  # Import mode or basic mode
                row_data['eventDate'] = date_obj
                
                # Add debug message if in import mode
                if request and debug_mode:
                    messages.info(request, f"Generated eventDate '{format_date_value(date_obj)}' from components: {day} {month} {year}")
                
                return True, False, date_obj
        
        # Have some but not all components
        elif (day or month or year) and not (day and month and year):
            error_msg = f"Incomplete date components: day={day or 'missing'}, month={month or 'missing'}, year={year or 'missing'}"
            
            if context:  # Preview mode
                context['errors'].append(error_msg)
                # Mark fields as having errors
                if not day: context['error_fields'].add('day')
                if not month: context['error_fields'].add('month')
                if not year: context['error_fields'].add('year')
                context['error_fields'].add('eventDate')
                
                return False, False, None
            elif request:  # Import mode
                handle_import_error(request, error_msg, row_index)
                
                # If in debug mode, continue with None value rather than failing
                if debug_mode:
                    messages.warning(request, f"Row {row_index+1}: Using NULL for eventDate due to incomplete components")
                    row_data['eventDate'] = None
                    return True, False, None
                else:
                    return False, True, None
            else:
                # Basic mode just returns the status
                return False, False, None
            
    return True, False, None

@csrf_exempt
@admin_required
def import_model(request, model_name):
    """
    Generic function to import data for any model from CSV or Excel file.
    This simplified version focuses on:
    1. Reading all values as text without restrictions
    2. Converting data to proper formats before import
    3. Showing a clear preview with potential issues
    4. Handling imports with better error messages
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to import
    Returns:
        Rendered template for import form, preview, or redirect
    """
    # Using the helper functions defined outside this function

    # Find the model
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    
    if not model:
        raise Http404("Model not found")
    
    # Prepare context with model information
    context = {
        'model_name': model._meta.verbose_name,
        'model_name_plural': model._meta.verbose_name_plural,
        'model_name_internal': model_name,
        'model_fields': [f.name for f in model._meta.fields if f.name != 'id'],
    }
    
    # For Specimen model, we only check catalogNumber for uniqueness
    # For other models, find unique field for duplicate detection
    unique_field = None
    if model_name == 'specimen':
        unique_field = 'catalogNumber'  # Specifically use catalogNumber for specimens
    else:
        # For other models, use the first unique field found (excluding id)
        for field in model._meta.fields:
            if field.unique and field.name != 'id':
                unique_field = field.name
                break
            
        # Check unique_together constraints if no unique field found
        if not unique_field:
            unique_together = getattr(model._meta, 'unique_together', [])
            if unique_together and isinstance(unique_together[0], (list, tuple)) and len(unique_together[0]) > 0:
                unique_field = unique_together[0][0]
    
    # Add unique field info to context
    context['has_unique_field'] = bool(unique_field)
    context['unique_field'] = unique_field
    
    # Reset any previous import session data
    if 'has_errors' in request.session:
        del request.session['has_errors']
    
    # Step 1: Handle file upload and parse into DataFrame
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_ext = file.name.split('.')[-1].lower()
        
        try:
            # Read file contents - all values as strings initially
            if file_ext == 'csv':
                # Use dtype=str to read everything as text
                df = pd.read_csv(file, dtype=str, keep_default_na=False)
            elif file_ext in ('xls', 'xlsx'):
                # Use dtype=str to read everything as text initially
                df = pd.read_excel(file, dtype=str)
                # Convert all numeric columns to string to prevent automatic float conversion
                for col in df.columns:
                    df[col] = df[col].astype(str)
            else:
                messages.error(request, 'Unsupported file type. Please upload a CSV or Excel file.')
                context['error'] = 'Unsupported file type. Please upload a CSV or Excel file.'
                return render(request, 'butterflies/import_model.html', context)
            
            # Basic cleanup - strip whitespace from all string values
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            
            # Replace empty strings with None
            df = df.replace(['', 'nan', 'None', 'NaN', 'null', 'NULL'], None)
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Check if dataframe is empty after cleaning
            if df.empty:
                messages.error(request, 'The uploaded file contains no usable data after cleaning.')
                context['error'] = 'The uploaded file contains no usable data after cleaning.'
                return render(request, 'butterflies/import_model.html', context)
                
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            context['error'] = f'Error processing file: {str(e)}'
            return render(request, 'butterflies/import_model.html', context)
        
        # Step 2: Check columns and prepare data for preview
        # Get expected field names
        expected_fields = [f.name for f in model._meta.fields if f.name != 'id']
        
        # Map any foreign key fields to their expected column names for import
        if model_name == 'specimen':
            fk_fields = {
                'locality': 'locality',        # Locality.localityCode
                'recordedBy': 'recordedBy',     # Initials.initials
                'georeferencedBy': 'georeferencedBy', # Initials.initials
                'identifiedBy': 'identifiedBy',   # Initials.initials
            }
        else:
            fk_fields = {}
        
        # Check for missing columns
        available_columns = list(df.columns)
        missing_columns = []
        
        for field in expected_fields:
            # Check if field is in DataFrame columns or has a mapped name
            if field not in available_columns and field not in fk_fields.keys():
                missing_columns.append(field)
        
        if missing_columns:
            context['error'] = f'Missing columns: {", ".join(missing_columns)}'
            context['available_columns'] = available_columns
            context['expected_columns'] = expected_fields
            return render(request, 'butterflies/import_model.html', context)
        
        # Step 3: Prepare data for preview
        # Get debug mode parameter (show detailed conversion info)
        debug_mode = request.POST.get('debug_mode') == 'true'
        
        # First, convert all rows to clean dicts for processing
        all_rows_data = []
        for idx, row in df.iterrows():
            # Convert row to clean dict (None instead of NaN)
            row_data = {}
            for field in expected_fields:
                # For foreign keys, use the mapped column name if available
                if field in fk_fields:
                    col_name = fk_fields[field]
                    if col_name in row:
                        row_data[field] = row[col_name]
                # For regular fields, use the field name directly
                elif field in row:
                    row_data[field] = row[field]
            all_rows_data.append(row_data)
            
        # Pre-validate to identify common error patterns
        common_errors = {}
        if model_name == 'specimen':
            # Get foreign key validation info
            fk_fields_validation, valid_values_cache = build_fk_validation_cache()
            
            # Track invalid sex values and foreign keys
            for row_data in all_rows_data:
                if 'sex' in row_data and row_data['sex']:
                    if row_data['sex'] not in ['male', 'female', '.']:
                        if 'sex_values' not in common_errors:
                            common_errors['sex_values'] = set()
                        common_errors['sex_values'].add(row_data['sex'])
                        
                # Track invalid foreign keys
                for fk_field in fk_fields_validation:
                    if fk_field in row_data and row_data[fk_field]:
                        # Special case: allow "." as a placeholder for identifiedBy
                        if fk_field == 'identifiedBy' and row_data[fk_field] == '.':
                            continue
                            
                        if row_data[fk_field] not in valid_values_cache[fk_field]:
                            key = f"{fk_field}_invalid"
                            if key not in common_errors:
                                common_errors[key] = set()
                            common_errors[key].add(row_data[fk_field])
                            
        # We'll use the parse_date_field helper function defined outside this function

        # Now process each row for preview with consistent error detection
        preview_data = []
        for row_data in all_rows_data:
            
            # Check for duplicates if we have a unique field
            is_duplicate = False
            suggested_key = None
            
            if unique_field and unique_field in row_data and row_data[unique_field]:
                unique_value = row_data[unique_field]
                # Check for duplicates and mark as error
                if model.objects.filter(**{unique_field: unique_value}).exists():
                    is_duplicate = True
                    # We'll add error to the preview item after it's created
            
            # Create preview item
            preview_item = {
                'data': row_data,
                'duplicate': is_duplicate,
                'suggested_key': suggested_key,
                'warnings': [],  # Store any format warnings here
                'errors': [],    # Store validation errors here that must be fixed
                'error_fields': set()  # Track fields with errors for highlighting
            }
            
            # Add duplicate error message if duplicate was found
            if is_duplicate and unique_field:
                unique_value = row_data[unique_field]
                field_label = unique_field.capitalize()
                error_msg = f"Duplicate {field_label}: '{unique_value}' already exists in the database"
                preview_item['errors'].append(error_msg)
                preview_item['error_fields'].add(unique_field)
            
                # Check for potential format issues
            if model_name == 'specimen':
                # Use our unified helper functions for validation
                validate_specimen_data(row_data, preview_item, common_errors, debug_mode)
                
                # Process dates using our unified helper
                process_date_fields_unified(row_data, None, None, preview_item, debug_mode)
                preview_data.append(preview_item)
        
        # Add preview data to context
        context['preview'] = preview_data
        context['fields'] = expected_fields
        
        # Check if any rows have errors that would prevent import
        has_errors = False
        error_count = 0
        for item in preview_data:
            if item['errors']:
                has_errors = True
                error_count += len(item['errors'])
        
        context['has_errors'] = has_errors
        context['error_count'] = error_count
        
        # Store error status in session for security check during confirmation
        request.session['has_errors'] = has_errors
        request.session.modified = True
        
        # Render preview template
        return render(request, 'butterflies/import_model_preview.html', context)
    
    # Step 4: Handle revalidation of form data
    elif request.method == 'POST' and request.POST.get('revalidate'):
        # Get model fields and row count
        fields = [f.name for f in model._meta.fields if f.name != 'id']
        rows = int(request.POST.get('row_count', 0))
        debug_mode = request.POST.get('debug_mode') == 'true'
        
        # Reconstruct rows from form data
        all_rows_data = []
        for i in range(rows):
            row_data = {f: request.POST.get(f'row_{i}_{f}', '') for f in fields}
            # Clean data: convert empty strings to None
            for field, value in row_data.items():
                if value == '':
                    row_data[field] = None
            all_rows_data.append(row_data)
            
        # Now perform the same validation as in the file upload case
        # Pre-validate to identify common error patterns
        common_errors = {}
        if model_name == 'specimen':
            # Get foreign key validation info
            fk_fields_validation, valid_values_cache = build_fk_validation_cache()
            
            # Track invalid values
            for row_data in all_rows_data:
                if 'sex' in row_data and row_data['sex']:
                    if row_data['sex'] not in ['male', 'female', '.']:
                        if 'sex_values' not in common_errors:
                            common_errors['sex_values'] = set()
                        common_errors['sex_values'].add(row_data['sex'])
                        
                # Track invalid foreign keys
                for fk_field in fk_fields_validation:
                    if fk_field in row_data and row_data[fk_field]:
                        # Special case: allow "." as a placeholder for identifiedBy
                        if fk_field == 'identifiedBy' and row_data[fk_field] == '.':
                            continue
                            
                        if row_data[fk_field] not in valid_values_cache[fk_field]:
                            key = f"{fk_field}_invalid"
                            if key not in common_errors:
                                common_errors[key] = set()
                            common_errors[key].add(row_data[fk_field])
                            
        # Now process each row for preview with consistent error detection
        preview_data = []
        for row_data in all_rows_data:
            # Check for duplicates if we have a unique field
            is_duplicate = False
            suggested_key = None
            
            if unique_field and unique_field in row_data and row_data[unique_field]:
                unique_value = row_data[unique_field]
                # Check for duplicates and mark as error
                if model.objects.filter(**{unique_field: unique_value}).exists():
                    is_duplicate = True
                    # We'll add error to the preview item after it's created
            
            # Create preview item
            preview_item = {
                'data': row_data,
                'duplicate': is_duplicate,
                'suggested_key': suggested_key,
                'warnings': [],  # Store any format warnings here
                'errors': [],    # Store validation errors here that must be fixed
                'error_fields': set()  # Track fields with errors for highlighting
            }
            
            # Add duplicate error message if duplicate was found
            if is_duplicate and unique_field:
                unique_value = row_data[unique_field]
                field_label = unique_field.capitalize()
                error_msg = f"Duplicate {field_label}: '{unique_value}' already exists in the database"
                preview_item['errors'].append(error_msg)
                preview_item['error_fields'].add(unique_field)
            
            # Perform the same validation as in the file upload case
            if model_name == 'specimen':
                # Use our unified helper functions for validation
                validate_specimen_data(row_data, preview_item, common_errors, debug_mode)
                
                # Process dates using our unified helper
                process_date_fields_unified(row_data, None, None, preview_item, debug_mode)
            
            preview_data.append(preview_item)
        
        # Add preview data to context
        context['preview'] = preview_data
        context['fields'] = fields
        
        # Check if any rows have errors that would prevent import
        has_errors = False
        error_count = 0
        for item in preview_data:
            if item['errors']:
                has_errors = True
                error_count += len(item['errors'])
        
        context['has_errors'] = has_errors
        context['error_count'] = error_count
        
        # Store error status in session for security check during confirmation
        request.session['has_errors'] = has_errors
        request.session.modified = True
        
        # Add a message to indicate revalidation
        if has_errors:
            messages.warning(request, f"Still found {error_count} errors. Please fix all errors before importing.")
        else:
            messages.success(request, "All validation errors have been fixed! You can now import the data.")
        
        # Render preview template
        return render(request, 'butterflies/import_model_preview.html', context)
        
    # Step 5: Handle import confirmation
    elif request.method == 'POST' and request.POST.get('confirm'):
        # Get model fields and row count
        fields = [f.name for f in model._meta.fields if f.name != 'id']
        rows = int(request.POST.get('row_count', 0))
        debug_mode = request.POST.get('debug_mode') == 'true'
        
        # Security check: Ensure there are no validation errors before proceeding
        # This prevents bypassing the disabled button via direct POST
        if 'has_errors' in request.session and request.session['has_errors']:
            messages.error(
                request,
                'Import cancelled: There are validation errors that must be fixed before importing.'
            )
            return redirect('import_model', model_name=model_name)
        
        # Initialize counters
        imported_count = 0
        skipped_count = 0
        
        # Clear previous import errors
        if 'import_errors' in request.session:
            del request.session['import_errors']
        request.session['import_errors'] = []
        
        # Process each row from form data
        for i in range(rows):
            # Extract data for this row from POST data
            row_data = {f: request.POST.get(f'row_{i}_{f}', '') for f in fields}
            
            # Clean data: convert empty strings to None
            for field, value in row_data.items():
                if value == '':
                    row_data[field] = None
            
            # Step 5: Process and convert data before creating objects
            try:
                # Note: We don't need to check for duplicates here again, since:
                # 1. The preview validation already caught any duplicates
                # 2. We checked request.session['has_errors'] above and prevented import if errors exist
                # 3. The user had to fix all errors before the import button was enabled
                
                # Model-specific conversions
                if model_name == 'specimen':
                    # Process foreign key fields using our helper function
                    process_foreign_keys(row_data, i, request, debug_mode)
                    
                    # Process all date fields using our unified helper
                    process_date_fields_unified(row_data, request, i, None, debug_mode)
                    
                    # Check if event date processing caused a skip flag
                    # The check is already done inside process_date_fields_unified, 
                    # but we need to handle the skip logic here
                    success, should_skip, _ = process_event_date(row_data, None, request, i, debug_mode)
                    if not success and should_skip:
                        skipped_count += 1
                        raise ValueError("Error processing eventDate, row skipped")
                    
                    # Process eventTime to strip seconds from Excel time values (HH:MM:SS → HH:MM)
                    if 'eventTime' in row_data and row_data['eventTime']:
                        time_value = str(row_data['eventTime'])
                        
                        # Only strip seconds if it's a standard time format (not a range with hyphens or other special formats)
                        if time_value.count(':') == 2 and '-' not in time_value and '/' not in time_value and ',' not in time_value:
                            # Extract just the hours and minutes (HH:MM)
                            try:
                                hour_minute = ':'.join(time_value.split(':')[:2])
                                row_data['eventTime'] = hour_minute
                                if debug_mode:
                                    messages.info(request, f"Stripped seconds from time value: '{time_value}' → '{hour_minute}'")
                            except Exception as time_ex:
                                if debug_mode:
                                    messages.warning(request, f"Failed to strip seconds from time '{time_value}': {str(time_ex)}")
                    
                    # Handle exact_loc boolean field
                    if 'exact_loc' in row_data and row_data['exact_loc']:
                        # Normalize to TRUE/FALSE strings
                        value = str(row_data['exact_loc']).upper()
                        if value in ['TRUE', 'T', 'YES', 'Y', '1']:
                            row_data['exact_loc'] = 'TRUE'
                        else:
                            row_data['exact_loc'] = 'FALSE'
                    
                    # Convert numeric fields to integers
                    int_fields = ['specimenNumber', 'year', 'month', 'day']
                    for field in int_fields:
                        if field in row_data and row_data[field]:
                            try:
                                # Convert to int, handling potential decimal points
                                if '.' in str(row_data[field]):
                                    row_data[field] = str(int(float(row_data[field])))
                                # Ensure it's a string representation of an integer
                                int(row_data[field])  # Just to validate
                            except (ValueError, TypeError):
                                # If not a valid number, keep as is
                                pass
                
                # Ensure date fields are properly formatted for Django model
                date_fields = ['eventDate', 'dateIdentified', 'georeferencedDate']
                for field in date_fields:
                    if field in row_data and row_data[field]:
                        # If it's a datetime or date object, ensure we get just the date part
                        if hasattr(row_data[field], 'date'):
                            row_data[field] = row_data[field].date()
                        elif hasattr(row_data[field], 'strftime'):
                            # It's already a date object, leave it as is
                            pass
                        elif isinstance(row_data[field], str) and ' ' in row_data[field]:
                            # Handle string with datetime format by extracting just the date part
                            try:
                                # Extract date part from datetime string (before any space)
                                date_part = row_data[field].split(' ')[0]
                                row_data[field] = date_part
                                if debug_mode:
                                    messages.info(request, f"Extracted date part '{date_part}' from '{row_data[field]}' for {field}")
                            except Exception as date_ex:
                                if debug_mode:
                                    messages.warning(request, f"Failed to extract date part from '{row_data[field]}': {str(date_ex)}")
                
                # Create the object with processed data
                instance = model.objects.create(**row_data)
                
                # Post-creation processing
                if model_name == 'specimen':
                    # Generate catalogNumber if missing
                    if not instance.catalogNumber:
                        year = instance.year or ''
                        locality_code = instance.locality.localityCode if instance.locality else ''
                        specimen_number = instance.specimenNumber or ''
                        
                        # Only generate if we have all components
                        if year and locality_code and specimen_number:
                            instance.catalogNumber = f"{year}-{locality_code}-{specimen_number}"
                            instance.save()
                            
                            if debug_mode:
                                messages.info(request, f"Auto-generated catalogNumber '{instance.catalogNumber}' for row {i+1}")
                
                imported_count += 1
                
            except Exception as e:
                # Handle import error
                error_message = str(e)
                
                # Create a user-friendly error message
                user_message = f"Error in row {i+1}: "
                
                # Handle common error types
                if "violates not-null constraint" in error_message:
                    field_match = re.search(r'column "([^"]+)"', error_message)
                    field_name = field_match.group(1) if field_match else "unknown field"
                    user_message += f"The field '{field_name}' cannot be empty"
                
                elif "value too long for type" in error_message:
                    field_match = re.search(r'column "([^"]+)"', error_message)
                    field_name = field_match.group(1) if field_match else "unknown field"
                    user_message += f"The value for '{field_name}' is too long"
                    
                elif "duplicate key value violates unique constraint" in error_message:
                    user_message += "This record has a duplicate value for a unique field"
                
                elif "invalid date format" in error_message:
                    field_match = re.search(r'column "([^"]+)"', error_message)
                    field_name = field_match.group(1) if field_match else "date field"
                    user_message += f"Invalid date format for '{field_name}'. Please ensure it's in YYYY-MM-DD format"
                    
                else:
                    # Default to simplified error message
                    user_message += f"Could not import - {error_message}"
                
                # Log the error
                messages.error(request, user_message)
                
                # Store in session for display after redirect
                import_errors = request.session.get('import_errors', [])
                import_errors.append(user_message)
                request.session['import_errors'] = import_errors
                
                # Add technical details in debug mode
                if debug_mode:
                    debug_message = f"Technical details for row {i+1}: {error_message}"
                    import_errors.append(debug_message)
                
                skipped_count += 1
        
        # Prepare summary message
        if imported_count > 0:
            messages.success(
                request, 
                f'Successfully imported {imported_count} records '
                f'({skipped_count} skipped due to errors).'
            )
        else:
            messages.error(request, 'No records were imported successfully.')
        
        # Handle import errors - make sure they appear on the list page
        import_errors = request.session.get('import_errors', [])
        if import_errors:
            request.session['import_complete'] = True
            # Don't add this warning message as we'll show detailed errors on the list page
            # messages.warning(request, f'There were {len(import_errors)} errors during import. See details below.')
        else:
            # Clear any previous import state
            request.session['import_complete'] = False
            if 'import_errors' in request.session:
                del request.session['import_errors']
        
        # Save the session before redirecting
        request.session.modified = True
        
        # Redirect to the list view
        return redirect('dynamic_list', model_name=model_name)
    
    # Render initial import form
    return render(request, 'butterflies/import_model.html', context)

# --- List View for All Models ---

@admin_required
def debug_bulk_delete_specimen(request):
    """
    Debug feature to bulk delete specimens.
    Provides a confirmation screen and requires typing "DELETE" to confirm.
    This is a debug-only feature and should be used with caution.
    Requires admin privileges.
    
    Parameters:
        request: HTTP request object
    Returns:
        Confirmation page or redirect to specimen list after deletion
    """
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '')
        if confirm_text == 'DELETE':
            # Perform the bulk delete
            count = Specimen.objects.all().count()
            Specimen.objects.all().delete()
            messages.success(request, f"Successfully deleted {count} specimen records.")
            return redirect('dynamic_list', model_name='specimen')
        else:
            messages.error(request, "Confirmation text did not match. Deletion canceled.")
            return redirect('dynamic_list', model_name='specimen')
    
    # GET request - show confirmation page
    count = Specimen.objects.all().count()
    context = {
        'count': count,
    }
    return render(request, 'butterflies/bulk_delete_confirm.html', context)

def all_list(request):
    """
    Display objects from all models in the butterflies app.
    Supports multi-field search across all models.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered template with tables for all models
    """
    app_models = apps.get_app_config('butterflies').get_models()
    model_tables = []
    for model in app_models:
        # Get all objects for the model
        objects = model.objects.all()
        # Get all fields except id
        fields = [
            {'name': field.name, 'verbose_name': getattr(field, 'verbose_name', field.name)}
            for field in model._meta.fields
            if field.name != 'id'
        ]
        # Multi-field search for each model
        for field in fields:
            value = request.GET.get(field['name'])
            if value:
                objects = objects.filter(**{f"{field['name']}__icontains": value})
        # Attach model_name to each object for template use
        obj_list = []
        for obj in objects:
            obj.model_name_internal = model._meta.model_name
            obj_list.append(obj)
        model_tables.append({
            'model_name': model._meta.verbose_name.title(),
            'model_name_internal': model._meta.model_name,
            'objects': obj_list,
            'fields': fields,
        })
    return render(request, 'butterflies/all_list.html', {
        'model_tables': model_tables,
        'request': request,
    })

# --- Legacy/Deprecated Views ---

def showdetails(request, template, model=None):
    """
    Legacy view to show details for all objects of a model.
    
    Parameters:
        request: HTTP request object
        template: Template to render
        model: Django model class (must be provided)
    Returns:
        Rendered template with objects and their fields
    
    Note: This function requires 'model' to be passed as a parameter,
    otherwise it will raise an error. Consider using dynamic_list instead.
    """
    if model is None:
        raise ValueError("Model parameter is required")
        
    objects = model.objects.all()
    
    for object in objects:
        object.fields = dict((field.name, field.value_to_string(object))
                            for field in object._meta.fields)
    
# --- Authentication Views ---
def custom_logout(request):
    """
    Custom logout view that supports both GET and POST requests.
    Logs out the user and redirects to the logged_out template.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered logged_out template
    """
    logout(request)
    return render(request, 'butterflies/auth/logged_out.html')