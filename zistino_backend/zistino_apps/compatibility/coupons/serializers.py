"""
Serializers for Coupon endpoints.
"""
from rest_framework import serializers
from zistino_apps.payments.models import Coupon
from zistino_apps.payments.serializers import CouponSerializer


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for coupon search."""
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


class CouponSearchRequestSerializer(serializers.Serializer):
    """Request serializer for coupon search matching old Swagger format."""
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


class CouponCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating coupon matching old Swagger format."""
    key = serializers.CharField(required=True, help_text='Coupon key/code')
    startDateTime = serializers.DateTimeField(required=False, allow_null=True, help_text='Start date/time (maps to valid_from)')
    endDateTime = serializers.DateTimeField(required=False, allow_null=True, help_text='End date/time (maps to valid_to)')
    maxUseCount = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Maximum use count (maps to usage_limit)')
    percent = serializers.IntegerField(required=False, default=0, help_text='Percentage discount (0-100)')
    price = serializers.IntegerField(required=False, default=0, help_text='Fixed price discount amount')
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (not used, for compatibility only)')
    roleId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Role ID (not used, for compatibility only)')
    type = serializers.IntegerField(required=False, default=0, help_text='Coupon type (maps to status: 0=inactive, 1=active)')
    limitationType = serializers.IntegerField(required=False, default=0, help_text='Limitation type (not used, for compatibility only)')
    userLimitationType = serializers.IntegerField(required=False, default=0, help_text='User limitation type (not used, for compatibility only)')


class CouponCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for Coupon search results matching old Swagger format."""
    id = serializers.IntegerField(read_only=True)
    key = serializers.CharField(read_only=True)
    type = serializers.SerializerMethodField()
    
    def get_type(self, obj):
        """Return status as type (0=inactive, 1=active)."""
        return obj.status


class CouponDetailSerializer(serializers.Serializer):
    """Compatibility serializer for Coupon full details matching old Swagger format."""
    id = serializers.IntegerField(read_only=True)
    key = serializers.CharField(read_only=True)
    startDateTime = serializers.DateTimeField(source='valid_from', read_only=True, allow_null=True)
    endDateTime = serializers.DateTimeField(source='valid_to', read_only=True, allow_null=True)
    maxUseCount = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    roleId = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    limitationType = serializers.SerializerMethodField()
    userLimitationType = serializers.SerializerMethodField()
    
    def get_maxUseCount(self, obj):
        """Return usage_limit as maxUseCount."""
        return obj.usage_limit if obj.usage_limit else 0
    
    def get_percent(self, obj):
        """Return percent (if amount represents percentage, otherwise 0)."""
        # If amount is between 0-100, treat as percent; otherwise 0
        if 0 <= obj.amount <= 100:
            return obj.amount
        return 0
    
    def get_price(self, obj):
        """Return price (if amount represents fixed price, otherwise 0)."""
        # If amount > 100, treat as fixed price; otherwise 0
        if obj.amount > 100:
            return obj.amount
        return 0
    
    def get_userId(self, obj):
        """Return userId (not stored in model, return default UUID for compatibility)."""
        # Return a default UUID string for compatibility
        return "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671"
    
    def get_roleId(self, obj):
        """Return roleId (not stored in model, return null)."""
        return None
    
    def get_type(self, obj):
        """Return status as type (0=inactive, 1=active)."""
        return obj.status
    
    def get_limitationType(self, obj):
        """Return limitationType (not stored in model, return 0)."""
        return 0
    
    def get_userLimitationType(self, obj):
        """Return userLimitationType (not stored in model, return 0)."""
        return 0

