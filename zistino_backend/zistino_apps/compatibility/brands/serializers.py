"""
Serializers for Brand endpoints.
"""
from rest_framework import serializers
from zistino_apps.products.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model."""
    imageUrl = serializers.CharField(source='image_url', allow_blank=True, required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'imageUrl', 'locale', 'is_active', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class BrandCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for Brand that matches old Swagger output format (for list endpoints)."""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    thumbnail = serializers.SerializerMethodField()
    locale = serializers.SerializerMethodField()
    masterId = serializers.SerializerMethodField()
    
    def get_thumbnail(self, obj):
        """Return image_url as thumbnail."""
        return obj.image_url if obj.image_url else None
    
    def get_locale(self, obj):
        """Return locale, or None if empty."""
        return obj.locale if obj.locale and obj.locale.strip() else None
    
    def get_masterId(self, obj):
        """Return null as masterId (Brand model doesn't have this field)."""
        return None


class BrandDetailCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for Brand detail that matches old Swagger output format (for detail endpoints)."""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    locale = serializers.SerializerMethodField()
    
    def get_description(self, obj):
        """Return description, or None if empty."""
        return obj.description if obj.description and obj.description.strip() else None
    
    def get_imageUrl(self, obj):
        """Return image_url, or None if empty."""
        return obj.image_url if obj.image_url else None
    
    def get_thumbnail(self, obj):
        """Return image_url as thumbnail, or None if empty."""
        return obj.image_url if obj.image_url else None
    
    def get_locale(self, obj):
        """Return locale, or None if empty."""
        return obj.locale if obj.locale and obj.locale.strip() else None


class BrandCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating a brand matching old Swagger format."""
    name = serializers.CharField(required=True, max_length=255, help_text='Brand name')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Brand description')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Brand image URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Brand thumbnail URL (mapped to imageUrl)')
    locale = serializers.CharField(required=False, default='fa', max_length=10, help_text='Locale code (e.g., fa, en)')
    masterId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID as string) - for reference only')


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


class BrandSearchRequestSerializer(serializers.Serializer):
    """Request serializer for brand search matching old Swagger format."""
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


class BrandGenerateRandomRequestSerializer(serializers.Serializer):
    """Request serializer for generating random brands matching old Swagger format."""
    nSeed = serializers.IntegerField(required=False, default=0, help_text='Random seed value for generating brands')
