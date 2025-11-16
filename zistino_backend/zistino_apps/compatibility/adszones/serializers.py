"""
Serializers for AdsZones compatibility layer.
"""
from rest_framework import serializers
from .models import AdsZone


class AdsZoneCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating ad zone matching old Swagger format."""
    name = serializers.CharField(required=True, max_length=255)
    width = serializers.IntegerField(required=False, default=0, min_value=0)
    height = serializers.IntegerField(required=False, default=0, min_value=0)


class AdsZoneCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for AdsZone that matches old Swagger output format."""
    
    class Meta:
        model = AdsZone
        fields = ['id', 'name', 'width', 'height']  # Only these 4 fields match old Swagger
        read_only_fields = ['id']


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


class AdsZoneSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching ad zones matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pageNumber = serializers.IntegerField(required=False, default=1, min_value=1)
    pageSize = serializers.IntegerField(required=False, default=20, min_value=1)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )

