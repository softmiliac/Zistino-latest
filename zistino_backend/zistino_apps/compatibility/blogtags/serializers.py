"""
Serializers for BlogTags compatibility layer.
"""
from rest_framework import serializers
from zistino_apps.content.models import BlogTag


class BlogTagCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating blog tag matching old Swagger format."""
    title = serializers.CharField(required=True, max_length=255, help_text='Tag title')
    slug = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='URL slug')
    locale = serializers.CharField(required=False, default='en', max_length=10, help_text='Locale code (e.g., fa, en)')


class BlogTagCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for BlogTag that matches old Swagger output format."""
    title = serializers.CharField(source='name', read_only=True)
    
    class Meta:
        model = BlogTag
        fields = ['id', 'title', 'slug', 'locale']
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


class BlogTagSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching blog tags matching old Swagger format."""
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

