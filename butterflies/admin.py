
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
    # Show every field except id
    list_display = (
        "species", "collector_name", "collection_date", "trap", "notes",
        "created_at", "updated_at"
    )
    list_filter = ("collection_date", "species", "trap", "created_at", "updated_at")
    search_fields = (
        "species", "collector_name", "notes", "trap__butterflyID", "trap__name",
        "created_at", "updated_at"
    )

@admin.register(Trap)
class TrapAdmin(admin.ModelAdmin):
    """
    Admin customization for Trap model.
    list_display: Fields shown in the admin list view.
    search_fields: Fields to search by in the admin list view.
    """
    # Show every field except id
    list_display = (
        "butterflyID", "name", "location_description", "setup_date", "notes",
        "created_at", "updated_at"
    )
    list_filter = ("setup_date", "created_at", "updated_at")
    search_fields = (
        "butterflyID", "name", "location_description", "notes",
        "created_at", "updated_at"
    )
