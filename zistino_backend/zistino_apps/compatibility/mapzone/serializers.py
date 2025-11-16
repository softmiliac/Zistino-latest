"""
Serializers for MapZone endpoints.
These import from users app serializers.
"""
from zistino_apps.users.serializers import ZoneSerializer, UserZoneSerializer
from rest_framework import serializers


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for mapzone search."""
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


class MapZoneSearchRequestSerializer(serializers.Serializer):
    """Request serializer for mapzone search matching old Swagger format."""
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


class MapZoneSearchUserInZoneRequestSerializer(serializers.Serializer):
    """Request serializer for searching users in zone."""
    zoneId = serializers.IntegerField(required=True)


class MapZoneUserInZoneRequestSerializer(serializers.Serializer):
    """Request serializer for getting user zones."""
    userid = serializers.CharField(required=False, allow_blank=True)
    userId = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.CharField(required=False, allow_blank=True)


class MapZoneCreateSerializer(serializers.Serializer):
    """Request serializer for creating a zone matching old Swagger format."""
    zone = serializers.CharField(required=True, help_text='Zone name')
    zonepath = serializers.CharField(required=False, allow_blank=True, default='', help_text='Zone path')
    description = serializers.CharField(required=False, allow_blank=True, default='', help_text='Zone description')
    address = serializers.CharField(required=False, allow_blank=True, default='', help_text='Zone address')
    
    def create(self, validated_data):
        """Create a new zone."""
        from zistino_apps.users.models import Zone
        return Zone.objects.create(
            zone=validated_data['zone'],
            zonepath=validated_data.get('zonepath', ''),
            description=validated_data.get('description', ''),
            address=validated_data.get('address', ''),
            is_active=True
        )


class MapZoneCreateUserInZoneRequestSerializer(serializers.Serializer):
    """Request serializer for creating user in zone matching old Swagger format."""
    userId = serializers.CharField(required=True, help_text='User ID (UUID or phone number)')
    zoneId = serializers.IntegerField(required=True, help_text='Zone ID')

