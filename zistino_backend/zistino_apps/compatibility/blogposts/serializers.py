"""
Serializers for BlogPosts compatibility layer.
"""
from rest_framework import serializers
from zistino_apps.content.models import BlogPost, BlogCategory, BlogTag


class FileSerializer(serializers.Serializer):
    """Serializer for file objects in request."""
    id = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.IntegerField(required=False, allow_null=True)
    rowId = serializers.IntegerField(required=False, allow_null=True)
    fileUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class BlogPostCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating blog post matching old Swagger format."""
    authorId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Author ID (string)')
    parentId = serializers.IntegerField(required=False, allow_null=True, help_text='Parent/Category ID')
    title = serializers.CharField(required=True, max_length=255, help_text='Post title')
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Post type (not used in model)')
    metaTitle = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Meta title (not used in model)')
    slug = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='URL slug')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Featured image URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Thumbnail URL (not used in model)')
    summery = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Post summary/excerpt')
    content = serializers.CharField(required=True, help_text='Post content')
    published = serializers.DateTimeField(required=False, allow_null=True, help_text='Published date/time')
    categories = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Categories as string (not used, use categoryIds)')
    categoryIds = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text='Category IDs (uses first one as category)'
    )
    tags = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Tags as string (not used, use tagIds)')
    tagIds = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text='Tag IDs'
    )
    productIds = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Product IDs (not used in model)'
    )
    locale = serializers.CharField(required=False, default='fa', max_length=10, help_text='Locale code (e.g., fa, en)')
    files = serializers.ListField(
        child=FileSerializer(),
        required=False,
        allow_empty=True,
        help_text='Files (not used in model)'
    )


class BlogPostCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for BlogPost that matches old Swagger output format."""
    authorId = serializers.CharField(source='author_name', read_only=True, allow_null=True)
    parentId = serializers.IntegerField(source='category_id', read_only=True, allow_null=True)
    type = serializers.SerializerMethodField()
    metaTitle = serializers.SerializerMethodField()
    imageUrl = serializers.CharField(source='featured_image', read_only=True, allow_null=True)
    thumbnail = serializers.SerializerMethodField()
    summery = serializers.CharField(source='excerpt', read_only=True, allow_null=True)
    published = serializers.DateTimeField(source='published_at', read_only=True, allow_null=True)
    categories = serializers.SerializerMethodField()
    categoryIds = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    tagIds = serializers.SerializerMethodField()
    productIds = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'authorId', 'parentId', 'title', 'type', 'metaTitle', 'slug',
            'imageUrl', 'thumbnail', 'summery', 'content', 'published',
            'categories', 'categoryIds', 'tags', 'tagIds', 'productIds',
            'locale', 'files'
        ]
        read_only_fields = ['id']
    
    def get_type(self, obj):
        """Return default type (not in model)."""
        return 0
    
    def get_metaTitle(self, obj):
        """Return meta title (not in model, use title)."""
        return obj.title
    
    def get_thumbnail(self, obj):
        """Return thumbnail (not in model, use featured_image)."""
        return obj.featured_image or ''
    
    def get_categories(self, obj):
        """Return categories as string (not in model)."""
        if obj.category:
            return obj.category.name
        return ''
    
    def get_categoryIds(self, obj):
        """Return category IDs as array."""
        if obj.category:
            return [obj.category.id]
        return []
    
    def get_tags(self, obj):
        """Return tags as string (comma-separated)."""
        tag_names = list(obj.tags.values_list('name', flat=True))
        return ', '.join(tag_names) if tag_names else ''
    
    def get_tagIds(self, obj):
        """Return tag IDs as array."""
        return list(obj.tags.values_list('id', flat=True))
    
    def get_productIds(self, obj):
        """Return product IDs (not in model, empty array)."""
        return []
    
    def get_files(self, obj):
        """Return files (not in model, empty array)."""
        return []


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


class BlogPostSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching blog posts (admin) matching old Swagger format."""
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
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Post type (not used in model)')


class BlogPostClientSearchRequestSerializer(serializers.Serializer):
    """Request serializer for client search matching old Swagger format."""
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0)
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blogPostCategoryId = serializers.IntegerField(required=False, allow_null=True, help_text='Blog post category ID')
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Post type (not used in model)')

