"""
Models for Roles compatibility layer.
"""
import uuid
from django.db import models


class Role(models.Model):
    """Role model matching old Swagger format."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text='Role name')
    description = models.TextField(blank=True, null=True, help_text='Role description')
    tenant = models.CharField(max_length=100, default='root', help_text='Tenant identifier')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name
