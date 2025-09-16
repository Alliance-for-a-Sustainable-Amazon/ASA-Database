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
    
    # Find unique field for duplicate detection
    unique_field = None
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
            # Check foreign key fields across all rows
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
            
            # Track invalid sex values
            for row_data in all_rows_data:
                if 'sex' in row_data and row_data['sex']:
                    if row_data['sex'] not in ['male', 'female', '.']:
                        if 'sex_values' not in common_errors:
                            common_errors['sex_values'] = set()
                        common_errors['sex_values'].add(row_data['sex'])
                        
                # Track invalid foreign keys
                for fk_field in fk_fields_validation:
                    if fk_field in row_data and row_data[fk_field]:
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
                if model.objects.filter(**{unique_field: unique_value}).exists():
                    is_duplicate = True
                    # Generate suggested unique value with suffix
                    counter = 2
                    while model.objects.filter(**{unique_field: f"{unique_value}-{counter}"}).exists():
                        counter += 1
                    suggested_key = f"{unique_value}-{counter}"
            
            # Create preview item
            preview_item = {
                'data': row_data,
                'duplicate': is_duplicate,
                'suggested_key': suggested_key,
                'warnings': [],  # Store any format warnings here
                'errors': [],    # Store validation errors here that must be fixed
                'error_fields': set()  # Track fields with errors for highlighting
            }
            
            # Check for potential format issues
            if model_name == 'specimen':
                # Check date fields with improved validation
                date_fields = ['eventDate', 'dateIdentified', 'georeferencedDate']
                for date_field in date_fields:
                    if date_field in row_data and row_data[date_field]:
                        original_value = row_data[date_field]
                        try:
                            # Try parsing the date
                            date_obj = None
                            try:
                                date_obj = date_parser.parse(str(original_value)).date()
                                # # Show how the date will look when formatted for display
                                # formatted = format_date_value(date_obj)
                                # preview_item['warnings'].append(
                                #     f"Date '{original_value}' will be stored as '{date_obj}' and displayed as '{formatted}'"
                                # )
                            except:
                                preview_item['warnings'].append(
                                    f"Could not parse date '{original_value}' for {date_field}"
                                )
                        except Exception as e:
                            preview_item['warnings'].append(
                                f"Invalid date format '{original_value}' for {date_field}: {str(e)}"
                            )
                
                # Check boolean fields
                if 'exact_loc' in row_data and row_data['exact_loc']:
                    value = str(row_data['exact_loc']).upper()
                    if value not in ['TRUE', 'FALSE']:
                        preview_item['warnings'].append(
                            f"Value '{row_data['exact_loc']}' for exact_loc will be converted to TRUE/FALSE"
                        )
                
                # Perform strict validation checks for fields that must be valid
                if model_name == 'specimen':
                    # Validate foreign key fields using our pre-cached data
                    fk_fields_validation = {
                        'locality': (Locality, 'localityCode', 'Locality'),
                        'recordedBy': (Initials, 'initials', 'Initials'),
                        'georeferencedBy': (Initials, 'initials', 'Initials'),
                        'identifiedBy': (Initials, 'initials', 'Initials')
                    }
                    
                    for fk_field, (related_model, lookup_field, display_name) in fk_fields_validation.items():
                        if fk_field in row_data and row_data[fk_field]:
                            lookup_value = row_data[fk_field]
                            key = f"{fk_field}_invalid"
                            
                            # Check if this value is in our pre-identified invalid values
                            if key in common_errors and lookup_value in common_errors[key]:
                                error_msg = f"Invalid {display_name}: '{lookup_value}' does not exist in the database"
                                preview_item['errors'].append(error_msg)
                                preview_item['error_fields'].add(fk_field)
                            else:
                                # Double-check in the database in case we missed something
                                if not related_model.objects.filter(**{lookup_field: lookup_value}).exists():
                                    error_msg = f"Invalid {display_name}: '{lookup_value}' does not exist in the database"
                                    preview_item['errors'].append(error_msg)
                                    preview_item['error_fields'].add(fk_field)
                    
                    # Validate sex field using pre-identified invalid values
                    if 'sex' in row_data and row_data['sex']:
                        if 'sex_values' in common_errors and row_data['sex'] in common_errors['sex_values']:
                            error_msg = f"Invalid sex: '{row_data['sex']}'. Must be 'male', 'female', or '.'"
                            preview_item['errors'].append(error_msg)
                            preview_item['error_fields'].add('sex')
                        elif row_data['sex'] not in ['male', 'female', '.']:
                            # Double-check in case we missed something in pre-validation
                            error_msg = f"Invalid sex: '{row_data['sex']}'. Must be 'male', 'female', or '.'"
                            preview_item['errors'].append(error_msg)
                            preview_item['error_fields'].add('sex')
                    
                    # Check required fields for catalogNumber generation
                    # (Only flag as error if catalogNumber is not provided but components are missing)
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
                            preview_item['errors'].append(error_msg)
                            for field in missing_components:
                                preview_item['error_fields'].add(field)
            
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
            # Check foreign key fields across all rows
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
                if model.objects.filter(**{unique_field: unique_value}).exists():
                    is_duplicate = True
                    # Generate suggested unique value with suffix
                    counter = 2
                    while model.objects.filter(**{unique_field: f"{unique_value}-{counter}"}).exists():
                        counter += 1
                    suggested_key = f"{unique_value}-{counter}"
            
            # Create preview item
            preview_item = {
                'data': row_data,
                'duplicate': is_duplicate,
                'suggested_key': suggested_key,
                'warnings': [],  # Store any format warnings here
                'errors': [],    # Store validation errors here that must be fixed
                'error_fields': set()  # Track fields with errors for highlighting
            }
            
            # Perform the same validation as in the file upload case
            # Add validation code here - same as in the file upload case
            if model_name == 'specimen':
                # Validate foreign key fields using our pre-cached data
                fk_fields_validation = {
                    'locality': (Locality, 'localityCode', 'Locality'),
                    'recordedBy': (Initials, 'initials', 'Initials'),
                    'georeferencedBy': (Initials, 'initials', 'Initials'),
                    'identifiedBy': (Initials, 'initials', 'Initials')
                }
                
                for fk_field, (related_model, lookup_field, display_name) in fk_fields_validation.items():
                    if fk_field in row_data and row_data[fk_field]:
                        lookup_value = row_data[fk_field]
                        key = f"{fk_field}_invalid"
                        
                        # Check if this value is in our pre-identified invalid values
                        if key in common_errors and lookup_value in common_errors[key]:
                            error_msg = f"Invalid {display_name}: '{lookup_value}' does not exist in the database"
                            preview_item['errors'].append(error_msg)
                            preview_item['error_fields'].add(fk_field)
                
                # Validate sex field
                if 'sex' in row_data and row_data['sex']:
                    if 'sex_values' in common_errors and row_data['sex'] in common_errors['sex_values']:
                        error_msg = f"Invalid sex: '{row_data['sex']}'. Must be 'male', 'female', or '.'"
                        preview_item['errors'].append(error_msg)
                        preview_item['error_fields'].add('sex')
                
                # Check required fields for catalogNumber generation
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
                        preview_item['errors'].append(error_msg)
                        for field in missing_components:
                            preview_item['error_fields'].add(field)
            
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
        renamed_count = 0
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
                # Handle duplicate values in unique fields
                if unique_field and row_data.get(unique_field):
                    original_value = row_data[unique_field]
                    if original_value and model.objects.filter(**{unique_field: original_value}).exists():
                        # Add suffix to make value unique
                        counter = 2
                        while model.objects.filter(**{unique_field: f"{original_value}-{counter}"}).exists():
                            counter += 1
                        
                        # Update with new unique value
                        row_data[unique_field] = f"{original_value}-{counter}"
                        renamed_count += 1
                        messages.info(request, f'Renamed duplicate "{original_value}" to "{row_data[unique_field]}"')
                
                # Model-specific conversions
                if model_name == 'specimen':
                    # Process foreign key fields
                    fk_fields = {
                        'locality': (Locality, 'localityCode'),
                        'recordedBy': (Initials, 'initials'),
                        'georeferencedBy': (Initials, 'initials'),
                        'identifiedBy': (Initials, 'initials')
                    }
                    
                    for fk_field, (related_model, lookup_field) in fk_fields.items():
                        if fk_field in row_data and row_data[fk_field]:
                            lookup_value = row_data[fk_field]
                            related_obj = related_model.objects.filter(**{lookup_field: lookup_value}).first()
                            if related_obj:
                                row_data[fk_field] = related_obj
                            else:
                                row_data[fk_field] = None
                                messages.warning(
                                    request, 
                                    f"{related_model.__name__} '{lookup_value}' not found for {fk_field} in row {i+1}."
                                )
                    
                    # Convert date fields from string to date objects
                    date_fields = ['eventDate', 'dateIdentified', 'georeferencedDate']
                    for field in date_fields:
                        if field in row_data and row_data[field]:
                            try:
                                # Parse string date to Python date object
                                date_value = None
                                
                                # Try direct parsing with dateutil
                                try:
                                    date_value = date_parser.parse(str(row_data[field])).date()
                                except:
                                    # If direct parsing fails, try our standard format
                                    try:
                                        date_value = parse_date_value(row_data[field])
                                    except:
                                        date_value = None
                                
                                if date_value:
                                    row_data[field] = date_value
                                    if debug_mode:
                                        messages.info(request, f"Converted date for {field} from '{row_data[field]}' to '{date_value}'")
                                else:
                                    row_data[field] = None
                                    if debug_mode:
                                        messages.warning(request, f"Could not parse date '{row_data[field]}' for {field}, set to None")
                            except Exception as e:
                                # If parsing fails, log warning and set to None
                                row_data[field] = None
                                if debug_mode:
                                    messages.warning(request, f"Error parsing date for {field}: {str(e)}")
                    
                    # Construct eventDate from components if missing
                    if not row_data.get('eventDate'):
                        day = row_data.get('day')
                        month = row_data.get('month')
                        year = row_data.get('year')
                        if day and month and year:
                            # First try to create a valid date to check if components make sense
                            try:
                                # Try to create a datetime object to validate the date
                                temp_date_str = f"{year}-{month}-{day}"
                                date_obj = None
                                
                                # Try parsing with various month formats
                                try:
                                    # If month is a number (1-12)
                                    if month.isdigit() and 1 <= int(month) <= 12:
                                        date_obj = datetime.date(int(year), int(month), int(day))
                                    else:
                                        # Try abbreviated and full month names
                                        for fmt in ["%Y-%b-%d", "%Y-%B-%d"]:
                                            try:
                                                date_obj = datetime.datetime.strptime(temp_date_str, fmt).date()
                                                break
                                            except ValueError:
                                                continue
                                except:
                                    pass
                                
                                if date_obj:
                                    # Store as date object
                                    row_data['eventDate'] = date_obj
                                    if debug_mode:
                                        messages.info(request, f"Generated eventDate '{format_date_value(date_obj)}' from components: {day} {month} {year}")
                                else:
                                    # Fallback to parsing a string
                                    date_str = f"{day} {month}, {year}"
                                    parsed_date = parse_date_value(date_str)
                                    if parsed_date:
                                        row_data['eventDate'] = parsed_date
                                    else:
                                        row_data['eventDate'] = None
                                    if debug_mode:
                                        messages.warning(request, f"Using string parsing for eventDate: '{date_str}' -> {parsed_date}")
                            except Exception as e:
                                # Log error and set to None
                                row_data['eventDate'] = None
                                if debug_mode:
                                    messages.warning(request, f"Error validating date components: {str(e)}. Using: '{row_data['eventDate']}'")
                        elif debug_mode and (day or month or year):
                            # Warn about incomplete date components
                            messages.warning(request, f"Incomplete date components for row {i+1}: day={day}, month={month}, year={year}")
                    
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
            if renamed_count > 0:
                messages.success(
                    request, 
                    f'Successfully imported {imported_count} records '
                    f'({renamed_count} with modified unique keys, {skipped_count} skipped due to errors).'
                )
            else:
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