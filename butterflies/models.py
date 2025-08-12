"""
models.py
Defines the database models for the butterflies app.
Each model represents a table in the database and describes the structure of butterfly-related data.

Classes:
    - ButterflyCollection: Represents a butterfly collection event, including species, collector, date, and notes.
    - Trap: Represents a trap used for collecting butterflies, including location, setup date, and notes.
"""


"""
models.py
Defines the database models for a biological specimen collection app.
Tables: Specimen, Locality, Initials
"""

from django.db import models
from .utils import dot_if_none, str_with_dots

class Locality(models.Model):
    class Meta:
        db_table = 'localityTable'
        verbose_name_plural = 'Localities'
    """
    Stores information about collection localities.
    """
    localityCode = models.CharField(max_length=100, unique=True, blank=True, null=True, default=None, help_text="Unique code for locality (superkey)")
    country = models.CharField(max_length=100, blank=True, null=True, default=None)
    region = models.CharField(max_length=100, blank=True, null=True, default=None)
    province = models.CharField(max_length=100, blank=True, null=True, default=None)
    district = models.CharField(max_length=100, blank=True, null=True, default=None)
    siteName = models.CharField(max_length=255, blank=True, null=True, default=None)
    siteDescription = models.TextField(blank=True, null=True, default=None)
    habitat = models.CharField(max_length=255, blank=True, null=True, default=None)

    @str_with_dots
    def __str__(self):
        return self.localityCode

class Initials(models.Model):
    class Meta:
        db_table = 'initialsTable'
    """
    Stores initials and related info.
    """
    initials = models.CharField(max_length=10, unique=True, blank=True, null=True, default=None, help_text="Initials (superkey)")
    name = models.CharField(max_length=255, blank=True, null=True, default=None, help_text="Full name")
    relationshipOrTitle = models.CharField(max_length=255, blank=True, null=True, default=None, help_text="Relationship or title")
    yearAndTerm = models.CharField(max_length=50, blank=True, null=True, default=None, help_text="Year and term")

    @str_with_dots
    def __str__(self):
        return self.initials

