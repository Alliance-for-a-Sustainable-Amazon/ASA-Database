"""
models.py
Defines the database models for the butterflies app.
Each model represents a table in the database.
"""

from django.db import models
import uuid
from django.utils import timezone

class ButterflyCollection(models.Model):
    """
    Represents a single butterfly collection event.
    Fields:
        - id: Unique identifier (UUID)
        - species: Name of the butterfly species
        - collection_date: Date and time the butterfly was collected
        - collector_name: Name of the person who collected the butterfly
        - notes: Optional notes about the collection
        - created_at: Timestamp when the record was created
        - updated_at: Timestamp when the record was last updated
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    species = models.CharField(max_length=255, verbose_name="Butterfly Species")
    collection_date = models.DateTimeField(default=timezone.now)
    collector_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation for admin and shell."""
        return f"{self.species} collected by {self.collector_name} on {self.collection_date.strftime('%Y-%m-%d')}"

class Trap(models.Model):
    """
    Represents a trap used for collecting butterflies.
    Fields:
        - id: Unique identifier (UUID)
        - name: Unique name/identifier for the trap
        - location_description: Description of the trap's location
        - setup_date: Date the trap was set up
        - notes: Optional notes about the trap
        - created_at: Timestamp when the record was created
        - updated_at: Timestamp when the record was last updated
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
