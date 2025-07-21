
# admin.py
# Registers models with the Django admin site and customizes their display and search options.

from django.contrib import admin
from .models import ButterflyCollection, Trap

@admin.register(ButterflyCollection)
class ButterflyCollectionAdmin(admin.ModelAdmin):
    """
    Admin customization for ButterflyCollection model.
    list_display: Fields shown in the admin list view.
    list_filter: Fields to filter by in the admin list view.
    search_fields: Fields to search by in the admin list view.
    """
    list_display = ("species", "collector_name", "collection_date", "created_at", "updated_at")
    list_filter = ("collection_date", "species")
    search_fields = ("species", "collector_name", "notes")

@admin.register(Trap)
class TrapAdmin(admin.ModelAdmin):
    """
    Admin customization for Trap model.
    list_display: Fields shown in the admin list view.
    search_fields: Fields to search by in the admin list view.
    """
    list_display = ("name", "location_description", "setup_date", "created_at", "updated_at")
    search_fields = ("name", "location_description", "notes")
