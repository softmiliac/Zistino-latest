"""
Django app configuration for compatibility layer.
"""
from django.apps import AppConfig


class CompatibilityConfig(AppConfig):
    """Configuration for compatibility app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zistino_apps.compatibility'
    verbose_name = 'Compatibility Layer'

