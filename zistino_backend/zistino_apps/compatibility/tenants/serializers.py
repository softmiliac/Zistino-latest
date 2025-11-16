"""
Serializers for Tenants endpoints matching old Swagger format.
"""
from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant matching old Swagger format."""
    adminEmail = serializers.EmailField(source='admin_email', read_only=True)
    connectionString = serializers.CharField(source='connection_string', read_only=True)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    validUpto = serializers.DateTimeField(source='extended_expiry_date', read_only=True, allow_null=True)
    
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'key', 'adminEmail', 'connectionString', 'isActive', 'validUpto']
        read_only_fields = ['id']


class TenantCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating tenant matching old Swagger format."""
    name = serializers.CharField(required=True, max_length=255, help_text='Tenant name')
    key = serializers.CharField(required=True, max_length=255, help_text='Tenant key/identifier')
    adminEmail = serializers.EmailField(required=False, allow_blank=True, allow_null=True, help_text='Admin email for tenant')
    connectionString = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Database connection string')


class TenantUpgradeRequestSerializer(serializers.Serializer):
    """Request serializer for upgrading tenant matching old Swagger format."""
    tenant = serializers.CharField(required=True, help_text='Tenant key or identifier')
    extendedExpiryDate = serializers.DateTimeField(required=True, help_text='Extended expiry date for subscription')
