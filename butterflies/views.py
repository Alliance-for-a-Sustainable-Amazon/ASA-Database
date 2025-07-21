def dynamic_list(request, model_name):
    """
    Generic dynamic list view for any model.
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
    })
def dynamic_detail(request, model_name, object_id):
    """
    Generic detail view for any model.
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
        return redirect(reverse('all_list'))
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
from django.forms import modelform_factory
from django.http import Http404

def model_list():
    """Return all models in the butterflies app."""
    return list(apps.get_app_config('butterflies').get_models())

def dynamic_create_edit(request, model_name, object_id=None):
    """
    Generic create/edit view for any model.
    Uses modelform_factory to generate the form dynamically.
    """
    model = None
    for m in model_list():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
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
            from django.urls import reverse
            return redirect(reverse('all_list'))
    else:
        form = form_class(instance=instance)
    return render(request, 'butterflies/_form.html', {'form': form, 'model_name': model._meta.verbose_name.title()})

# views.py
# Contains view functions and class-based views for the butterflies app.
# Handles HTTP requests and responses for butterfly collections and traps.

from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import ButterflyCollection, Trap
from .forms import ButterflyCollectionForm, TrapForm


def create_butterfly(request):
    """
    View for creating a new butterfly collection event.
    Handles GET (show empty form) and POST (process submitted form) requests.
    On successful submission, saves the new collection and displays a success message.
    """
    from django.contrib import messages
    form = ButterflyCollectionForm()
    if request.method == 'POST':
        form = ButterflyCollectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Butterfly collection added successfully!')
            form = ButterflyCollectionForm()  # reset form after success
    return render(request, 'butterflies/butterfly_form.html', {'form': form})


def create_trap(request):
    """
    View for creating a new trap.
    Handles GET (show empty form) and POST (process submitted form) requests.
    On successful submission, saves the new trap and displays a success message.
    """
    from django.contrib import messages
    form = TrapForm()
    if request.method == 'POST':
        form = TrapForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trap added successfully!')
            form = TrapForm()  # reset form after success
    return render(request, 'butterflies/trap_form.html', {'form': form})



class ButterflyListView(ListView):
    """
    Displays a list of all butterfly collection events.
    Uses a template to render the list and provides field metadata for display.
    """
    model = ButterflyCollection
    template_name = 'butterflies/butterfly_list.html'
    context_object_name = 'butterflies'

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in ButterflyCollection._meta.fields:
            if field.name == 'id':
                continue
            value = self.request.GET.get(field.name)
            if value:
                queryset = queryset.filter(**{f"{field.name}__icontains": value})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in ButterflyCollection._meta.fields
            if field.name != 'id'
        ]
        # Attach model_name to each object for template use
        obj_list = []
        for obj in context['butterflies']:
            obj.model_name = ButterflyCollection._meta.model_name
            obj_list.append(obj)
        context['butterflies'] = obj_list
        context['fields'] = fields
        context['request'] = self.request
        return context

class TrapListView(ListView):
    """
    Displays a list of all traps used for butterfly collection.
    Uses a template to render the list and provides field metadata for display.
    """
    model = Trap
    template_name = 'butterflies/trap_list.html'
    context_object_name = 'traps'

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in Trap._meta.fields:
            if field.name == 'id':
                continue
            value = self.request.GET.get(field.name)
            if value:
                queryset = queryset.filter(**{f"{field.name}__icontains": value})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in Trap._meta.fields
            if field.name != 'id'
        ]
        # Attach model_name to each object for template use
        obj_list = []
        for obj in context['traps']:
            obj.model_name = Trap._meta.model_name
            obj_list.append(obj)
        context['traps'] = obj_list
        context['fields'] = fields
        context['request'] = self.request
        return context

from django.apps import apps

def all_list(request):
    # Dynamically get all models in the butterflies app
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

def showdetails(request, template):
    objects = model.objects.all()

    for object in objects:
        object.fields = dict((field.name, field.value_to_string(object))
                                            for field in object._meta.fields)

    return render(template, { 'objects':objects })