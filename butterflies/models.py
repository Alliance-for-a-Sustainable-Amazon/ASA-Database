"""
models.py
Defines the database models for the butterflies app.
Each model represents a table in the database and describes the structure of butterfly-related data.

Classes:
    - ButterflyCollection: Represents a butterfly collection event, including species, collector, date, and notes.
    - Trap: Represents a trap used for collecting butterflies, including location, setup date, and notes.
"""

from django.db import models
import uuid
from django.utils import timezone

class ButterflyCollection(models.Model):
    """
    Represents a single butterfly collection event.
    Fields:
        id (UUIDField): Unique identifier for the collection event.
        species (CharField): Name of the butterfly species collected.
        collection_date (DateTimeField): Date and time the butterfly was collected.
        collector_name (CharField): Name of the person who collected the butterfly.
        notes (TextField): Optional notes about the collection event.
        created_at (DateTimeField): Timestamp when the record was created.
        updated_at (DateTimeField): Timestamp when the record was last updated.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    species = models.CharField(max_length=255, verbose_name="Butterfly Species")
    collection_date = models.DateTimeField(default=timezone.now)
    collector_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a human-readable string representation of the butterfly collection event.
        Useful for admin interface and debugging.
        """
        return f"{self.species} collected by {self.collector_name} on {self.collection_date.strftime('%Y-%m-%d')}"

class Trap(models.Model):
    """
    Represents a trap used for collecting butterflies.
    Fields:
        id (UUIDField): Unique identifier for the trap.
        name (CharField): Unique name/identifier for the trap.
        location_description (TextField): Description of the trap's location.
        setup_date (DateField): Date the trap was set up.
        notes (TextField): Optional notes about the trap.
        created_at (DateTimeField): Timestamp when the record was created.
        updated_at (DateTimeField): Timestamp when the record was last updated.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Trap Identifier")
    location_description = models.TextField(blank=True, null=True)
    setup_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation for admin and shell."""
        return self.name
