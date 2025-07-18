from django.db import models
import uuid
from django.utils import timezone

class ButterflyCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    species = models.CharField(max_length=255, verbose_name="Butterfly Species")
    collection_date = models.DateTimeField(default=timezone.now)
    collector_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.species} collected by {self.collector_name} on {self.collection_date.strftime('%Y-%m-%d')}"

class Trap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Trap Identifier")
    location_description = models.TextField(blank=True, null=True)
    setup_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
