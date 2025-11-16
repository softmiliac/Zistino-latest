"""
Serializers for MailTemplates endpoints.
"""
from rest_framework import serializers
from .models import MailTemplate


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for mail template search."""
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


class MailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for MailTemplate."""
    templateType = serializers.CharField(source='template_type')
    isActive = serializers.BooleanField(source='is_active')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = MailTemplate
        fields = ['id', 'name', 'subject', 'body', 'templateType', 'locale', 'isActive', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class MailTemplateCreateSerializer(serializers.Serializer):
    """Request serializer for creating a mail template matching old Swagger format."""
    name = serializers.CharField(required=True, help_text='Template name/identifier')
    # Note: 'from' is a Python reserved keyword - we'll handle it manually
    to = serializers.CharField(required=False, allow_blank=True, default='', help_text='To email address (not used, for compatibility only)')
    subject = serializers.CharField(required=True, help_text='Email subject line')
    body = serializers.CharField(required=True, help_text='Email body (HTML or plain text)')
    locale = serializers.CharField(required=True, help_text='Language code (e.g., "en", "fa")')
    
    def to_internal_value(self, data):
        """Handle 'from' field which is a Python reserved keyword."""
        # Allow 'from' field without validation (for compatibility)
        # We'll extract it but not use it
        if isinstance(data, dict) and 'from' in data:
            # Just keep it in the data but don't validate it
            pass
        return super().to_internal_value(data)
    
    def is_valid(self, raise_exception=False):
        """Override to allow 'from' field without validation errors."""
        # Get initial data
        if hasattr(self, 'initial_data'):
            # Remove 'from' temporarily for validation, then add it back
            initial_data = self.initial_data
            if isinstance(initial_data, dict) and 'from' in initial_data:
                # Store 'from' value
                from_value = initial_data.get('from')
                # Create a copy without 'from' for validation
                data_without_from = {k: v for k, v in initial_data.items() if k != 'from'}
                # Temporarily replace initial_data
                self.initial_data = data_without_from
                try:
                    result = super().is_valid(raise_exception=raise_exception)
                    # Restore 'from' in initial_data for reference
                    if isinstance(self.initial_data, dict):
                        self.initial_data['from'] = from_value
                    return result
                finally:
                    # Restore original initial_data
                    self.initial_data = initial_data
        return super().is_valid(raise_exception=raise_exception)
    
    def create(self, validated_data):
        """Create a new mail template."""
        from .models import MailTemplate
        # Remove 'to' as it's not used (from is already not in validated_data)
        validated_data.pop('to', None)
        return MailTemplate.objects.create(
            name=validated_data['name'],
            subject=validated_data['subject'],
            body=validated_data['body'],
            template_type=validated_data.get('name', ''),  # Use name as template_type if not provided
            locale=validated_data['locale'],
            is_active=True
        )


class MailTemplateDetailSerializer(serializers.Serializer):
    """Serializer for mail template detail matching old Swagger format (with from and to fields)."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    from_field = serializers.SerializerMethodField(help_text='From email address (placeholder)')
    to = serializers.SerializerMethodField(help_text='To email address (placeholder)')
    subject = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True, required=False)
    locale = serializers.CharField(read_only=True)
    
    def __init__(self, *args, include_body=True, **kwargs):
        """Initialize serializer with optional body field."""
        super().__init__(*args, **kwargs)
        self.include_body = include_body
    
    def get_from_field(self, obj):
        """Return placeholder 'from' value."""
        return 'a'  # Placeholder value matching old Swagger
    
    def get_to(self, obj):
        """Return placeholder 'to' value."""
        return 'b'  # Placeholder value matching old Swagger
    
    def to_representation(self, instance):
        """Convert to representation with 'from' field name."""
        # Get the model instance fields
        ret = {
            'id': getattr(instance, 'id', None),
            'name': getattr(instance, 'name', ''),
            'from': self.get_from_field(instance),  # Use 'from' directly in output
            'to': self.get_to(instance),
            'subject': getattr(instance, 'subject', ''),
            'locale': getattr(instance, 'locale', '')
        }
        # Include body only if specified
        if self.include_body:
            ret['body'] = getattr(instance, 'body', '')
        return ret


class MailTemplateSearchRequestSerializer(serializers.Serializer):
    """Request serializer for mail template search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 = page 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 = all results)')
    orderBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )

