"""
Serializers for Localizations endpoints.
"""
from rest_framework import serializers
from .models import Localization


class LocalizationSerializer(serializers.ModelSerializer):
    """Serializer for Localization."""
    key = serializers.CharField()
    value = serializers.CharField()
    resourceSet = serializers.CharField(source='resource_set')
    locale = serializers.CharField()
    isActive = serializers.BooleanField(source='is_active')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Localization
        fields = ['id', 'key', 'value', 'resourceSet', 'locale', 'isActive', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for localization search."""
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


class LocalizationCreateSerializer(serializers.Serializer):
    """Request serializer for creating a localization matching old Swagger format."""
    resourceSet = serializers.CharField(required=True, help_text='Resource set name')
    locale = serializers.CharField(required=True, help_text='Locale code (e.g., "en", "fa")')
    key = serializers.CharField(required=True, help_text='Translation key')
    text = serializers.CharField(required=True, help_text='Translated text (maps to value)')
    
    def create(self, validated_data):
        """Create a new localization."""
        from .models import Localization
        return Localization.objects.create(
            resource_set=validated_data['resourceSet'],
            locale=validated_data['locale'],
            key=validated_data['key'],
            value=validated_data['text'],  # Map 'text' to 'value'
            is_active=True
        )


class LocalizationSearchRequestSerializer(serializers.Serializer):
    """Request serializer for localization search matching old Swagger format."""
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


class ResourceSetSerializer(serializers.Serializer):
    """Serializer for resource set response."""
    name = serializers.CharField()
    count = serializers.IntegerField()


class LocalizationByResourceSetSerializer(serializers.Serializer):
    """Serializer for localizations by resource set (key-value pairs)."""
    key = serializers.CharField()
    value = serializers.CharField()


class LocalizationDetailSerializer(serializers.Serializer):
    """Serializer for localization detail matching old Swagger format (with text field)."""
    id = serializers.IntegerField(read_only=True)
    resourceSet = serializers.CharField(source='resource_set', read_only=True)
    locale = serializers.CharField(read_only=True)
    key = serializers.CharField(read_only=True)
    text = serializers.CharField(source='value', read_only=True)  # Map 'value' to 'text' for output

