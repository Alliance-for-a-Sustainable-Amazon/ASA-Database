
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
    # EventDate mini-fields
    event_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 32)],
        required=False,
        label="Event Day"
    )
    event_month = forms.ChoiceField(
        choices=[('', 'Month')] + [(str(m).zfill(2), str(m).zfill(2)) for m in range(1, 13)],
        required=False,
        label="Event Month"
    )
    event_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Event Year"
    )

    # GeoreferencedDate mini-fields
    georef_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 32)],
        required=False,
        label="Georeferenced Day"
    )
    georef_month = forms.ChoiceField(
        choices=[('', 'Month')] + [(str(m).zfill(2), str(m).zfill(2)) for m in range(1, 13)],
        required=False,
        label="Georeferenced Month"
    )
    georef_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Georeferenced Year"
    )
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

    # # Event date mini-fields (not part of model)
    # event_day = forms.ChoiceField(
    #     choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
    #     required=False,
    #     label="Event Day"
    # )
    # event_month = forms.ChoiceField(
    #     choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
    #     required=False,
    #     label="Event Month"
    # )
    # event_year = forms.ChoiceField(
    #     choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
    #     required=False,
    #     label="Event Year"
    # )

    # Specimen date fields as dropdowns
    year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Year"
    )
    month = forms.ChoiceField(
        choices=[('', 'Month')] + [(str(m).zfill(2), str(m).zfill(2)) for m in range(1, 13)],
        required=False,
        label="Month"
    )
    day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(d).zfill(2), str(d).zfill(2)) for d in range(1, 32)],
        required=False,
        label="Day"
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
        # Add Select2 class for searchable dropdowns
        for f in ['disp_day', 'disp_month', 'disp_year', 'year', 'month', 'day', 'event_day', 'event_month', 'event_year', 'georef_day', 'georef_month', 'georef_year']:
            self.fields[f].widget.attrs['class'] = 'select2'

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
                instance.disposition += f"; {entry}"
            else:
                instance.disposition = entry

        # Compile eventDate from dropdowns
        event_day = self.cleaned_data.get('event_day')
        event_month = self.cleaned_data.get('event_month')
        event_year = self.cleaned_data.get('event_year')
        if event_day and event_month and event_year:
            instance.eventDate = f"{event_year}-{event_month}-{event_day}"
        else:
            instance.eventDate = None

        # Compile georeferencedDate from dropdowns
        georef_day = self.cleaned_data.get('georef_day')
        georef_month = self.cleaned_data.get('georef_month')
        georef_year = self.cleaned_data.get('georef_year')
        if georef_day and georef_month and georef_year:
            instance.georeferencedDate = f"{georef_year}-{georef_month}-{georef_day}"
        else:
            instance.georeferencedDate = None

        if commit:
            instance.save()
            self.save_m2m()
        return instance
