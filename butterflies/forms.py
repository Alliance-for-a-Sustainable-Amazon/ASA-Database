
# forms.py
# Defines Django ModelForm classes for butterfly collections and traps.
# These forms are used in views to handle user input and validation.

from django import forms
from .models import ButterflyCollection, Trap

class ButterflyCollectionForm(forms.ModelForm):
    """
    Form for creating and editing ButterflyCollection instances.
    Fields:
        - species: Name of the butterfly species
        - collection_date: Date and time the butterfly was collected
        - collector_name: Name of the person who collected the butterfly
        - notes: Optional notes about the collection
    """
    class Meta:
        model = ButterflyCollection
        fields = ['species', 'collection_date', 'collector_name', 'notes']

class TrapForm(forms.ModelForm):
    """
    Form for creating and editing Trap instances.
    Fields:
        - name: Unique name/identifier for the trap
        - location_description: Description of the trap's location
        - setup_date: Date the trap was set up
        - notes: Optional notes about the trap
    """
    class Meta:
        model = Trap
        fields = ['name', 'location_description', 'setup_date', 'notes']