class Specimen(models.Model):
    class Meta:
        db_table = 'specimenTable'
        # This ordering array specifies the conceptual field order
        # Important fields come first, but this doesn't change the database schema
        # It affects operations like model_to_dict() and form field ordering
        ordering = [
            # 1. Record-level Fields
            'modified', 
            
            # 2. Location Fields
            'locality', 'decimalLatitude', 'decimalLongitude', 'exact_loc',
            'coordinateUncertaintyInMeters', 'georeferencedBy', 'georeferencedDate',
            'georeferenceProtocol', 'minimumElevationInMeters', 'maximumElevationInMeters',
            'localityDescriptionNotes',
            
            # 3. Occurrence Fields
            'specimenNumber', 'catalogNumber', 'recordedBy', 'sex',
            'uploaded_iNaturalist', 'behavior', 'occurrenceRemarks', 'disposition',
            
            # 4. Event Fields
            'year', 'month', 'day', 'eventTime', 'eventDate',
            'habitatNotes', 'samplingProtocol',
            
            # 5. Taxon Fields
            'family', 'subfamily', 'tribe', 'subtribe', 'genus',
            'specificEpithet', 'infraspecificEpithet',
            
            # 6. Identification Fields
            'identifiedBy', 'dateIdentified', 'identificationReferences', 'identificationRemarks'
        ]

    # ----------------------------------
    # 1. Record-level Fields
    # ----------------------------------
    # Concatenated modification history (append-only, semicolon-separated)
    modified = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    
    # ----------------------------------
    # 2. Location Fields
    # ----------------------------------
    # Locality is a relation; all other locality info is in Locality table
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True, help_text="Dropdown: localityCode from Locality table.")
    decimalLatitude = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (XX.XXXXXX).")
    decimalLongitude = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (XX.XXXXXX).")
    exact_loc = models.CharField(max_length=5, blank=True, null=True, choices=[('TRUE', 'TRUE'), ('FALSE', 'FALSE')], help_text='Dropdown: "TRUE", "FALSE".')
    coordinateUncertaintyInMeters = models.CharField(max_length=100, blank=True, null=True, help_text="Text.")
    georeferencedBy = models.ForeignKey(Initials, on_delete=models.SET_NULL, null=True, related_name='georeferenced_specimens', help_text="Dropdown: initials from Initials table.")
    georeferencedDate = models.CharField(max_length=100, blank=True, null=True, help_text="Date (DD-MMM-YYYY; ex., 27-Nov-2024).")
    georeferenceProtocol = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    minimumElevationInMeters = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (X,XXX).")
    maximumElevationInMeters = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (X,XXX).")
    localityDescriptionNotes = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    
    # ----------------------------------
    # 3. Occurrence Fields
    # ----------------------------------
    specimenNumber = models.CharField(max_length=100, unique=True, blank=True, null=True, default=None, help_text="Manual entry. If duplicate, error.")
    catalogNumber = models.CharField(max_length=100, unique=True, blank=True, null=True, default=None, help_text="Auto-generated: year-localityCode-specimenNumber (nnnn). Do not edit.")
    recordedBy = models.ForeignKey(Initials, on_delete=models.SET_NULL, null=True, help_text="Dropdown: initials from Initials table.")
    sex = models.CharField(max_length=6, choices=[('male', 'male'), ('female', 'female'), ('.', '.')], help_text="Dropdown: male/female/.")
    uploaded_iNaturalist = models.CharField(max_length=5, choices=[('TRUE', 'TRUE'), ('FALSE', 'FALSE')], help_text="Dropdown: TRUE/FALSE.")
    behavior = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    occurrenceRemarks = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    disposition = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    
    # ----------------------------------
    # 4. Event Fields
    # ----------------------------------
    year = models.CharField(max_length=4, blank=True, null=True, help_text="Dropdown/typeable: 1900-2050.")
    month = models.CharField(max_length=10, blank=True, null=True, help_text="Dropdown/typeable.")
    day = models.CharField(max_length=2, blank=True, null=True, help_text="Dropdown/typeable.")
    eventTime = models.CharField(max_length=50, blank=True, null=True, help_text="Time (XX:XX) military format.")
    eventDate = models.CharField(max_length=100, blank=True, null=True, help_text="Date (DD-MMM-YYYY; ex., 27-Nov-2024).")
    habitatNotes = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    samplingProtocol = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    
    # ----------------------------------
    # 5. Taxon Fields
    # ----------------------------------
    family = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    subfamily = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    tribe = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    subtribe = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    genus = models.CharField(max_length=100, blank=True, null=True, help_text="Text/write in.")
    specificEpithet = models.CharField(max_length=100, blank=True, null=True, help_text="Text/write in.")
    infraspecificEpithet = models.CharField(max_length=100, blank=True, null=True, help_text="Text/write in.")
    
    # ----------------------------------
    # 6. Identification Fields
    # ----------------------------------
    identifiedBy = models.ForeignKey(Initials, on_delete=models.SET_NULL, null=True, related_name='identified_specimens', help_text="Dropdown: initials from Initials table.")
    dateIdentified = models.CharField(max_length=100, blank=True, null=True, help_text="Date (DD-MMM-YYYY; ex., 27-Nov-2024).")
    identificationReferences = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    identificationRemarks = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    
    def save(self, *args, **kwargs):
        # Auto-generate catalogNumber if not set and required fields are present
        if not self.catalogNumber:
            year = self.year or ''
            locality_code = self.locality.localityCode if self.locality and self.locality.localityCode else ''
            specimen_number = self.specimenNumber or ''
            self.catalogNumber = f"{year}-{locality_code}-{specimen_number}"
        super().save(*args, **kwargs)
        
    @property
    def binomial(self):
        """Generate the binomial name from genus and specificEpithet"""
        if self.genus and self.specificEpithet:
            return f"{self.genus} {self.specificEpithet}"
        return "."
    
    @str_with_dots
    def __str__(self):
        specimen_num = dot_if_none(self.specimenNumber)
        catalog_num = dot_if_none(self.catalogNumber)
        return f"Specimen {specimen_num} (Catalog {catalog_num})"
