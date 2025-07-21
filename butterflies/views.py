
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
        context['fields'] = fields
        context['request'] = self.request
        return context

def all_list(request):
    butterflies = ButterflyCollection.objects.all()
    traps = Trap.objects.all()
    butterfly_fields = [
        {'name': field.name, 'verbose_name': field.verbose_name}
        for field in ButterflyCollection._meta.fields
        if field.name != 'id'
    ]
    trap_fields = [
        {'name': field.name, 'verbose_name': field.verbose_name}
        for field in Trap._meta.fields
        if field.name != 'id'
    ]

    # Multi-field search for butterflies
    for field in butterfly_fields:
        value = request.GET.get(field['name'])
        if value:
            butterflies = butterflies.filter(**{f"{field['name']}__icontains": value})

    # Multi-field search for traps
    for field in trap_fields:
        value = request.GET.get(field['name'])
        if value:
            traps = traps.filter(**{f"{field['name']}__icontains": value})

    return render(request, 'butterflies/all_list.html', {
        'butterflies': butterflies,
        'traps': traps,
        'butterfly_fields': butterfly_fields,
        'trap_fields': trap_fields,
        'request': request,
    })

def showdetails(request, template):
    objects = model.objects.all()

    for object in objects:
        object.fields = dict((field.name, field.value_to_string(object))
                                            for field in object._meta.fields)

    return render(template, { 'objects':objects })