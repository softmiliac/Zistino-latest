"""
Django project initialization.
This ensures Celery is imported when Django starts.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)

