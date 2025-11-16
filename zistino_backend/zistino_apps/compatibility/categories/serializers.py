"""
Serializers for Category endpoints.
"""
from rest_framework import serializers
from zistino_apps.products.models import Category
import hashlib


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    imageUrl = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'imageUrl', 'is_active', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    def get_imageUrl(self, obj):
        """Return image URL if image exists."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ''


class CategoryCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating category matching old Swagger format."""
    parentId = serializers.IntegerField(required=False, allow_null=True, help_text='Parent category ID (not used in current model)')
    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    shortDescription = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Not used in current model')
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Category type (not used in current model)')
    imagePath = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image path or URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Thumbnail (not used in current model)')
    masterId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Master ID (not used in current model)')
    sortOrder = serializers.IntegerField(required=False, default=0, help_text='Sort order (not used in current model)')
    locale = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Locale (not used in current model)')


class CategoryCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for Category that matches old Swagger output format."""
    parentId = serializers.SerializerMethodField()
    parName = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True, allow_blank=True, default='')
    shortDescription = serializers.CharField(read_only=True, allow_null=True, default=None)
    type = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    imagePath = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    masterId = serializers.SerializerMethodField()
    masterName = serializers.SerializerMethodField()
    sortOrder = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    locale = serializers.CharField(read_only=True, allow_null=True, default=None)

    class Meta:
        model = Category
        fields = [
            'id', 'parentId', 'parName', 'name', 'description', 'shortDescription', 'type',
            'imagePath', 'thumbnail', 'masterId', 'masterName', 'sortOrder', 'locale'
        ]
        read_only_fields = ['id']

    def get_imagePath(self, obj):
        """Return image path as relative path matching old Swagger format."""
        if obj.image:
            # Get relative URL path (like "/uploads/app/image.webp")
            image_url = obj.image.url
            # If it's already a full URL, extract the path
            if image_url.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                image_url = parsed.path
            # Remove /media/ prefix if present (old Swagger uses /uploads/app/)
            if image_url.startswith('/media/'):
                image_url = image_url.replace('/media/', '/uploads/app/')
            return image_url
        return None

    def get_thumbnail(self, obj):
        """Return thumbnail as relative path matching old Swagger format (same as imagePath)."""
        # Thumbnail is same as imagePath in old Swagger
        return self.get_imagePath(obj)

    def get_parentId(self, obj):
        """Return parent ID (not used in current model, return 0 to match old Swagger)."""
        return 0

    def get_parName(self, obj):
        """Return parent name (not used in current model, return null to match old Swagger)."""
        return None

    def get_masterId(self, obj):
        """Return master ID (return null to match old Swagger format)."""
        return None

    def get_masterName(self, obj):
        """Return master name (return null to match old Swagger format)."""
        return None

    def to_representation(self, instance):
        """Convert to old Swagger format."""
        data = super().to_representation(instance)
        
        # Convert UUID id to integer hash for compatibility with old Swagger
        # Old Swagger shows id as integer (e.g., 6), but our model uses UUID
        if 'id' in data and data['id']:
            # Use deterministic hash (MD5) to get a consistent integer
            # This ensures the same UUID always maps to the same integer across server restarts
            uuid_str = str(data['id'])
            # Use MD5 hash for deterministic results
            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
            hash_int = int(hash_obj.hexdigest(), 16)
            data['id'] = hash_int % 2147483647  # Max 32-bit integer
        
        # Set default locale if not provided
        if 'locale' not in data or data['locale'] is None:
            data['locale'] = 'en'
        
        return data


class CategoryClientSerializer(serializers.ModelSerializer):
    """Serializer for client category endpoints matching old Swagger format."""
    parentId = serializers.SerializerMethodField()
    imagePath = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    lastModifiedOn = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    shortDescription = serializers.CharField(read_only=True, allow_null=True, default=None)

    class Meta:
        model = Category
        fields = ['id', 'parentId', 'name', 'imagePath', 'thumbnail', 'count', 'lastModifiedOn', 'children', 'shortDescription']
        read_only_fields = ['id']

    def get_parentId(self, obj):
        """Return parent ID (0 for now, no hierarchical categories)."""
        return 0

    def get_imagePath(self, obj):
        """Return image path as relative path or null."""
        if obj.image:
            # Get relative URL path (like "/uploads/app/image.webp")
            image_url = obj.image.url
            # If it's already a full URL, extract the path
            if image_url.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                image_url = parsed.path
            # Remove /media/ prefix if present (old Swagger uses /uploads/app/)
            if image_url.startswith('/media/'):
                image_url = image_url.replace('/media/', '/uploads/app/')
            return image_url
        return None

    def get_thumbnail(self, obj):
        """Return thumbnail (null for client endpoints)."""
        return None

    def get_count(self, obj):
        """Return count of products in category (null by default, populated in by-type-count endpoint)."""
        # This will be set by the view if needed
        return getattr(obj, '_product_count', None)

    def get_lastModifiedOn(self, obj):
        """Return last modified date in old Swagger format."""
        # Category model only has created_at, use that
        date_field = obj.created_at
        if date_field:
            # Format: "0001-01-01T00:00:00" (old Swagger shows this for null dates)
            # Return ISO format without timezone
            dt_str = date_field.isoformat()
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return "0001-01-01T00:00:00"

    def get_children(self, obj):
        """Return children array (empty for now, no hierarchical categories)."""
        return []

    def to_representation(self, instance):
        """Convert to old Swagger format."""
        data = super().to_representation(instance)
        
        # Convert UUID id to integer hash for compatibility with old Swagger
        if 'id' in data and data['id']:
            uuid_str = str(data['id'])
            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
            hash_int = int(hash_obj.hexdigest(), 16)
            data['id'] = hash_int % 2147483647  # Max 32-bit integer
        
        return data


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for category search."""
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


class CategorySearchRequestSerializer(serializers.Serializer):
    """Request serializer for category search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )
    id = serializers.IntegerField(required=False, allow_null=True, help_text='Category ID filter')
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Category type filter')

