"""
Serializers for Configuration endpoints.
"""
from rest_framework import serializers
from zistino_apps.configurations.models import Configuration
from zistino_apps.configurations.serializers import ConfigurationSerializer, ConfigRequestSerializer


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for configuration search."""
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


class ConfigurationSearchRequestSerializer(serializers.Serializer):
    """Request serializer for configuration search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 = page 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 = all results)')
    orderBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )


class ConfigurationCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating configuration matching old Swagger format."""
    name = serializers.CharField(required=True, help_text='Configuration name')
    type = serializers.IntegerField(required=True, help_text='Configuration type')
    value = serializers.CharField(required=True, allow_blank=True, help_text='Configuration value (as string)')

