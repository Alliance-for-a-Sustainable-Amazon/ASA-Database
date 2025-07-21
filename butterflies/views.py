from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import ButterflyCollection, Trap
from .forms import ButterflyCollectionForm, TrapForm

def create_butterfly(request):
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
    model = ButterflyCollection
    template_name = 'butterflies/butterfly_list.html'
    context_object_name = 'butterflies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in ButterflyCollection._meta.fields
            if field.name != 'id'
        ]
        context['fields'] = fields
        return context

class TrapListView(ListView):
    model = Trap
    template_name = 'butterflies/trap_list.html'
    context_object_name = 'traps'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in Trap._meta.fields
            if field.name != 'id'
        ]
        context['fields'] = fields
        return context

def all_list(request):
    butterflies = ButterflyCollection.objects.all()
    traps = Trap.objects.all()
    species = request.GET.get('species')
    trap_name = request.GET.get('trap_name')
    if species:
        butterflies = butterflies.filter(species__icontains=species)
    if trap_name:
        traps = traps.filter(name__icontains=trap_name)
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
    return render(request, 'butterflies/all_list.html', {
        'butterflies': butterflies,
        'traps': traps,
        'butterfly_fields': butterfly_fields,
        'trap_fields': trap_fields,
    })

def showdetails(request, template):
    objects = model.objects.all()

    for object in objects:
        object.fields = dict((field.name, field.value_to_string(object))
                                            for field in object._meta.fields)

    return render(template, { 'objects':objects })