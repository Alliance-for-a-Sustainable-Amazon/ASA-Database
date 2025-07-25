
# forms.py
# Defines Django ModelForm classes for butterfly collections and traps.
# These forms are used in views to handle user input and validation.

from django import forms
from .models import Initials, Locality, Specimen

# --- Forms for Biological Specimen Database ---
class InitialsForm(forms.ModelForm):
    class Meta:
        model = Initials
        fields = '__all__'

class LocalityForm(forms.ModelForm):
    class Meta:
        model = Locality
        fields = '__all__'


# Custom SpecimenForm with append-only logic for 'modified' field
class SpecimenForm(forms.ModelForm):
    # Extra fields for the 'modified' entry
    mod_month = forms.CharField(max_length=2, required=False, label="Modification Month")
    mod_day = forms.CharField(max_length=2, required=False, label="Modification Day")
    mod_year = forms.CharField(max_length=4, required=False, label="Modification Year")
    mod_initials = forms.ModelChoiceField(queryset=Initials.objects.all(), required=False, label="Modification Initials")
    mod_description = forms.CharField(max_length=255, required=False, label="Modification Description")

    class Meta:
        model = Specimen
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        # If any mod fields are filled, append to 'modified' field
        mod_fields = [
            self.cleaned_data.get('mod_month'),
            self.cleaned_data.get('mod_day'),
            self.cleaned_data.get('mod_year'),
            str(self.cleaned_data.get('mod_initials') or ''),
            self.cleaned_data.get('mod_description')
        ]
        if any(mod_fields):
            entry = ','.join([f or '' for f in mod_fields])
            if instance.modified:
                instance.modified += f';{entry}'
            else:
                instance.modified = entry
        if commit:
            instance.save()
            self.save_m2m()
        return instance
