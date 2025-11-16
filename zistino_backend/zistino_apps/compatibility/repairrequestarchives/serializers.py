"""
Serializers for RepairRequestArchives endpoints.
"""
from rest_framework import serializers


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for repair request archive search."""
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


class RepairRequestArchiveSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching repair request archives matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID string)')
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')


class RepairRequestArchiveSerializer(serializers.Serializer):
    """Request serializer for updating repair request archive matching old Swagger format."""
    id = serializers.CharField(read_only=True)
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    createdAt = serializers.DateTimeField(read_only=True)

