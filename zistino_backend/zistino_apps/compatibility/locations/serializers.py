"""
Serializers for Locations endpoints.
These match old Swagger request/response formats.
"""
from rest_framework import serializers
from zistino_apps.deliveries.models import LocationUpdate


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for location search."""
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


class LocationCreateUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating location matching old Swagger format."""
    userId = serializers.CharField(required=True, help_text='User ID (UUID string)')
    tripId = serializers.IntegerField(required=True, help_text='Trip ID')
    latitude = serializers.DecimalField(required=True, max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(required=True, max_digits=9, decimal_places=6)
    speed = serializers.IntegerField(required=False, default=0)
    heading = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    altitude = serializers.DecimalField(required=False, default=0, max_digits=9, decimal_places=2)
    satellites = serializers.IntegerField(required=False, default=0)
    hdop = serializers.IntegerField(required=False, default=0)
    gsmSignal = serializers.IntegerField(required=False, default=0, help_text='GSM signal strength')
    odometer = serializers.IntegerField(required=False, default=0)


class LocationSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching locations matching old Swagger format."""
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
    tripId = serializers.IntegerField(required=False, allow_null=True, help_text='Filter by trip ID')


class LocationResponseSerializer(serializers.Serializer):
    """Response serializer for location matching old Swagger format."""
    id = serializers.IntegerField()
    userId = serializers.CharField(help_text='User ID (UUID string)')
    tripId = serializers.IntegerField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    speed = serializers.IntegerField()
    heading = serializers.CharField(required=False, allow_null=True)
    altitude = serializers.DecimalField(max_digits=9, decimal_places=2)
    satellites = serializers.IntegerField()
    hdop = serializers.IntegerField()
    gsmSignal = serializers.IntegerField()
    odometer = serializers.IntegerField()
    createdOn = serializers.DateTimeField(help_text='Creation timestamp')
