from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import ButterflyCollection, Trap
from .forms import ButterflyCollectionForm, TrapForm

def create_butterfly(request):
    if request.method == 'POST':
        form = ButterflyCollectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('butterfly_list')
    else:
        form = ButterflyCollectionForm()
    return render(request, 'butterflies/butterfly_form.html', {'form': form})

def create_trap(request):
    if request.method == 'POST':
        form = TrapForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_trap')  # Optionally redirect elsewhere
    else:
        form = TrapForm()
    return render(request, 'butterflies/trap_form.html', {'form': form})


class ButterflyListView(ListView):
    model = ButterflyCollection
    template_name = 'butterflies/butterfly_list.html'
    context_object_name = 'butterflies'

class TrapListView(ListView):
    model = Trap
    template_name = 'butterflies/trap_list.html'
    context_object_name = 'traps'

def all_list(request):
    butterflies = ButterflyCollection.objects.all()
    traps = Trap.objects.all()
    species = request.GET.get('species')
    trap_name = request.GET.get('trap_name')
    if species:
        butterflies = butterflies.filter(species__icontains=species)
    if trap_name:
        traps = traps.filter(name__icontains=trap_name)
    return render(request, 'butterflies/all_list.html', {'butterflies': butterflies, 'traps': traps})

def showdetails(request, template):
    objects = model.objects.all()

    for object in objects:
        object.fields = dict((field.name, field.value_to_string(object))
                                            for field in object._meta.fields)

    return render(template, { 'objects':objects })