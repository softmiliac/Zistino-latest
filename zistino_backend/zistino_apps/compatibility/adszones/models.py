"""
Models for AdsZones compatibility layer.
"""
from django.db import models


class AdsZone(models.Model):
    """Advertisement zone model for managing ad display zones."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    width = models.IntegerField(default=0, help_text='Zone width in pixels')
    height = models.IntegerField(default=0, help_text='Zone height in pixels')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ads_zones'
        verbose_name = 'Ads Zone'
        verbose_name_plural = 'Ads Zones'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

