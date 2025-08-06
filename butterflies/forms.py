
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
    
    # Modified mini-fields
    mod_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Modified Day"
    )
    mod_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Modified Month"
    )
    mod_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Modified Year"
    )
    mod_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Modified Initials"
    )
    mod_description = forms.CharField(
        max_length=255,
        required=False,
        label="Modification Description"
    )
    
    # Behavior mini-fields
    behavior_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Behavior Day"
    )
    behavior_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Behavior Month"
    )
    behavior_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Behavior Year"
    )
    behavior_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Behavior Initials"
    )
    behavior_description = forms.CharField(
        max_length=255,
        required=False,
        label="Behavior Description"
    )
    
    # OccurrenceRemarks mini-fields
    remarks_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Remarks Day"
    )
    remarks_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Remarks Month"
    )
    remarks_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Remarks Year"
    )
    remarks_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Remarks Initials"
    )
    remarks_description = forms.CharField(
        max_length=255,
        required=False,
        label="Remarks Description"
    )
    
    # HabitatNotes mini-fields
    habitat_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Habitat Day"
    )
    habitat_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Habitat Month"
    )
    habitat_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Habitat Year"
    )
    habitat_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Habitat Initials"
    )
    habitat_description = forms.CharField(
        max_length=255,
        required=False,
        label="Habitat Description"
    )
    
    # SamplingProtocol mini-fields
    protocol_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Protocol Day"
    )
    protocol_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Protocol Month"
    )
    protocol_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Protocol Year"
    )
    protocol_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Protocol Initials"
    )
    protocol_description = forms.CharField(
        max_length=255,
        required=False,
        label="Protocol Description"
    )
    
    # LocalityDescriptionNotes mini-fields
    locality_notes_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Locality Notes Day"
    )
    locality_notes_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Locality Notes Month"
    )
    locality_notes_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Locality Notes Year"
    )
    locality_notes_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Locality Notes Initials"
    )
    locality_notes_description = forms.CharField(
        max_length=255,
        required=False,
        label="Locality Notes Description"
    )
    
    # GeoreferenceProtocol mini-fields
    georef_protocol_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="Georeference Protocol Day"
    )
    georef_protocol_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="Georeference Protocol Month"
    )
    georef_protocol_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="Georeference Protocol Year"
    )
    georef_protocol_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="Georeference Protocol Initials"
    )
    georef_protocol_description = forms.CharField(
        max_length=255,
        required=False,
        label="Georeference Protocol Description"
    )
    
    # IdentificationReferences mini-fields
    id_references_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="ID References Day"
    )
    id_references_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="ID References Month"
    )
    id_references_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="ID References Year"
    )
    id_references_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="ID References Initials"
    )
    id_references_description = forms.CharField(
        max_length=255,
        required=False,
        label="ID References Description"
    )
    
    # IdentificationRemarks mini-fields
    id_remarks_day = forms.ChoiceField(
        choices=[('', 'Day')] + [(str(i), str(i)) for i in range(1, 32)],
        required=False,
        label="ID Remarks Day"
    )
    id_remarks_month = forms.ChoiceField(
        choices=[('', 'Month'), ('Jan.', 'Jan.'), ('Feb.', 'Feb.'), ('Mar.', 'Mar.'), ('Apr.', 'Apr.'), ('May', 'May'), ('Jun.', 'Jun.'), ('Jul.', 'Jul.'), ('Aug.', 'Aug.'), ('Sep.', 'Sep.'), ('Oct.', 'Oct.'), ('Nov.', 'Nov.'), ('Dec.', 'Dec.')],
        required=False,
        label="ID Remarks Month"
    )
    id_remarks_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(y), str(y)) for y in range(1900, 2051)],
        required=False,
        label="ID Remarks Year"
    )
    id_remarks_initials = forms.ModelChoiceField(
        queryset=Initials.objects.all(),
        required=False,
        label="ID Remarks Initials"
    )
    id_remarks_description = forms.CharField(
        max_length=255,
        required=False,
        label="ID Remarks Description"
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
        exclude = ['modified', 'disposition', 'behavior', 'occurrenceRemarks', 'habitatNotes', 'samplingProtocol', 'localityDescriptionNotes', 'georeferenceProtocol', 'identificationReferences', 'identificationRemarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make catalogNumber field disabled and styled for display only
        self.fields['catalogNumber'].disabled = True
        self.fields['catalogNumber'].widget.attrs['style'] = 'background-color: #eee; color: #888;'
        self.fields['catalogNumber'].widget.attrs['placeholder'] = '(auto generated)'
        # Add Select2 class for searchable dropdowns
        select2_fields = [
            'mod_day', 'mod_month', 'mod_year',
            'disp_day', 'disp_month', 'disp_year', 
            'year', 'month', 'day', 
            'event_day', 'event_month', 'event_year', 
            'georef_day', 'georef_month', 'georef_year',
            'behavior_day', 'behavior_month', 'behavior_year',
            'remarks_day', 'remarks_month', 'remarks_year',
            'habitat_day', 'habitat_month', 'habitat_year',
            'protocol_day', 'protocol_month', 'protocol_year',
            'locality_notes_day', 'locality_notes_month', 'locality_notes_year',
            'georef_protocol_day', 'georef_protocol_month', 'georef_protocol_year',
            'id_references_day', 'id_references_month', 'id_references_year',
            'id_remarks_day', 'id_remarks_month', 'id_remarks_year'
        ]
        for f in select2_fields:
            if f in self.fields:
                self.fields[f].widget.attrs['class'] = 'select2'

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Append-only logic for modified
        mod_day = self.cleaned_data.get('mod_day')
        mod_month = self.cleaned_data.get('mod_month')
        mod_year = self.cleaned_data.get('mod_year')
        mod_initials = self.cleaned_data.get('mod_initials')
        mod_description = self.cleaned_data.get('mod_description')
        if mod_day and mod_month and mod_year and mod_initials and mod_description:
            entry = f"{mod_day} {mod_month} {mod_year}, {mod_initials}, {mod_description}".strip()
            if instance.modified:
                instance.modified += f"; {entry}"
            else:
                instance.modified = entry
        
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
        
        # Append-only logic for behavior
        behavior_day = self.cleaned_data.get('behavior_day')
        behavior_month = self.cleaned_data.get('behavior_month')
        behavior_year = self.cleaned_data.get('behavior_year')
        behavior_initials = self.cleaned_data.get('behavior_initials')
        behavior_description = self.cleaned_data.get('behavior_description')
        if behavior_day and behavior_month and behavior_year and behavior_initials and behavior_description:
            entry = f"{behavior_day} {behavior_month} {behavior_year}, {behavior_initials}, {behavior_description}".strip()
            if instance.behavior:
                instance.behavior += f"; {entry}"
            else:
                instance.behavior = entry
                
        # Append-only logic for occurrenceRemarks
        remarks_day = self.cleaned_data.get('remarks_day')
        remarks_month = self.cleaned_data.get('remarks_month')
        remarks_year = self.cleaned_data.get('remarks_year')
        remarks_initials = self.cleaned_data.get('remarks_initials')
        remarks_description = self.cleaned_data.get('remarks_description')
        if remarks_day and remarks_month and remarks_year and remarks_initials and remarks_description:
            entry = f"{remarks_day} {remarks_month} {remarks_year}, {remarks_initials}, {remarks_description}".strip()
            if instance.occurrenceRemarks:
                instance.occurrenceRemarks += f"; {entry}"
            else:
                instance.occurrenceRemarks = entry
                
        # Append-only logic for habitatNotes
        habitat_day = self.cleaned_data.get('habitat_day')
        habitat_month = self.cleaned_data.get('habitat_month')
        habitat_year = self.cleaned_data.get('habitat_year')
        habitat_initials = self.cleaned_data.get('habitat_initials')
        habitat_description = self.cleaned_data.get('habitat_description')
        if habitat_day and habitat_month and habitat_year and habitat_initials and habitat_description:
            entry = f"{habitat_day} {habitat_month} {habitat_year}, {habitat_initials}, {habitat_description}".strip()
            if instance.habitatNotes:
                instance.habitatNotes += f"; {entry}"
            else:
                instance.habitatNotes = entry
                
        # Append-only logic for samplingProtocol
        protocol_day = self.cleaned_data.get('protocol_day')
        protocol_month = self.cleaned_data.get('protocol_month')
        protocol_year = self.cleaned_data.get('protocol_year')
        protocol_initials = self.cleaned_data.get('protocol_initials')
        protocol_description = self.cleaned_data.get('protocol_description')
        if protocol_day and protocol_month and protocol_year and protocol_initials and protocol_description:
            entry = f"{protocol_day} {protocol_month} {protocol_year}, {protocol_initials}, {protocol_description}".strip()
            if instance.samplingProtocol:
                instance.samplingProtocol += f"; {entry}"
            else:
                instance.samplingProtocol = entry
                
        # Append-only logic for localityDescriptionNotes
        locality_notes_day = self.cleaned_data.get('locality_notes_day')
        locality_notes_month = self.cleaned_data.get('locality_notes_month')
        locality_notes_year = self.cleaned_data.get('locality_notes_year')
        locality_notes_initials = self.cleaned_data.get('locality_notes_initials')
        locality_notes_description = self.cleaned_data.get('locality_notes_description')
        if locality_notes_day and locality_notes_month and locality_notes_year and locality_notes_initials and locality_notes_description:
            entry = f"{locality_notes_day} {locality_notes_month} {locality_notes_year}, {locality_notes_initials}, {locality_notes_description}".strip()
            if instance.localityDescriptionNotes:
                instance.localityDescriptionNotes += f"; {entry}"
            else:
                instance.localityDescriptionNotes = entry
                
        # Append-only logic for georeferenceProtocol
        georef_protocol_day = self.cleaned_data.get('georef_protocol_day')
        georef_protocol_month = self.cleaned_data.get('georef_protocol_month')
        georef_protocol_year = self.cleaned_data.get('georef_protocol_year')
        georef_protocol_initials = self.cleaned_data.get('georef_protocol_initials')
        georef_protocol_description = self.cleaned_data.get('georef_protocol_description')
        if georef_protocol_day and georef_protocol_month and georef_protocol_year and georef_protocol_initials and georef_protocol_description:
            entry = f"{georef_protocol_day} {georef_protocol_month} {georef_protocol_year}, {georef_protocol_initials}, {georef_protocol_description}".strip()
            if instance.georeferenceProtocol:
                instance.georeferenceProtocol += f"; {entry}"
            else:
                instance.georeferenceProtocol = entry
                
        # Append-only logic for identificationReferences
        id_references_day = self.cleaned_data.get('id_references_day')
        id_references_month = self.cleaned_data.get('id_references_month')
        id_references_year = self.cleaned_data.get('id_references_year')
        id_references_initials = self.cleaned_data.get('id_references_initials')
        id_references_description = self.cleaned_data.get('id_references_description')
        if id_references_day and id_references_month and id_references_year and id_references_initials and id_references_description:
            entry = f"{id_references_day} {id_references_month} {id_references_year}, {id_references_initials}, {id_references_description}".strip()
            if instance.identificationReferences:
                instance.identificationReferences += f"; {entry}"
            else:
                instance.identificationReferences = entry
                
        # Append-only logic for identificationRemarks
        id_remarks_day = self.cleaned_data.get('id_remarks_day')
        id_remarks_month = self.cleaned_data.get('id_remarks_month')
        id_remarks_year = self.cleaned_data.get('id_remarks_year')
        id_remarks_initials = self.cleaned_data.get('id_remarks_initials')
        id_remarks_description = self.cleaned_data.get('id_remarks_description')
        if id_remarks_day and id_remarks_month and id_remarks_year and id_remarks_initials and id_remarks_description:
            entry = f"{id_remarks_day} {id_remarks_month} {id_remarks_year}, {id_remarks_initials}, {id_remarks_description}".strip()
            if instance.identificationRemarks:
                instance.identificationRemarks += f"; {entry}"
            else:
                instance.identificationRemarks = entry

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
