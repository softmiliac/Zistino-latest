"""
Serializers for Comment endpoints.
"""
from rest_framework import serializers
from zistino_apps.notifications.models import Comment
from zistino_apps.notifications.serializers import CommentSerializer


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


class CommentSearchRequestSerializer(serializers.Serializer):
    """Request serializer for comment search matching old Swagger format."""
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
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product UUID as string')
    examId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Exam ID (not used, for compatibility only)')
    jobId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Job ID (not used, for compatibility only)')
    blogId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Blog ID (not used, for compatibility only)')
    trackId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Track ID (not used, for compatibility only)')
    isAccepted = serializers.BooleanField(required=False, allow_null=True, help_text='Filter by accepted status')
    parentId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Parent comment ID (0 for top-level comments)')


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment."""
    product = serializers.UUIDField(required=True, help_text='Product UUID')
    parent = serializers.IntegerField(required=False, allow_null=True, help_text='Parent comment ID (for replies)')
    rate = serializers.IntegerField(required=False, min_value=0, max_value=5, default=0, help_text='Rating (0-5)')
    text = serializers.CharField(required=True, help_text='Comment text')
    user_full_name = serializers.CharField(required=False, allow_blank=True, help_text='User full name')
    user_image_url = serializers.URLField(required=False, allow_blank=True, help_text='User image URL')
    product_image = serializers.URLField(required=False, allow_blank=True, help_text='Product image URL')


class CommentCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating a comment matching old Swagger format."""
    parentId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Parent comment ID (0 for top-level comments)')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product UUID as string (e.g., "94860000-b419-c60d-e381-08de1e92a377"). Required for create, optional for update.')
    examId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Exam ID (not used, for compatibility only)')
    jobId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Job ID (not used, for compatibility only)')
    trackId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Track ID (not used, for compatibility only)')
    blogId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Blog ID (not used, for compatibility only)')
    files = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='string', help_text='Files (not used, for compatibility only)')
    helpFul = serializers.IntegerField(required=False, default=0, help_text='Helpful count (not used, for compatibility only)')
    reported = serializers.IntegerField(required=False, default=0, help_text='Reported count (not used, for compatibility only)')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='string', help_text='Title (not used, for compatibility only)')
    type = serializers.IntegerField(required=False, default=0, help_text='Type (not used, for compatibility only)')
    rate = serializers.IntegerField(required=False, min_value=0, max_value=5, default=0, help_text='Rating (0-5)')
    text = serializers.CharField(required=False, allow_blank=True, help_text='Comment text (required for create, optional for update)')
    isAccepted = serializers.BooleanField(required=False, default=True, help_text='Whether comment is accepted (admin can set this)')
    
    def validate_productId(self, value):
        """Validate that productId is a valid UUID (not "string" placeholder)."""
        # Allow None/empty for updates (product shouldn't be changed)
        if not value or value == '':
            return None
        
        if value == 'string':
            raise serializers.ValidationError('productId must be a valid UUID, not "string"')
        try:
            import uuid
            uuid.UUID(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError(f'Invalid UUID format: "{value}"')
        return value


class CommentAnonymousSerializer(serializers.Serializer):
    """Serializer for creating an anonymous comment."""
    product = serializers.UUIDField(required=True, help_text='Product UUID')
    rate = serializers.IntegerField(required=False, min_value=0, max_value=5, default=0, help_text='Rating (0-5)')
    text = serializers.CharField(required=True, help_text='Comment text')
    user_full_name = serializers.CharField(required=True, help_text='User full name (required for anonymous)')
    user_image_url = serializers.URLField(required=False, allow_blank=True, help_text='User image URL')


class CommentAnonymousRequestSerializer(serializers.Serializer):
    """Request serializer for creating an anonymous comment matching old Swagger format."""
    parentId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Parent comment ID (0 for top-level comments)')
    productId = serializers.CharField(required=True, help_text='Product UUID as string')
    examId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Exam ID (not used, for compatibility only)')
    jobId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Job ID (not used, for compatibility only)')
    trackId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Track ID (not used, for compatibility only)')
    blogId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Blog ID (not used, for compatibility only)')
    files = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='string', help_text='Files (not used, for compatibility only)')
    helpFul = serializers.IntegerField(required=False, default=0, help_text='Helpful count (not used, for compatibility only)')
    reported = serializers.IntegerField(required=False, default=0, help_text='Reported count (not used, for compatibility only)')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='string', help_text='Title (not used, for compatibility only)')
    type = serializers.IntegerField(required=False, default=0, help_text='Type (not used, for compatibility only)')
    rate = serializers.IntegerField(required=False, min_value=0, max_value=5, default=0, help_text='Rating (0-5)')
    text = serializers.CharField(required=True, help_text='Comment text')
    isAccepted = serializers.BooleanField(required=False, default=True, help_text='Whether comment is accepted (admin can set this)')
    
    def validate_productId(self, value):
        """Validate that productId is a valid UUID (not "string" placeholder)."""
        if value == 'string' or not value:
            raise serializers.ValidationError('productId must be a valid UUID, not "string"')
        try:
            import uuid
            uuid.UUID(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError(f'Invalid UUID format: "{value}"')
        return value


class CommentByUserIdRequestSerializer(serializers.Serializer):
    """Request serializer for getting comments by user ID matching old Swagger format."""
    userId = serializers.UUIDField(required=True, help_text='User UUID')
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0)
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )


class CommentByUserIdSerializer(serializers.Serializer):
    """Request serializer for getting comments by user ID."""
    userId = serializers.UUIDField(required=True, help_text='User UUID')


