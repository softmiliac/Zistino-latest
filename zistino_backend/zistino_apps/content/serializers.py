from rest_framework import serializers
from .models import Testimonial, Tag, MenuLink, BlogCategory, BlogTag, BlogPost


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'text', 'imageUrl', 'rate', 'locale', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    imageUrl = serializers.CharField(source='image_url', allow_blank=True, required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'text', 'description', 'locale', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    createdAt = serializers.DateTimeField(source='created_at', read_only=True)


class MenuLinkSerializer(serializers.ModelSerializer):
    parentId = serializers.IntegerField(source='parent_id', allow_null=True, required=False, read_only=True)

    class Meta:
        model = MenuLink
        fields = ['id', 'name', 'linkUrl', 'parentId', 'imageUrl', 'locale', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    linkUrl = serializers.CharField(source='link_url')
    imageUrl = serializers.CharField(source='image_url', allow_blank=True, required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)


# Request serializers for search endpoints
class ProblemSearchRequestSerializer(serializers.Serializer):
    """Request serializer for problem search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)


class TestimonialSearchRequestSerializer(serializers.Serializer):
    """Request serializer for testimonial search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")


class TagSearchRequestSerializer(serializers.Serializer):
    """Request serializer for tag search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)


class MenuLinkSearchRequestSerializer(serializers.Serializer):
    """Request serializer for menu link search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    orderBy = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="List of field names to order by (e.g., ['name'])"
    )


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for Blog Category."""
    imageUrl = serializers.CharField(source='image_url', allow_blank=True, required=False)

    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'imageUrl', 'locale', 'is_active', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    createdAt = serializers.DateTimeField(source='created_at', read_only=True)


class BlogTagSerializer(serializers.ModelSerializer):
    """Serializer for Blog Tag."""
    class Meta:
        model = BlogTag
        fields = ['id', 'name', 'slug', 'description', 'locale', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    createdAt = serializers.DateTimeField(source='created_at', read_only=True)


class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer for Blog Post."""
    categoryId = serializers.IntegerField(source='category_id', allow_null=True, required=False, read_only=True)
    featuredImage = serializers.CharField(source='featured_image', allow_blank=True, required=False)
    authorName = serializers.CharField(source='author_name', allow_blank=True, required=False)
    isPublished = serializers.BooleanField(source='is_published')
    publishedAt = serializers.DateTimeField(source='published_at', allow_null=True, required=False)
    viewsCount = serializers.IntegerField(source='views_count', read_only=True)
    tagIds = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featuredImage',
            'categoryId', 'tagIds', 'authorName', 'isPublished', 'publishedAt',
            'viewsCount', 'locale', 'createdAt'
        ]
        read_only_fields = ['id', 'viewsCount', 'createdAt']

    def get_tagIds(self, obj):
        """Return list of tag IDs."""
        return list(obj.tags.values_list('id', flat=True))


# Request serializers for blog search endpoints
class BlogPostSearchRequestSerializer(serializers.Serializer):
    """Request serializer for blog post search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")


class BlogCategorySearchRequestSerializer(serializers.Serializer):
    """Request serializer for blog category search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")


class BlogTagSearchRequestSerializer(serializers.Serializer):
    """Request serializer for blog tag search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")

