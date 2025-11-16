"""
Serializers for Roles endpoints matching old Swagger format.
"""
from rest_framework import serializers
from .models import Role


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for role search."""
    fields = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    groupBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Group by fields'
    )


class RoleCreateUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating role matching old Swagger format."""
    id = serializers.UUIDField(required=False, allow_null=True, help_text='Role ID (UUID). If provided, updates existing role.')
    name = serializers.CharField(required=True, max_length=255, help_text='Role name')
    description = serializers.CharField(required=False, allow_blank=True, default='', help_text='Role description')


class RoleListSerializer(serializers.ModelSerializer):
    """Serializer for role list matching old Swagger format."""
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'tenant']
        read_only_fields = ['id', 'tenant']


class RoleSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching roles matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 treated as 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 treated as 100)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True,
        help_text='Order by fields'
    )


class RoleListRequestSerializer(serializers.Serializer):
    """Request serializer for getting role list matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 treated as 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 treated as 100)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True,
        help_text='Order by fields'
    )


class RolePermissionsRequestSerializer(serializers.Serializer):
    """Request serializer for updating role permissions."""
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text='List of permission IDs or names'
    )
