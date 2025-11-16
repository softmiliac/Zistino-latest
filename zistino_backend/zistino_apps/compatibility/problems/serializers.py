"""
Serializers for Problems endpoints matching old Swagger format.
"""
from rest_framework import serializers
from zistino_apps.products.models import Problem


class AdvancedSearchSerializer(serializers.Serializer):
    """Nested advanced search serializer."""
    fields = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True
    )
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    groupBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True
    )


class ProblemCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating problem matching old Swagger format."""
    title = serializers.CharField(required=True, help_text='Problem title')
    description = serializers.CharField(required=False, allow_blank=True, default='', help_text='Problem description')
    iconUrl = serializers.CharField(required=False, allow_blank=True, default='', help_text='Icon URL')
    parentId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Parent problem ID (0 for top-level)')
    repairDuration = serializers.IntegerField(required=False, default=0, help_text='Repair duration in minutes')
    priority = serializers.IntegerField(required=False, default=0, help_text='Display priority')
    locale = serializers.CharField(required=False, allow_blank=True, default='', help_text='Locale')
    # Note: productId is required by the model but not in old Swagger request
    # We'll handle this in the view - use a default product or make it optional


class ProblemSearchRequestSerializer(serializers.Serializer):
    """Request serializer for problem search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 treated as 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 treated as all results)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True,
        help_text='Order by fields'
    )
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID)')


class ProblemDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for Problem matching old Swagger format exactly."""
    parentId = serializers.SerializerMethodField()
    iconUrl = serializers.SerializerMethodField()
    repairDuration = serializers.IntegerField(source='repair_duration', read_only=True)

    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'description', 'iconUrl', 'parentId', 'repairDuration',
            'priority', 'locale'
        ]
        read_only_fields = ['id']

    def get_parentId(self, obj):
        """Get parent ID, return None if no parent."""
        return obj.parent_id if obj.parent_id else None

    def get_iconUrl(self, obj):
        """Get icon URL, return 'string' if empty (matching old Swagger format)."""
        if obj.icon_url:
            return obj.icon_url
        return 'string'
