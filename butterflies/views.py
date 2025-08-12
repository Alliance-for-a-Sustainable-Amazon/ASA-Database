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
import csv
import io
import openpyxl
import pandas as pd
# App-specific imports
from .models import Specimen, Locality, Initials
from .forms import SpecimenForm, LocalityForm, InitialsForm
from .utils import dot_if_none

# --- Utility Functions ---
def model_list():
    """
    Return all models in the butterflies app.
    """
    return list(apps.get_app_config('butterflies').get_models())

# --- Generic CRUD Views ---
def dynamic_list(request, model_name):
    """
    Generic dynamic list view for any model.
    Displays all objects for the specified model with filtering capabilities.
    
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
    return render(request, 'butterflies/dynamic_list.html', {
        'objects': obj_list,
        'fields': fields,
        'model_name': model._meta.verbose_name.title(),
        'model_name_internal': model._meta.model_name,
        'request': request,
        'home_url': 'report_table',
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

def dynamic_delete(request, model_name, object_id):
    """
    Generic delete view for any model.
    Shows confirmation page before deleting an object.
    
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

def dynamic_create_edit(request, model_name, object_id=None):
    """
    Generic create/edit view for any model using the organized form approach.
    Uses the organized form template for Specimen model.
    
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
    
    # Use appropriate form class based on model
    if model._meta.model_name == 'specimen':
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

def create_specimen(request):
    """
    Create a new Specimen object using the organized form layout.
    Handles both form display and processing.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered organized form template with success message on submission
    """
    form = SpecimenForm()
    if request.method == 'POST':
        form = SpecimenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Specimen added successfully!')
            form = SpecimenForm()
    return render(request, 'butterflies/specimen_form.html', {'form': form})

def create_locality(request):
    """
    Create a new Locality object.
    Handles both form display and processing.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered form template with success message on submission
    """
    form = LocalityForm()
    if request.method == 'POST':
        form = LocalityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Locality added successfully!')
            form = LocalityForm()
    return render(request, 'butterflies/locality_form.html', {'form': form})

def create_initials(request):
    """
    Create a new Initials object.
    Handles both form display and processing.
    
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

def report_table(request):
    """
    Display all specimens with related data in a report table.
    Includes links for export functionality.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered template with specimens and export URLs
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
        'localityDescriptionNotes', 'country', 'stateProvince', 'county', 'municipality',
        
        # 3. Occurrence Fields
        'specimenNumber', 'catalogNumber', 'recordedBy', 'sex', 
        'uploaded_iNaturalist', 'behavior', 'occurrenceRemarks', 'disposition',
        
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
            specimen.uploaded_iNaturalist,
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
            specimen.localityDescriptionNotes,
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
        'localityDescriptionNotes', 'country', 'stateProvince', 'county', 'municipality',
        
        # 3. Occurrence Fields
        'specimenNumber', 'catalogNumber', 'recordedBy', 'sex', 
        'uploaded_iNaturalist', 'behavior', 'occurrenceRemarks', 'disposition',
        
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
            specimen.uploaded_iNaturalist,
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
            specimen.localityDescriptionNotes,
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
def import_model(request, model_name):
    """
    Generic function to import data for any model from CSV or Excel file.
    
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
                context['error'] = 'Unsupported file type. Please upload a CSV or Excel file.'
                return render(request, 'butterflies/import_model.html', context)
        except Exception as e:
            context['error'] = f'Error reading file: {str(e)}'
            return render(request, 'butterflies/import_model.html', context)
        
        # Validate columns
        required_fields = [f.name for f in model._meta.fields if f.name != 'id']
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
                model.objects.create(**data)
                imported_count += 1
            except Exception:
                skipped_count += 1
                
        if renamed_count > 0:
            messages.success(request, f'Successfully imported {imported_count} records ({renamed_count} with modified unique keys, {skipped_count} skipped due to errors).')
        else:
            messages.success(request, f'Successfully imported {imported_count} records ({skipped_count} skipped due to errors).')
        return redirect('dynamic_list', model_name=model_name)
    
    return render(request, 'butterflies/import_model.html', context)

# --- List View for All Models ---

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
    
    return render(template, {'objects': objects})