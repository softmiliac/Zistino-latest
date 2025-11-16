"""
Serializers for ProductSections endpoints.
These import from products app serializers and add compatibility request/response serializers.
"""
from zistino_apps.products.serializers import (
    ProductSectionSerializer,
)
from zistino_apps.compatibility.products.serializers import ProductCompatibilitySerializer
from rest_framework import serializers
from zistino_apps.products.models import ProductSection
import json


# Reuse ProductSectionSerializer and ProductSectionSearchRequestSerializer from products app
# These are already compatible with Flutter app expectations

# Additional serializers for ProductSections-specific endpoints
class ProductSectionGroupSerializer(serializers.Serializer):
    """Serializer for product section group operations."""
    groupName = serializers.CharField(required=True, max_length=100)
    sections = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of section IDs in this group'
    )


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for product section search."""
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


class ProductSectionCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating product sections matching old Swagger format."""
    parentId = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Parent section ID (optional)')
    startDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Start date (maps to expire_date)')
    endDate = serializers.DateTimeField(required=False, allow_null=True, help_text='End date (maps to expire_date)')
    type = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Section type (maps to setting_type)')
    name = serializers.CharField(required=False, max_length=255, allow_blank=True, allow_null=True)
    groupName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Group name')
    page = serializers.CharField(required=False, max_length=50, default='home', allow_blank=True, allow_null=True)
    version = serializers.IntegerField(required=False, default=0, allow_null=True)
    productId = serializers.CharField(required=False, allow_null=True, allow_blank=True, help_text='Product UUID')
    imagePath = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image path/URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Thumbnail (not stored in model)')
    setting = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Setting (not stored directly)')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Link URL')
    orderId = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Order ID (not stored in model)')
    locale = serializers.CharField(required=False, max_length=10, default='en', allow_blank=True, allow_null=True)


class ProductSectionSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching product sections matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0, help_text='Page number (0 defaults to 1)')
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0, help_text='Page size (0 defaults to 1)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )
    parentId = serializers.IntegerField(required=False, default=0, help_text='Parent section ID (optional, not used in filtering)')
    startDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Start date filter')
    endDate = serializers.DateTimeField(required=False, allow_null=True, help_text='End date filter')
    type = serializers.IntegerField(required=False, default=0, help_text='Section type filter (maps to setting_type)')


class ProductSectionCompatibilitySerializer(serializers.ModelSerializer):
    """ProductSection serializer matching old Swagger response format."""
    parentId = serializers.SerializerMethodField()
    startDate = serializers.SerializerMethodField()
    endDate = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    groupName = serializers.CharField(source='group_name', read_only=True)
    imagePath = serializers.CharField(source='image_path', read_only=True, allow_null=True)
    thumbnail = serializers.SerializerMethodField()
    setting = serializers.SerializerMethodField()
    linkUrl = serializers.CharField(source='link_url', read_only=True, allow_null=True)
    orderId = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductSection
        fields = [
            'id', 'parentId', 'startDate', 'endDate', 'type', 'name', 'groupName',
            'page', 'version', 'product', 'imagePath', 'thumbnail', 'setting',
            'description', 'linkUrl', 'orderId', 'locale'
        ]
        read_only_fields = ['id']
    
    def get_parentId(self, obj):
        """Return parentId (currently not in model, return None)."""
        return None
    
    def get_startDate(self, obj):
        """Return startDate (maps to expire_date or None)."""
        if obj.expire_date:
            return obj.expire_date.isoformat()
        return None
    
    def get_endDate(self, obj):
        """Return endDate (maps to expire_date or None)."""
        if obj.expire_date:
            return obj.expire_date.isoformat()
        return None
    
    def get_type(self, obj):
        """Return type (maps to setting_type or None)."""
        if obj.setting_type is not None:
            return obj.setting_type
        return None
    
    def get_thumbnail(self, obj):
        """Return thumbnail (not stored in model, return None)."""
        return None
    
    def get_setting(self, obj):
        """Return setting as JSON string matching old Swagger format."""
        setting_dict = {
            'type': obj.setting_type if obj.setting_type is not None else 0
        }
        return json.dumps(setting_dict)
    
    def get_orderId(self, obj):
        """Return orderId (not stored in model, return 0)."""
        return 0
    
    def get_product(self, obj):
        """Return full product object or None matching old Swagger format."""
        if obj.product:
            return ProductCompatibilitySerializer(obj.product, context=self.context).data
        return None


class ProductSectionGroupUpdateSerializer(serializers.Serializer):
    """Request serializer for updating a group of product sections."""
    id = serializers.IntegerField(required=False, default=0)
    name = serializers.CharField(required=True, max_length=255)
    parentId = serializers.IntegerField(required=False, default=0)
    startDate = serializers.DateTimeField(required=False, allow_null=True)
    endDate = serializers.DateTimeField(required=False, allow_null=True)
    type = serializers.IntegerField(required=False, default=0)
    groupName = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    page = serializers.CharField(required=False, max_length=50, default='home')
    version = serializers.IntegerField(required=False, default=0)
    productId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imagePath = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    setting = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    orderId = serializers.IntegerField(required=False, default=0)
    locale = serializers.CharField(required=False, max_length=10, default='en')
