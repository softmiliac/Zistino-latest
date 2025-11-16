"""
Models for RoleClaims compatibility layer.
"""
import uuid
from django.db import models
from zistino_apps.compatibility.roles.models import Role


class RoleClaim(models.Model):
    """RoleClaim model matching old Swagger format."""
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='claims', help_text='Role this claim belongs to')
    claim_type = models.CharField(max_length=100, default='permission', help_text='Type of claim (e.g., permission)')
    claim_value = models.CharField(max_length=255, help_text='Claim value (e.g., Permissions.Products.View)')
    description = models.TextField(blank=True, null=True, help_text='Claim description')
    group = models.CharField(max_length=255, blank=True, null=True, help_text='Claim group name')
    selected = models.BooleanField(default=False, help_text='Whether this claim is selected')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_claims'
        ordering = ['claim_value']
        verbose_name = 'Role Claim'
        verbose_name_plural = 'Role Claims'
        indexes = [
            models.Index(fields=['role', 'claim_type']),
            models.Index(fields=['claim_value']),
        ]

    def __str__(self):
        return f'{self.role.name} - {self.claim_value}'
