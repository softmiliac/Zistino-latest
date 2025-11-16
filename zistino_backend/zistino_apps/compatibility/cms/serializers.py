"""
Serializers for CMS endpoints.
"""
from rest_framework import serializers
from zistino_apps.products.models import ProductSection
from zistino_apps.products.serializers import ProductSectionSerializer


class CMSCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for CMS that matches old Swagger output format."""
    id = serializers.IntegerField(read_only=True)
    version = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    content = serializers.SerializerMethodField()
    groupName = serializers.SerializerMethodField()
    locale = serializers.CharField(read_only=True)
    
    def get_content(self, obj):
        """Return description as content."""
        return obj.description if obj.description else ''
    
    def get_groupName(self, obj):
        """Return group_name as groupName."""
        return obj.group_name if obj.group_name else ''


class CMSCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating CMS matching old Swagger format."""
    version = serializers.IntegerField(required=False, default=0, help_text='Version number')
    name = serializers.CharField(required=True, max_length=255, help_text='CMS name')
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='CMS content (maps to description)')
    groupName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100, help_text='Group name (maps to group_name)')
    locale = serializers.CharField(required=False, default='en', max_length=10, help_text='Locale code (e.g., fa, en)')


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields serializer."""
    fields = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    groupBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Group by fields'
    )


class CMSSearchRequestSerializer(serializers.Serializer):
    """Request serializer for CMS search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0)
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )

