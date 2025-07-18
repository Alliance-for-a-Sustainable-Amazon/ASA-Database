from django.contrib import admin
from .models import ButterflyCollection, Trap

@admin.register(ButterflyCollection)
class ButterflyCollectionAdmin(admin.ModelAdmin):
    list_display = ("species", "collector_name", "collection_date", "created_at", "updated_at")
    list_filter = ("collection_date", "species")
    search_fields = ("species", "collector_name", "notes")

@admin.register(Trap)
class TrapAdmin(admin.ModelAdmin):
    list_display = ("name", "location_description", "setup_date", "created_at", "updated_at")
    search_fields = ("name", "location_description", "notes")