class CommentNotifyMeSerializer(serializers.Serializer):
    """Request serializer for notify me endpoint."""
    productId = serializers.UUIDField(required=True, help_text='Product UUID')


class CommentCompatibilitySerializer(serializers.Serializer):
    """Compatibility serializer for Comment that matches old Swagger output format."""
    id = serializers.IntegerField(read_only=True)
    userId = serializers.SerializerMethodField()
    userEmail = serializers.SerializerMethodField()
    userPhoneNumber = serializers.SerializerMethodField()
    userFullName = serializers.SerializerMethodField()
    userThumbnail = serializers.SerializerMethodField()
    parentId = serializers.SerializerMethodField()
    productId = serializers.SerializerMethodField()
    productName = serializers.SerializerMethodField()
    examId = serializers.SerializerMethodField()
    jobId = serializers.SerializerMethodField()
    blogId = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    helpFul = serializers.SerializerMethodField()
    reported = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    rate = serializers.IntegerField(read_only=True)
    text = serializers.CharField(read_only=True)
    isAccepted = serializers.BooleanField(source='is_accepted', read_only=True)
    createdOn = serializers.DateTimeField(source='created_on', read_only=True)
    
    def get_userId(self, obj):
        """Return user ID as UUID string."""
        if obj.user:
            return str(obj.user.id)
        return None
    
    def get_userEmail(self, obj):
        """Return user email."""
        if obj.user:
            return obj.user.email or ''
        return ''
    
    def get_userPhoneNumber(self, obj):
        """Return user phone number."""
        if obj.user:
            return obj.user.phone_number or ''
        return ''
    
    def get_userFullName(self, obj):
        """Return user full name."""
        if obj.user_full_name:
            return obj.user_full_name
        if obj.user:
            name_parts = [obj.user.first_name, obj.user.last_name]
            return ' '.join(filter(None, name_parts)) or obj.user.username or obj.user.phone_number or ''
        return ''
    
    def get_userThumbnail(self, obj):
        """Return user thumbnail/image URL."""
        # First check if comment has user_image_url
        if obj.user_image_url:
            request = self.context.get('request')
            if request and not obj.user_image_url.startswith('http'):
                return request.build_absolute_uri(obj.user_image_url)
            return obj.user_image_url
        
        # Then check user's image_url field
        if obj.user and hasattr(obj.user, 'image_url') and obj.user.image_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.image_url.url)
            return str(obj.user.image_url.url) if hasattr(obj.user.image_url, 'url') else str(obj.user.image_url)
        
        return ''
    
    def get_parentId(self, obj):
        """Return parent comment ID."""
        return obj.parent.id if obj.parent else None
    
    def get_productId(self, obj):
        """Return product ID as UUID string."""
        if obj.product:
            return str(obj.product.id)
        return None
    
    def get_productName(self, obj):
        """Return product name."""
        if obj.product:
            return obj.product.name or ''
        return ''
    
    def get_examId(self, obj):
        """Return null (not used)."""
        return None
    
    def get_jobId(self, obj):
        """Return null (not used)."""
        return None
    
    def get_blogId(self, obj):
        """Return null (not used)."""
        return None
    
    def get_files(self, obj):
        """Return 'string' (not used, for compatibility)."""
        return 'string'
    
    def get_title(self, obj):
        """Return 'string' (not used, for compatibility)."""
        return 'string'
    
    def get_helpFul(self, obj):
        """Return 0 (not used, for compatibility)."""
        return 0
    
    def get_reported(self, obj):
        """Return 0 (not used, for compatibility)."""
        return 0
    
    def get_type(self, obj):
        """Return 0 (not used, for compatibility)."""
        return 0


class CommentWithChildrenSerializer(CommentCompatibilitySerializer):
    """Compatibility serializer for Comment with children (nested replies) matching old Swagger format."""
    children = serializers.SerializerMethodField()
    productImage = serializers.SerializerMethodField()
    helpFul = serializers.SerializerMethodField()
    reported = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    jobId = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    examId = serializers.SerializerMethodField()
    blogId = serializers.SerializerMethodField()
    
    def get_children(self, obj):
        """Return nested children comments."""
        children = obj.children.filter(is_accepted=True).select_related('user', 'product', 'parent')
        return CommentWithChildrenSerializer(children, many=True, context=self.context).data
    
    def get_productImage(self, obj):
        """Return product image URL."""
        if obj.product_image:
            request = self.context.get('request')
            if request and not obj.product_image.startswith('http'):
                return request.build_absolute_uri(obj.product_image)
            return obj.product_image
        if obj.product and hasattr(obj.product, 'image') and obj.product.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.image.url)
            return str(obj.product.image.url) if hasattr(obj.product.image, 'url') else str(obj.product.image)
        return None
    
    def get_helpFul(self, obj):
        """Return null (not used)."""
        return None
    
    def get_reported(self, obj):
        """Return null (not used)."""
        return None
    
    def get_type(self, obj):
        """Return null (not used)."""
        return None
    
    def get_jobId(self, obj):
        """Return null (not used)."""
        return None
    
    def get_files(self, obj):
        """Return empty string (not used, for compatibility)."""
        return ''
    
    def get_title(self, obj):
        """Return empty string (not used, for compatibility)."""
        return ''
    
    def get_examId(self, obj):
        """Return 0 (not used)."""
        return 0
    
    def get_blogId(self, obj):
        """Return null (not used)."""
        return None

