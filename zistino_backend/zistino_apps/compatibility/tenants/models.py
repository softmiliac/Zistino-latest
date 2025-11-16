"""
Models for Tenants compatibility layer.
"""
import uuid
from django.db import models


class Tenant(models.Model):
    """Tenant model matching old Swagger format."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text='Tenant name')
    key = models.CharField(max_length=255, unique=True, help_text='Tenant key/identifier')
    admin_email = models.EmailField(blank=True, null=True, help_text='Admin email for tenant')
    connection_string = models.TextField(blank=True, null=True, help_text='Database connection string')
    is_active = models.BooleanField(default=True, help_text='Whether tenant is active')
    extended_expiry_date = models.DateTimeField(blank=True, null=True, help_text='Extended expiry date for subscription (validUpto)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'
        ordering = ['name']
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def __str__(self):
        return f"{self.name} ({self.key})"
