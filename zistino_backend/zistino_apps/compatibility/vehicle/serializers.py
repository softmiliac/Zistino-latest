"""
Serializers for Vehicle endpoints.
These match old Swagger request/response formats.
"""
from rest_framework import serializers
from zistino_apps.users.models import Vehicle
from django.contrib.auth import get_user_model

User = get_user_model()


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for vehicle search."""
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


class VehicleCreateUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating vehicle matching old Swagger format."""
    userId = serializers.CharField(required=True, help_text='User ID (UUID string)')
    modelMake = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    plateNum = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    licence = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    bodytype = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    color = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    manufacturer = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    registrationNum = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    engineSize = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    tank = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    numoftyres = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    gpsDeviceId = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    active = serializers.BooleanField(required=False, default=True)
    latitude = serializers.DecimalField(required=False, allow_null=True, max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(required=False, allow_null=True, max_digits=9, decimal_places=6)
    protocol = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    port = serializers.IntegerField(required=False, default=0)


class VehicleSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching vehicles matching old Swagger format."""
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


class VehicleResponseSerializer(serializers.Serializer):
    """Response serializer for vehicle matching old Swagger format."""
    userId = serializers.CharField(help_text='User ID (UUID string)')
    modelMake = serializers.CharField(required=False, allow_null=True)
    plateNum = serializers.CharField(required=False, allow_null=True)
    licence = serializers.CharField(required=False, allow_null=True)
    bodytype = serializers.CharField(required=False, allow_null=True)
    color = serializers.CharField(required=False, allow_null=True)
    manufacturer = serializers.CharField(required=False, allow_null=True)
    registrationNum = serializers.CharField(required=False, allow_null=True)
    engineSize = serializers.CharField(required=False, allow_null=True)
    tank = serializers.CharField(required=False, allow_null=True)
    numoftyres = serializers.CharField(required=False, allow_null=True)
    gpsDeviceId = serializers.CharField(required=False, allow_null=True)
    active = serializers.BooleanField()
    latitude = serializers.DecimalField(required=False, allow_null=True, max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(required=False, allow_null=True, max_digits=9, decimal_places=6)
    protocol = serializers.CharField(required=False, allow_null=True)
    port = serializers.IntegerField(required=False, default=0)
