"""
Serializers for AdsItems compatibility layer.
"""
from rest_framework import serializers
from .models import AdsItem
from zistino_apps.compatibility.adszones.serializers import AdsZoneCompatibilitySerializer


class AdsItemCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating ad item matching old Swagger format."""
    adsZoneId = serializers.IntegerField(required=True, help_text='Ads zone ID')
    filePath = serializers.CharField(required=True, max_length=500, help_text='Path to the ad file')
    fileType = serializers.IntegerField(required=False, default=0, help_text='Type of file (0=image, 1=video, etc.)')
    fromTime = serializers.DateTimeField(required=True, help_text='When the ad starts displaying')
    toTime = serializers.DateTimeField(required=True, help_text='When the ad stops displaying')
    locale = serializers.CharField(required=False, default='en', max_length=10, help_text='Locale code (e.g., fa, en)')


class AdsItemCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for AdsItem that matches old Swagger output format."""
    adsZoneId = serializers.IntegerField(source='ads_zone_id', read_only=True)
    filePath = serializers.CharField(source='file_path', read_only=True)
    fileType = serializers.IntegerField(source='file_type', read_only=True)
    fromTime = serializers.SerializerMethodField()
    toTime = serializers.SerializerMethodField()
    
    class Meta:
        model = AdsItem
        fields = ['id', 'adsZoneId', 'filePath', 'fileType', 'fromTime', 'toTime', 'locale']
        read_only_fields = ['id']
    
    def get_fromTime(self, obj):
        """Format from_time in old Swagger format: '2025-11-09T06:54:24.692' (no Z, no timezone)."""
        if obj.from_time:
            dt_str = obj.from_time.isoformat()
            # Remove timezone info
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return None
    
    def get_toTime(self, obj):
        """Format to_time in old Swagger format: '2025-11-09T06:54:24.692' (no Z, no timezone)."""
        if obj.to_time:
            dt_str = obj.to_time.isoformat()
            # Remove timezone info
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return None


class AdsItemSearchResponseSerializer(serializers.ModelSerializer):
    """Serializer for search response with nested adsZone object."""
    adsZone = AdsZoneCompatibilitySerializer(source='ads_zone', read_only=True)
    fromTime = serializers.SerializerMethodField()
    toTime = serializers.SerializerMethodField()
    
    class Meta:
        model = AdsItem
        fields = ['id', 'adsZone', 'fromTime', 'toTime', 'locale']
        read_only_fields = ['id']
    
    def get_fromTime(self, obj):
        """Format from_time in old Swagger format: '2025-11-09T07:30:16.660Z' (with Z)."""
        if obj.from_time:
            dt_str = obj.from_time.isoformat()
            # Remove timezone offset and add Z
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6] + 'Z'
            elif not dt_str.endswith('Z'):
                dt_str = dt_str + 'Z'
            return dt_str
        return None
    
    def get_toTime(self, obj):
        """Format to_time in old Swagger format: '2025-11-09T07:30:16.660Z' (with Z)."""
        if obj.to_time:
            dt_str = obj.to_time.isoformat()
            # Remove timezone offset and add Z
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6] + 'Z'
            elif not dt_str.endswith('Z'):
                dt_str = dt_str + 'Z'
            return dt_str
        return None


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


class AdsItemSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching ad items matching old Swagger format."""
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

