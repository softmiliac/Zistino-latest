"""
Serializers for BlogCategories compatibility layer.
"""
from rest_framework import serializers
from zistino_apps.content.models import BlogCategory


class BlogCategoryCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating blog category matching old Swagger format."""
    title = serializers.CharField(required=True, max_length=255, help_text='Category title')
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image path or URL')
    slug = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='URL slug')
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Category content/description')
    locale = serializers.CharField(required=False, default='en', max_length=10, help_text='Locale code (e.g., fa, en)')


class BlogCategoryUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for updating blog category matching old Swagger format (all fields optional for updates)."""
    title = serializers.CharField(required=False, max_length=255, help_text='Category title')
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image path or URL')
    slug = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='URL slug')
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Category content/description')
    locale = serializers.CharField(required=False, default='en', max_length=10, help_text='Locale code (e.g., fa, en)')


class BlogCategoryCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for BlogCategory that matches old Swagger output format."""
    title = serializers.CharField(source='name', read_only=True)
    image = serializers.CharField(source='image_url', read_only=True, allow_null=True)
    slug = serializers.CharField(read_only=True, allow_null=True)
    content = serializers.CharField(source='description', read_only=True, allow_null=True)
    locale = serializers.CharField(read_only=True, allow_null=True, default='en')
    
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'image', 'slug', 'content', 'locale']
        read_only_fields = ['id']


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


class BlogCategorySearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching blog categories matching old Swagger format."""
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

