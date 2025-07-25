
# admin.py
# Registers models with the Django admin site and customizes their display and search options.

from django.contrib import admin
from .models import Specimen, Locality, Initials


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Locality._meta.fields]
    search_fields = ['localityCode', 'siteName', 'siteDescription', 'habitat']
    list_filter = ['localityCode', 'country']

@admin.register(Initials)
class InitialsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Initials._meta.fields]
    search_fields = ['initials', 'full_name']
    list_filter = ['initials']

@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Specimen._meta.fields]
    search_fields = ['specimen_number', 'catalog_number', 'notes']
    list_filter = ['uploaded_iNaturalist', 'sex', 'locality', 'recordedBy']
