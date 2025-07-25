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

class Locality(models.Model):
    class Meta:
        db_table = 'localityTable'
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

    def __str__(self):
        return self.initials

class Specimen(models.Model):
    class Meta:
        db_table = 'specimenTable'

    # Concatenated modification history (append-only, semicolon-separated)
    modified = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    specimenNumber = models.CharField(max_length=100, unique=True, blank=True, null=True, default=None, help_text="Manual entry. If duplicate, error.")
    catalogNumber = models.CharField(max_length=100, unique=True, blank=True, null=True, default=None, help_text="Unique voucher code.")
    recordedBy = models.ForeignKey(Initials, on_delete=models.SET_NULL, null=True, help_text="Dropdown: initials from Initials table.")
    uploaded_iNaturalist = models.CharField(max_length=5, choices=[('TRUE', 'TRUE'), ('FALSE', 'FALSE')], help_text="Dropdown: TRUE/FALSE.")
    sex = models.CharField(max_length=6, choices=[('male', 'male'), ('female', 'female'), ('.', '.')], help_text="Dropdown: male/female/.")
    behavior = models.TextField(blank=True, null=True, help_text="Text.")
    disposition = models.TextField(blank=True, null=True, help_text="Append-only: Each entry is 'MM-DD-YYYY, initials, description'; entries separated by semicolon. Use form to add, not edit.")
    occurrenceRemarks = models.TextField(blank=True, null=True, help_text="Text.")
    eventDate = models.DateField(blank=True, null=True, help_text="Date (DD-MMM-YYYY; ex., 27-Nov-2024).")
    eventTime = models.TimeField(blank=True, null=True, help_text="Time (XX:XX) military format.")
    year = models.CharField(max_length=4, blank=True, null=True, help_text="Dropdown/typeable: 1900-2050.")
    month = models.CharField(max_length=2, blank=True, null=True, help_text="Dropdown/typeable.")
    day = models.CharField(max_length=2, blank=True, null=True, help_text="Dropdown/typeable.")
    habitat = models.CharField(max_length=255, blank=True, null=True, help_text="Text.")
    habitatNotes = models.TextField(blank=True, null=True, help_text="Text.")
    samplingProtocol = models.TextField(blank=True, null=True, help_text="Text.")
    # Locality is a relation; all other locality info is in Locality table
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True, help_text="Dropdown: localityCode from Locality table.")
    localityDescriptionNotes = models.TextField(blank=True, null=True, help_text="Text.")
    minimumElevationInMeters = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (X,XXX).")
    maximumElevationInMeters = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (X,XXX).")
    decimalLatitude = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (XX.XXXXXX).")
    decimalLongitude = models.CharField(max_length=20, blank=True, null=True, help_text="Text/number (XX.XXXXXX).")
    exact_loc = models.CharField(max_length=5, blank=True, null=True, choices=[('TRUE', 'TRUE'), ('FALSE', 'FALSE')], help_text='Dropdown: "TRUE", "FALSE".')
    coordinateUncertaintyInMeters = models.CharField(max_length=100, blank=True, null=True, help_text="Text.")
    georeferencedBy = models.ForeignKey(Initials, on_delete=models.SET_NULL, null=True, related_name='georeferenced_specimens', help_text="Dropdown: initials from Initials table.")
    georeferencedDate = models.DateField(blank=True, null=True, help_text="Date (DD-MMM-YYYY; ex., 27-Nov-2024).")
    georeferenceProtocol = models.TextField(blank=True, null=True, help_text="Text.")
    identifiedBy = models.ForeignKey(Initials, on_delete=models.SET_NULL, null=True, related_name='identified_specimens', help_text="Dropdown: initials from Initials table.")
    dateIdentified = models.DateField(blank=True, null=True, help_text="Date (DD-MMM-YYYY; ex., 27-Nov-2024).")
    identificationReferences = models.TextField(blank=True, null=True, help_text="Text.")
    identificationRemarks = models.TextField(blank=True, null=True, help_text="Text.")
    family = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    subfamily = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    tribe = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    subtribe = models.CharField(max_length=100, blank=True, null=True, help_text='Text/write in.')
    genus = models.CharField(max_length=100, blank=True, null=True, help_text="Text/write in.")
    specificEpithet = models.CharField(max_length=100, blank=True, null=True, help_text="Text/write in.")
    infraspecificEpithet = models.CharField(max_length=100, blank=True, null=True, help_text="Text/write in.")

    def __str__(self):
        return f"Specimen {self.specimenNumber} (Catalog {self.catalogNumber})"
