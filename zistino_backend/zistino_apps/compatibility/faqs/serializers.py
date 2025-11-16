"""
Serializers for Faqs endpoints.
"""
from rest_framework import serializers
from zistino_apps.products.models import FAQ


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for FAQ search."""
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


class FaqCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating FAQ matching old Swagger format."""
    categoryId = serializers.IntegerField(required=False, default=0, help_text='Category ID (not used, for compatibility only)')
    title = serializers.CharField(required=True, help_text='FAQ title/question')
    description = serializers.CharField(required=False, allow_blank=True, default='', help_text='FAQ description/answer')
    locale = serializers.CharField(required=False, allow_blank=True, default='', help_text='Locale (not used, for compatibility only)')


class FaqSerializer(serializers.ModelSerializer):
    """Serializer for FAQ - maps to Flutter's expected format."""
    # Flutter expects: id, title, description, categoryId, categoryName
    title = serializers.CharField(source='question', read_only=True)
    description = serializers.CharField(source='answer', read_only=True, allow_blank=True)
    categoryId = serializers.IntegerField(default=0, read_only=True)  # TODO: Add category field to FAQ model
    categoryName = serializers.CharField(default='', read_only=True, allow_blank=True)  # TODO: Add category field to FAQ model
    # For input (create/update), accept both 'title'/'question' and 'description'/'answer'
    question = serializers.CharField(required=False, write_only=True)
    answer = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = FAQ
        fields = [
            'id', 'title', 'description', 'categoryId', 'categoryName',
            'question', 'answer', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'categoryId', 'categoryName', 'title', 'description']

    def to_internal_value(self, data):
        """Map 'title' to 'question' and 'description' to 'answer' for input."""
        # Create a copy to avoid modifying the original
        data = data.copy()
        
        # Map 'title' to 'question' if present
        if 'title' in data and 'question' not in data:
            data['question'] = data['title']
        
        # Map 'description' to 'answer' if present
        if 'description' in data and 'answer' not in data:
            data['answer'] = data['description']
        
        # Make question required only for create (when instance is None)
        if self.instance is None and 'question' not in data and 'title' not in data:
            raise serializers.ValidationError({'title': 'This field is required.'})
        
        return super().to_internal_value(data)


class FaqSearchRequestSerializer(serializers.Serializer):
    """Request serializer for FAQ search matching old Swagger format."""
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
    categoryId = serializers.IntegerField(required=False, default=0, help_text='Category ID (not used, for compatibility only)')


class FaqClientSearchRequestSerializer(serializers.Serializer):
    """Request serializer for FAQ client search matching old Swagger format."""
    categoryId = serializers.IntegerField(required=False, default=0, help_text='Category ID (not used, for compatibility only)')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')


class FaqClientSearchExRequestSerializer(serializers.Serializer):
    """Request serializer for FAQ client extended search matching old Swagger format."""
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
    categoryId = serializers.IntegerField(required=False, default=0, help_text='Category ID (not used, for compatibility only)')

