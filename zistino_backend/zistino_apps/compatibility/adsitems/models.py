"""
Models for AdsItems compatibility layer.
"""
from django.db import models


class AdsItem(models.Model):
    """Advertisement item model for managing individual ads."""
    id = models.AutoField(primary_key=True)
    ads_zone = models.ForeignKey(
        'compatibility.AdsZone',
        on_delete=models.CASCADE,
        related_name='ads_items',
        db_column='ads_zone_id',
        help_text='Foreign key to AdsZone'
    )
    file_path = models.CharField(max_length=500, help_text='Path to the ad file')
    file_type = models.IntegerField(default=0, help_text='Type of file (0=image, 1=video, etc.)')
    from_time = models.DateTimeField(help_text='When the ad starts displaying')
    to_time = models.DateTimeField(help_text='When the ad stops displaying')
    locale = models.CharField(max_length=10, default='en', help_text='Locale code (e.g., fa, en)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ads_items'
        verbose_name = 'Ads Item'
        verbose_name_plural = 'Ads Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ad {self.id} in Zone {self.ads_zone_id}"

