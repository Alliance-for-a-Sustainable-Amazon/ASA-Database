# views_organized.py
# DEPRECATED - This file is no longer used. All functionality has been merged into views.py
# The organized form layout is now the default approach throughout the application.

from django.shortcuts import render
from django.contrib import messages
from .forms_organized import SpecimenForm as OrganizedSpecimenForm
from .views import model_list  # Reuse the model_list function from views.py

def create_specimen_organized(request):
    """
    Create a new Specimen object with an organized form layout.
    Handles both form display and processing.
    
    Parameters:
        request: HTTP request object
    Returns:
        Rendered organized form template with success message on submission
    """
    # Create a new form instance
    form = OrganizedSpecimenForm()
    
    if request.method == 'POST':
        form = OrganizedSpecimenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Specimen added successfully!')
            form = OrganizedSpecimenForm()
    
    # Use the form from forms_organized.py
    return render(request, 'butterflies/specimen_form_organized.html', {'form': form})

def dynamic_create_edit_organized(request, model_name, object_id=None):
    """
    Generic create/edit view for any model with the organized template.
    Uses the organized form template for Specimen model.
    
    Parameters:
        request: HTTP request object
        model_name: String name of the model to create or edit
        object_id: Optional primary key for edit mode
    Returns:
        Rendered form template or redirect to report_table after save
    """
    from django.forms import modelform_factory
    from django.urls import reverse
    from django.http import Http404
    from django.shortcuts import redirect
    # Import forms from forms_organized.py
    from .forms_organized import SpecimenForm as OrganizedSpecimenForm, LocalityForm, InitialsForm
    
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
    
    # Use appropriate form class based on model
    if model._meta.model_name == 'specimen':
        form_class = OrganizedSpecimenForm
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
        template_name = 'butterflies/specimen_form_organized.html'
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
