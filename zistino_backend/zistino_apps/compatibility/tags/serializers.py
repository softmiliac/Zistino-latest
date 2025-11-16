"""
Serializers for Tags endpoints matching old Swagger format.
"""
from rest_framework import serializers
from zistino_apps.content.models import Tag
from zistino_apps.content.serializers import TagSerializer


class TagDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for Tag matching old Swagger format."""
    masterId = serializers.SerializerMethodField()
    type = serializers.IntegerField(default=0, read_only=True)
    masterText = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'text', 'description', 'masterId', 'type', 'masterText', 'locale']
        read_only_fields = ['id']
    
    def get_masterId(self, obj):
        """Get master ID (always null as Tag model doesn't have master)."""
        return None
    
    def get_masterText(self, obj):
        """Get master text (always null as Tag model doesn't have master)."""
        return None


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for tag search."""
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


class TagCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating tag matching old Swagger format."""
    text = serializers.CharField(required=True, max_length=255, help_text='Tag text')
    description = serializers.CharField(required=False, allow_blank=True, default='', help_text='Tag description')
    masterId = serializers.IntegerField(required=False, default=0, help_text='Master tag ID (0 for top-level, not used)')
    type = serializers.IntegerField(required=False, default=0, help_text='Tag type (not used)')
    locale = serializers.CharField(required=False, allow_blank=True, default='fa', help_text='Locale')


class TagSearchRequestSerializer(serializers.Serializer):
    """Request serializer for tag search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 treated as 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 treated as 1)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=list,
        allow_empty=True,
        help_text='Order by fields'
    )
    type = serializers.IntegerField(required=False, default=0, help_text='Tag type filter (not used)')
