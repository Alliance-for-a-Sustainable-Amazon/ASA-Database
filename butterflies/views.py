# views.py
# Consolidated view functions for butterfly collections using the organized form approach.
# All forms now use the organized layout for better usability.

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
# App-specific imports
from .models import Specimen, Locality, Initials
from .forms import SpecimenForm, SpecimenEditForm, LocalityForm, InitialsForm
from .utils import dot_if_none
from .auth_utils import admin_required

# --- Utility Functions ---
def model_list():
    """
    Return all models in the butterflies app.
    """
    return list(apps.get_app_config('butterflies').get_models())

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
        # Clear the session variables after retrieving them
        request.session['import_complete'] = False
        if 'import_errors' in request.session:
            del request.session['import_errors']
    
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
    return render(request, 'butterflies/_detail.html', {
        'object': obj,
        'fields': fields,
        'model_name': model._meta.verbose_name.title(),
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
    Shows a paginated table of specimens with filtering options.
    This is the main dashboard view.
    Requires user authentication.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered template with filtered specimen list
    """
    specimens = Specimen.objects.select_related('locality', 'recordedBy', 'georeferencedBy', 'identifiedBy').all()
    from django.urls import reverse
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
    Requires admin privileges.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to import
    Returns:
        Rendered template for import form, preview, or redirect
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    
    if not model:
        raise Http404("Model not found")
    
    # Get model information safely without exposing _meta in templates
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
            
    # If no unique field is found, check if there are any unique_together constraints
    if not unique_field:
        unique_together = getattr(model._meta, 'unique_together', [])
        if unique_together:
            # For simplicity, we'll just use the first field of the first unique_together constraint
            # A more comprehensive solution would handle multiple fields
            if isinstance(unique_together[0], (list, tuple)) and len(unique_together[0]) > 0:
                unique_field = unique_together[0][0]
            
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        ext = file.name.split('.')[-1].lower()
        
        try:
            if ext == 'csv':
                df = pd.read_csv(file)
            elif ext in ('xls', 'xlsx'):
                df = pd.read_excel(file)
            else:
                messages.error(request, 'Unsupported file type. Please upload a CSV or Excel file.')
                context['error'] = 'Unsupported file type. Please upload a CSV or Excel file.'
                return render(request, 'butterflies/import_model.html', context)
                
            # Check if dataframe is empty
            if df.empty:
                messages.error(request, 'The uploaded file contains no data.')
                context['error'] = 'The uploaded file contains no data.'
                return render(request, 'butterflies/import_model.html', context)
                
        except pd.errors.EmptyDataError:
            messages.error(request, 'The uploaded file is empty.')
            context['error'] = 'The uploaded file is empty.'
            return render(request, 'butterflies/import_model.html', context)
        except pd.errors.ParserError:
            messages.error(request, 'Error parsing the file. Please check the file format.')
            context['error'] = 'Error parsing the file. Please check the file format.'
            return render(request, 'butterflies/import_model.html', context)
        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
            context['error'] = f'Error reading file: {str(e)}'
            return render(request, 'butterflies/import_model.html', context)
        
        # Validate columns
        required_fields = [f.name for f in model._meta.fields if f.name != 'id']
        
        # Special handling for foreign key fields in specimen model
        if model_name == 'specimen':
            # Replace foreign key field names with their expected column names in the import file
            fk_mapping = {
                'locality': 'locality',  # Expected column name for locality.localityCode
                'recordedBy': 'recordedBy',  # Expected column name for recordedBy.initials
                'georeferencedBy': 'georeferencedBy',  # Expected column name for georeferencedBy.initials
                'identifiedBy': 'identifiedBy',  # Expected column name for identifiedBy.initials
            }
            
            # Update required_fields list with mapped field names
            for idx, field in enumerate(required_fields):
                if field in fk_mapping:
                    required_fields[idx] = fk_mapping[field]
        
        # Check for missing required columns
        missing = [f for f in required_fields if f not in df.columns]
        if missing:
            context['error'] = f'Missing columns: {", ".join(missing)}'
            return render(request, 'butterflies/import_model.html', context)
        
        # Check for duplicates and prepare preview
        preview = []
        for _, row in df.iterrows():
            is_duplicate = False
            suggested_key = None
            
            if unique_field and unique_field in row:
                unique_value = row[unique_field]
                if unique_value and model.objects.filter(**{unique_field: unique_value}).exists():
                    is_duplicate = True
                    # Find available suffix (-2, -3, etc.)
                    counter = 2
                    while model.objects.filter(**{unique_field: f"{unique_value}-{counter}"}).exists():
                        counter += 1
                    suggested_key = f"{unique_value}-{counter}"
            
            preview.append({
                'data': row.to_dict(),
                'duplicate': is_duplicate,
                'suggested_key': suggested_key
            })
        
        context['preview'] = preview
        context['fields'] = required_fields
        context['unique_field'] = unique_field
        # Pass the unique field information to the template
        if unique_field:
            context['has_unique_field'] = True
            context['unique_field'] = unique_field
        else:
            context['has_unique_field'] = False
            
        return render(request, 'butterflies/import_model_preview.html', context)
    
    elif request.method == 'POST' and request.POST.get('confirm'):
        # Process imported data
        fields = [f.name for f in model._meta.fields if f.name != 'id']
        rows = int(request.POST.get('row_count', 0))
        
        # Debug mode can be enabled via a hidden field in the form
        debug_mode = request.POST.get('debug_mode') == 'true'
        
        imported_count = 0
        renamed_count = 0
        skipped_count = 0
        
        for i in range(rows):
            data = {f: request.POST.get(f'row_{i}_{f}', '') for f in fields}
            
            # Convert empty strings to None
            for k, v in data.items():
                if v == '':
                    data[k] = None
            
            # Handle duplicates by adding suffix
            if unique_field and data.get(unique_field):
                original_value = data[unique_field]
                if original_value and model.objects.filter(**{unique_field: original_value}).exists():
                    # Find available suffix (-2, -3, etc.)
                    counter = 2
                    while model.objects.filter(**{unique_field: f"{original_value}-{counter}"}).exists():
                        counter += 1
                    
                    # Apply the suffix
                    data[unique_field] = f"{original_value}-{counter}"
                    renamed_count += 1
                    
                    # Log a message about the renamed key
                    messages.info(request, f'Renamed duplicate "{original_value}" to "{data[unique_field]}"')
            
            # Create new record
            try:
                # Handle foreign keys for Specimen model
                if model_name == 'specimen':
                    # Handle locality foreign key
                    if 'locality' in data and data['locality']:
                        try:
                            locality_code = data['locality']
                            locality = Locality.objects.filter(localityCode=locality_code).first()
                            if locality:
                                data['locality'] = locality
                            else:
                                # If locality not found, set to None and log
                                messages.warning(request, f"Locality '{locality_code}' not found for row {i+1}. Setting to None.")
                                data['locality'] = None
                        except Exception as e:
                            messages.warning(request, f"Error processing locality for row {i+1}: {str(e)}")
                            data['locality'] = None
                    
                    # Handle recordedBy foreign key
                    if 'recordedBy' in data and data['recordedBy']:
                        try:
                            initials = data['recordedBy']
                            recorded_by = Initials.objects.filter(initials=initials).first()
                            if recorded_by:
                                data['recordedBy'] = recorded_by
                            else:
                                # If initials not found, set to None and log
                                messages.warning(request, f"Initials '{initials}' not found for recordedBy in row {i+1}. Setting to None.")
                                data['recordedBy'] = None
                        except Exception as e:
                            messages.warning(request, f"Error processing recordedBy for row {i+1}: {str(e)}")
                            data['recordedBy'] = None
                    
                    # Handle georeferencedBy foreign key
                    if 'georeferencedBy' in data and data['georeferencedBy']:
                        try:
                            initials = data['georeferencedBy']
                            georeferenced_by = Initials.objects.filter(initials=initials).first()
                            if georeferenced_by:
                                data['georeferencedBy'] = georeferenced_by
                            else:
                                # If initials not found, set to None and log
                                messages.warning(request, f"Initials '{initials}' not found for georeferencedBy in row {i+1}. Setting to None.")
                                data['georeferencedBy'] = None
                        except Exception as e:
                            messages.warning(request, f"Error processing georeferencedBy for row {i+1}: {str(e)}")
                            data['georeferencedBy'] = None
                    
                    # Handle identifiedBy foreign key
                    if 'identifiedBy' in data and data['identifiedBy']:
                        try:
                            initials = data['identifiedBy']
                            identified_by = Initials.objects.filter(initials=initials).first()
                            if identified_by:
                                data['identifiedBy'] = identified_by
                            else:
                                # If initials not found, set to None and log
                                messages.warning(request, f"Initials '{initials}' not found for identifiedBy in row {i+1}. Setting to None.")
                                data['identifiedBy'] = None
                        except Exception as e:
                            messages.warning(request, f"Error processing identifiedBy for row {i+1}: {str(e)}")
                            data['identifiedBy'] = None
                
                # Handle date fields for Specimen model
                if model_name == 'specimen':
                    # Construct eventDate from day, month, year if provided
                    if 'day' in data and 'month' in data and 'year' in data and all([data['day'], data['month'], data['year']]):
                        data['eventDate'] = f"{data['day']} {data['month']}, {data['year']}"
                    
                    # Construct other date fields similarly
                    if 'dateIdentified' not in data or not data['dateIdentified']:
                        # Try to construct from dateIdentified components if present in the import data
                        date_id_day = data.get('dateIdentified_day')
                        date_id_month = data.get('dateIdentified_month')
                        date_id_year = data.get('dateIdentified_year')
                        if date_id_day and date_id_month and date_id_year:
                            data['dateIdentified'] = f"{date_id_day} {date_id_month}, {date_id_year}"
                
                # Perform validation before trying to create the object
                validation_errors = []
                
                # Validate field lengths
                for field_name, value in data.items():
                    if value is not None and hasattr(model, '_meta'):
                        try:
                            field = model._meta.get_field(field_name)
                            if hasattr(field, 'max_length') and field.max_length is not None:
                                if len(str(value)) > field.max_length:
                                    validation_errors.append(
                                        f"The value '{value}' for field '{field_name}' is too long. "
                                        f"Maximum length is {field.max_length} characters."
                                    )
                                    
                                    # Special handling for exact_loc field
                                    if field_name == 'exact_loc' and model_name == 'specimen':
                                        validation_errors.append(
                                            f"For 'exact_loc', only 'TRUE' or 'FALSE' values are allowed."
                                        )
                        except Exception:
                            # If we can't get field info, skip validation for this field
                            pass
                
                # Additional data validation for specimen model
                if model_name == 'specimen':
                    # Validate specimenNumber (required for catalogNumber generation)
                    if not data.get('specimenNumber'):
                        validation_errors.append(f"Missing specimenNumber, which is needed for catalogNumber generation")
                    
                    # Validate year (required for catalogNumber generation)
                    if not data.get('year'):
                        validation_errors.append(f"Missing year, which is needed for catalogNumber generation")
                        
                    # Validate locality (required for catalogNumber generation)
                    if not data.get('locality'):
                        validation_errors.append(f"Missing locality, which is needed for catalogNumber generation")
                    
                    # Validate exact_loc format
                    if data.get('exact_loc') and data.get('exact_loc') not in ['TRUE', 'FALSE']:
                        validation_errors.append(
                            f"The value '{data.get('exact_loc')}' for 'exact_loc' is invalid. "
                            f"Only 'TRUE' or 'FALSE' are allowed."
                        )
                
                # If there are validation errors, raise an exception to skip this row
                if validation_errors:
                    error_message = f"Row {i+1}: " + "; ".join(validation_errors)
                    messages.error(request, error_message)
                    import_errors = request.session.get('import_errors', [])
                    import_errors.append(error_message)
                    request.session['import_errors'] = import_errors
                    skipped_count += 1
                    continue  # Skip to the next row
                
                # Create the object with processed data
                instance = model.objects.create(**data)
                
                # For Specimen, ensure catalogNumber is generated
                if model_name == 'specimen':
                    if not instance.catalogNumber:
                        # Get the components needed for catalogNumber generation
                        year = instance.year or ''
                        locality_code = instance.locality.localityCode if instance.locality else ''
                        specimen_number = instance.specimenNumber or ''
                        
                        # Generate the catalogNumber
                        instance.catalogNumber = f"{year}-{locality_code}-{specimen_number}"
                        instance.save()
                        
                        if debug_mode:
                            messages.info(request, f"Auto-generated catalogNumber '{instance.catalogNumber}' for row {i+1}")
                
                imported_count += 1
            except Exception as e:
                # Make the error message more user-friendly
                error_message = str(e)
                user_friendly_message = f"<span style='color: #721c24;'><strong>Error importing row {i+1}:</strong> "
                
                # Check for common error types and provide more user-friendly messages
                if "value too long for type character varying" in error_message:
                    # Extract the field length from the error message
                    import re
                    length_match = re.search(r'character varying\((\d+)\)', error_message)
                    max_length = length_match.group(1) if length_match else "unknown"
                    
                    # Try to determine which field caused the error
                    field_name = "unknown field"
                    for field in model._meta.fields:
                        if hasattr(field, 'max_length') and str(field.max_length) == max_length:
                            field_name = field.name
                            break
                    
                    user_friendly_message += f"The value for '{field_name}' is too long. Maximum length is {max_length} characters."
                    
                    # Add specific guidance for exact_loc field
                    if field_name == 'exact_loc':
                        user_friendly_message += " For 'exact_loc', only 'TRUE' or 'FALSE' values are allowed."
                
                elif "null value in column" in error_message and "violates not-null constraint" in error_message:
                    # Extract field name from the error message
                    field_match = re.search(r'column "([^"]+)"', error_message)
                    if field_match:
                        field_name = field_match.group(1)
                        user_friendly_message += f"The field '{field_name}' cannot be empty. Please provide a value."
                    else:
                        user_friendly_message += "A required field is missing. Please ensure all required fields have values."
                
                elif "duplicate key value violates unique constraint" in error_message:
                    user_friendly_message += "This record has a duplicate value for a unique field. Please ensure all unique fields have distinct values."
                
                elif "invalid input syntax" in error_message:
                    user_friendly_message += "The data format is incorrect. Please check the data types of your fields."
                
                else:
                    # For other errors, just use the original message
                    user_friendly_message += error_message
                
                # Complete the error message formatting
                user_friendly_message += "</span>"
                
                # Log the error
                messages.error(request, user_friendly_message)
                
                # Store errors in session to display them on redirect
                import_errors = request.session.get('import_errors', [])
                import_errors.append(user_friendly_message)
                request.session['import_errors'] = import_errors
                
                # If in debug mode, also include the original technical error
                if debug_mode:
                    debug_message = f"Technical details for row {i+1}: {error_message}"
                    import_errors.append(debug_message)
                
                skipped_count += 1
                
        # Prepare summary message
        if renamed_count > 0:
            messages.success(request, f'Successfully imported {imported_count} records ({renamed_count} with modified unique keys, {skipped_count} skipped due to errors).')
        else:
            messages.success(request, f'Successfully imported {imported_count} records ({skipped_count} skipped due to errors).')
        
        # If there were errors during import, make sure they're preserved for display on the redirect
        import_errors = request.session.get('import_errors', [])
        if import_errors:
            # Add a warning message that will be displayed on the list page
            messages.warning(request, f'There were {len(import_errors)} errors during import. See details below.')
            
            # Keep the error messages in session for display
            request.session['import_complete'] = True
            
            # Redirect to the list page for this model
            return redirect('dynamic_list', model_name=model_name)
        else:
            # Clear any previous import errors since this import was successful
            if 'import_errors' in request.session:
                del request.session['import_errors']
            
            # Redirect to the list page for this model
            return redirect('dynamic_list', model_name=model_name)
    
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