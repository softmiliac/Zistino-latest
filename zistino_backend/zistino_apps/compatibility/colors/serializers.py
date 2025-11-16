"""
Serializers for Color endpoints.
"""
from rest_framework import serializers
from zistino_apps.products.models import Color
from zistino_apps.products.serializers import ColorSerializer


class ColorCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating color matching old Swagger format."""
    name = serializers.CharField(required=True, max_length=100, help_text='Color name')
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20, help_text='Color code')
    locale = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10, help_text='Locale code (e.g., fa, en)')


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


class ColorSearchRequestSerializer(serializers.Serializer):
    """Request serializer for color search matching old Swagger format."""
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

