"""
Serializers for Trip endpoints.
These match old Swagger request/response formats.
"""
from rest_framework import serializers
from zistino_apps.deliveries.models import Trip


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for trip search."""
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


class TripCreateUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating trip matching old Swagger format."""
    userId = serializers.CharField(required=True, help_text='User ID (UUID string)')
    startLocationId = serializers.IntegerField(required=False, default=0, help_text='Start location ID')
    endLocationId = serializers.IntegerField(required=False, default=0, help_text='End location ID')
    distance = serializers.IntegerField(required=False, default=0, help_text='Distance in meters')
    duration = serializers.IntegerField(required=False, default=0, help_text='Duration in seconds')
    maxSpeed = serializers.IntegerField(required=False, default=0, help_text='Maximum speed')
    averageSpeed = serializers.IntegerField(required=False, default=0, help_text='Average speed')
    averageAltitude = serializers.IntegerField(required=False, default=0, help_text='Average altitude')


class TripSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching trips matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 treated as 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 treated as 1)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True,
        help_text='Order by fields'
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Filter by user ID')


class TripResponseSerializer(serializers.Serializer):
    """Response serializer for trip matching old Swagger format."""
    id = serializers.IntegerField()
    userId = serializers.CharField(help_text='User ID (UUID string)')
    startLocationId = serializers.IntegerField()
    endLocationId = serializers.IntegerField()
    distance = serializers.IntegerField()
    duration = serializers.IntegerField()
    maxSpeed = serializers.IntegerField()
    averageSpeed = serializers.IntegerField()
    averageAltitude = serializers.IntegerField()
    createdOn = serializers.DateTimeField(help_text='Creation timestamp')
