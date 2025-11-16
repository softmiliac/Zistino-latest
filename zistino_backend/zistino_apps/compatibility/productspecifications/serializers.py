"""
Serializers for ProductSpecifications endpoints.
These import from products app serializers and add compatibility request/response serializers.
"""
from zistino_apps.products.serializers import (
    SpecificationSerializer,
)
from zistino_apps.products.models import Specification
from rest_framework import serializers


# Reuse SpecificationSerializer from products app
# Create compatibility serializers for old Swagger format

class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for product specification search."""
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


class ProductSpecificationCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating product specifications matching old Swagger format."""
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Category (not stored in model)')
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Content (maps to size field)')
    locale = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Locale (not stored in model)')


class ProductSpecificationSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching product specifications matching old Swagger format."""
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


class ProductSpecificationCompatibilitySerializer(serializers.ModelSerializer):
    """ProductSpecification serializer matching old Swagger response format."""
    category = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    locale = serializers.SerializerMethodField()
    
    class Meta:
        model = Specification
        fields = ['id', 'category', 'content', 'locale']
        read_only_fields = ['id']
    
    def get_category(self, obj):
        """Return category (maps from level field or product category)."""
        # Try to get from level field first (where we stored category name)
        if obj.level:
            return obj.level
        # Fall back to product's category name
        if obj.product and obj.product.category:
            return obj.product.category.name
        return 'string'  # Default value
    
    def get_content(self, obj):
        """Return content (maps from size field)."""
        return obj.size if obj.size else 'string'
    
    def get_locale(self, obj):
        """Return locale (not stored in model, return default)."""
        return 'string'  # Default value since locale is not stored

