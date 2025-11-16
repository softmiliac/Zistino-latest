"""
Serializers for ProductProblems endpoints.
These import from products app serializers and add compatibility request/response serializers.
"""
from zistino_apps.products.serializers import ProblemSerializer, ProblemSearchRequestSerializer
from rest_framework import serializers


# Reuse ProblemSerializer and ProblemSearchRequestSerializer from products app
# These are already compatible with Flutter app expectations

# Additional serializers for ProductProblems-specific endpoints
class ProductProblemGroupSerializer(serializers.Serializer):
    """Serializer for product problem group operations matching old Swagger format."""
    productId = serializers.CharField(required=True, help_text='Product UUID')
    roleId = serializers.CharField(required=True, help_text='Role UUID')


class ProductProblemItemSerializer(serializers.Serializer):
    """Serializer for individual product problem item in save-range request."""
    id = serializers.IntegerField(required=False, default=0, help_text='Product problem ID (0 for new, >0 for update)')
    problemId = serializers.IntegerField(required=False, default=0, help_text='Problem ID (0 for new, >0 for update)')
    productId = serializers.CharField(required=True, help_text='Product UUID')
    roleId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Role ID (optional, not stored in Problem model)')
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, default=0)
    isActive = serializers.BooleanField(required=False, default=True, help_text='Active status (optional, not stored in Problem model)')


class ProductProblemSaveRangeSerializer(serializers.Serializer):
    """Serializer for saving a range of product problems matching old Swagger format."""
    productId = serializers.CharField(required=True, help_text='Product UUID')
    productProblems = serializers.ListField(
        child=ProductProblemItemSerializer(),
        required=True,
        help_text='List of product problem objects to save'
    )


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for product problem group search."""
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


class ProductProblemSearchGroupRequestSerializer(serializers.Serializer):
    """Request serializer for searching problem groups matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0, help_text='Page number (0 defaults to 1)')
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0, help_text='Page size (0 defaults to 1)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )
    productId = serializers.CharField(required=False, allow_null=True, allow_blank=True, help_text='Product UUID to filter by')


class ProductProblemCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating/updating product problems matching old Swagger format."""
    problemId = serializers.IntegerField(required=False, default=0, help_text='Problem ID (0 for new, >0 for update)')
    productId = serializers.CharField(required=True, help_text='Product UUID')
    roleId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Role ID (optional, not stored in Problem model)')
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, default=0)
    isActive = serializers.BooleanField(required=False, default=True, help_text='Active status (optional, not stored in Problem model)')


class ProductProblemCompatibilitySerializer(serializers.Serializer):
    """Response serializer for product problems matching old Swagger format."""
    id = serializers.IntegerField(read_only=True, help_text='Product problem ID')
    problem = serializers.SerializerMethodField(help_text='Problem object (null in old Swagger)')
    product = serializers.SerializerMethodField(help_text='Product object (null in old Swagger)')
    roleId = serializers.CharField(read_only=True, help_text='Role UUID')
    price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2, help_text='Price')
    isActive = serializers.BooleanField(read_only=True, help_text='Active status')
    
    def get_problem(self, obj):
        """Return null as per old Swagger format."""
        return None
    
    def get_product(self, obj):
        """Return null as per old Swagger format."""
        return None
