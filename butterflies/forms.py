from django import forms
from .models import ButterflyCollection, Trap

class ButterflyCollectionForm(forms.ModelForm):
    class Meta:
        model = ButterflyCollection
        fields = ['species', 'collection_date', 'collector_name', 'notes']

class TrapForm(forms.ModelForm):
    class Meta:
        model = Trap
        fields = ['name', 'location_description', 'setup_date', 'notes']
