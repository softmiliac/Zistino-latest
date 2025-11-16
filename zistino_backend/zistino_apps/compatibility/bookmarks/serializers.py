"""
Serializers for Bookmark endpoints.
"""
from rest_framework import serializers
from zistino_apps.products.models import Bookmark
from zistino_apps.products.serializers import ProductSerializer


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for Bookmark model."""
    productId = serializers.UUIDField(source='product_id', read_only=True)
    product = ProductSerializer(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'productId', 'product', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class BookmarkCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for Bookmark that matches old Swagger output format."""
    id = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        """Convert UUID to integer for compatibility (using hash)."""
        import hashlib
        return int(hashlib.md5(str(obj.id).encode()).hexdigest(), 16) % (10 ** 10)
    
    def get_userId(self, obj):
        """Return user ID as string."""
        return str(obj.user.id)
    
    def get_content(self, obj):
        """Return product name as content."""
        return obj.product.name if obj.product else ''


class BookmarkCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating a bookmark matching old Swagger format."""
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (string/UUID). If not provided, uses current user.')
    content = serializers.CharField(required=True, help_text='Product ID (UUID as string) or product name to bookmark')

    def validate_content(self, value):
        """Validate content. Accepts UUID, product name, or any string (for compatibility with old Swagger)."""
        # Old Swagger allows any string as content - validation happens in the view
        # This allows the serializer to pass through any string value
        return value


class BookmarkClientCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating a bookmark via client endpoint matching old Swagger format."""
    content = serializers.CharField(required=True, help_text='Product ID (UUID as string) or product name to bookmark')

    def validate_content(self, value):
        """Validate content. Accepts UUID, product name, or any string (for compatibility with old Swagger)."""
        # Old Swagger allows any string as content - validation happens in the view
        # This allows the serializer to pass through any string value
        return value


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


class BookmarkSearchRequestSerializer(serializers.Serializer):
    """Request serializer for bookmark search matching old Swagger format."""
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

