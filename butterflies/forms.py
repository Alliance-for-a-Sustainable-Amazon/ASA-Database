
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

# Clean, explicit SpecimenForm
class SpecimenForm(forms.ModelForm):
    # Disposition mini-fields (not part of model)
    disp_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Disposition Day"
    )
    disp_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Disposition Month"
    )
    disp_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Disposition Year"
    )
    disp_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Disposition Initials"
    )
    disp_description = forms.CharField(
        max_length=255,
        required=False,
        label="Disposition Description"
    )

    class Meta:
        model = Specimen
        exclude = ['disposition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make catalogNumber field disabled and styled for display only
        self.fields['catalogNumber'].disabled = True
        self.fields['catalogNumber'].widget.attrs['style'] = 'background-color: #eee; color: #888;'
        self.fields['catalogNumber'].widget.attrs['placeholder'] = '(auto generated)'

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Append-only logic for disposition
        disp_day = self.cleaned_data.get('disp_day')
        disp_month = self.cleaned_data.get('disp_month')
        disp_year = self.cleaned_data.get('disp_year')
        disp_initials = self.cleaned_data.get('disp_initials')
        disp_description = self.cleaned_data.get('disp_description')
        if disp_day and disp_month and disp_year and disp_initials and disp_description:
            entry = f"{disp_day} {disp_month} {disp_year}, {disp_initials}, {disp_description}".strip()
            if instance.disposition:
                instance.disposition += f";{entry}"
            else:
                instance.disposition = entry
        if commit:
            instance.save()
            self.save_m2m()
        return instance
