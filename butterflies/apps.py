
# apps.py
# Defines the configuration for the butterflies Django app.
# This class is used by Django to set up app-specific settings.

from django.apps import AppConfig

class ButterfliesConfig(AppConfig):
    """
    Configuration class for the butterflies app.
    Sets the default auto field and app name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'butterflies'
