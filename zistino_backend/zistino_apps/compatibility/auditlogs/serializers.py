"""
Serializers for AuditLogs compatibility layer.
"""
from rest_framework import serializers


class AuditLogCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for AuditLog that matches old Swagger output format."""
    id = serializers.CharField(read_only=True, help_text='Audit log ID')
    userId = serializers.CharField(read_only=True, help_text='User ID who performed the action')
    type = serializers.CharField(read_only=True, help_text='Type of audit log')
    tableName = serializers.CharField(read_only=True, help_text='Name of the table affected')
    dateTime = serializers.DateTimeField(read_only=True, help_text='Date and time of the action')
    oldValues = serializers.CharField(read_only=True, help_text='Old values before change')
    newValues = serializers.CharField(read_only=True, help_text='New values after change')
    affectedColumns = serializers.CharField(read_only=True, help_text='Columns that were affected')
    primaryKey = serializers.CharField(read_only=True, help_text='Primary key of the affected record')

