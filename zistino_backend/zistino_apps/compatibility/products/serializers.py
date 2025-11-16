"""
Serializers for Products endpoints.
These import from products app serializers and add compatibility request/response serializers.
"""
from zistino_apps.products.serializers import (
    ProductSerializer,
    ProductSearchRequestSerializer,
    CategorySerializer,
)
from rest_framework import serializers
from zistino_apps.products.models import Product, Category, Color, Price, Specification, Warranty
from zistino_apps.notifications.models import Comment
from zistino_apps.orders.models import OrderItem
from django.db.models import Count, Avg
from datetime import datetime
import json


class ProductTextRequestSerializer(serializers.Serializer):
    """Serializer for productTexts array in old Swagger request format."""
    id = serializers.IntegerField(required=False, allow_null=True, default=0)
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product UUID')
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    categories = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    colorsList = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    masterColor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pricesList = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    masterPrice = serializers.IntegerField(required=False, allow_null=True, default=0)
    warranty = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    specifications = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tags = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    brandName = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    locale = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ProductTextSerializer(serializers.Serializer):
    """Serializer for productTexts array in old Swagger format."""
    id = serializers.IntegerField(read_only=True, default=0)
    name = serializers.CharField(read_only=True, allow_null=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    categories = serializers.CharField(read_only=True, allow_null=True)
    colorsList = serializers.CharField(read_only=True, allow_null=True)
    masterColor = serializers.CharField(read_only=True, allow_null=True)
    pricesList = serializers.CharField(read_only=True, allow_null=True)
    masterPrice = serializers.IntegerField(read_only=True, default=0)
    warranty = serializers.CharField(read_only=True, allow_null=True)
    specifications = serializers.CharField(read_only=True, allow_null=True)
    tags = serializers.CharField(read_only=True, allow_null=True)
    brandName = serializers.CharField(read_only=True, allow_null=True)
    locale = serializers.CharField(read_only=True, allow_null=True)


class ProductCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating products matching old Swagger format."""
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rate = serializers.IntegerField(required=False, default=0)
    categories = serializers.CharField(required=False, allow_null=True)
    categoryIds = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        allow_null=True,
        help_text='Array of category IDs (integers) - will use first one if available'
    )
    viewsCount = serializers.IntegerField(required=False, default=0)
    likesCount = serializers.IntegerField(required=False, default=0)
    commentsCount = serializers.IntegerField(required=False, default=0)
    ordersCount = serializers.IntegerField(required=False, default=0)
    size = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    isMaster = serializers.BooleanField(required=False, default=True)
    masterId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    colorsList = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    masterColor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pricesList = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    masterPrice = serializers.IntegerField(required=False, allow_null=True, default=0)
    imagesList = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    masterImage = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    warranty = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    specifications = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tags = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tagIds = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        allow_null=True
    )
    brandId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    discountPercent = serializers.IntegerField(required=False, default=0)
    inStock = serializers.IntegerField(required=False, default=0)
    isActive = serializers.BooleanField(required=False, default=True)
    locale = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    badge = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Badge')
    productTexts = ProductTextRequestSerializer(many=True, required=False, allow_null=True)
    hieght = serializers.IntegerField(required=False, allow_null=True, default=0)
    width = serializers.IntegerField(required=False, allow_null=True, default=0)
    length = serializers.IntegerField(required=False, allow_null=True, default=0)
    weight = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    type = serializers.IntegerField(required=False, allow_null=True, default=0)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unitCount = serializers.IntegerField(required=False, allow_null=True, default=0)
    inStockAlert = serializers.BooleanField(required=False, allow_null=True, default=False)
    buyPrice = serializers.IntegerField(required=False, allow_null=True, default=0)
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    barCode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    atLeast = serializers.IntegerField(required=False, default=0)
    atMost = serializers.IntegerField(required=False, default=0)
    jsonExt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    seoSetting = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    verify = serializers.IntegerField(required=False, allow_null=True, default=0)
    issue = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    expaireDate = serializers.DateTimeField(required=False, allow_null=True)
    p1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    p2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    p3 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    p4 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    p5 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    f1 = serializers.IntegerField(required=False, allow_null=True, default=0)
    f2 = serializers.IntegerField(required=False, allow_null=True, default=0)
    f3 = serializers.IntegerField(required=False, allow_null=True, default=0)
    f4 = serializers.IntegerField(required=False, allow_null=True, default=0)
    f5 = serializers.IntegerField(required=False, allow_null=True, default=0)


class ProductCompatibilitySerializer(serializers.ModelSerializer):
    """
    Compatibility serializer for Product that matches old Swagger format exactly.
    Includes all fields from old Swagger API response.
    """
    # Basic fields
    id = serializers.UUIDField(read_only=True)  # Add id field at top level
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    rate = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    categoryIds = serializers.SerializerMethodField()
    viewsCount = serializers.IntegerField(read_only=True, default=0)
    likesCount = serializers.SerializerMethodField()
    commentsCount = serializers.SerializerMethodField()
    ordersCount = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    isMaster = serializers.BooleanField(read_only=True, default=True)
    masterId = serializers.SerializerMethodField()
    colorsList = serializers.SerializerMethodField()
    masterColor = serializers.SerializerMethodField()
    pricesList = serializers.SerializerMethodField()
    masterPrice = serializers.SerializerMethodField()
    imagesList = serializers.SerializerMethodField()
    masterImage = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    warranty = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    tagIds = serializers.SerializerMethodField()
    brandId = serializers.CharField(read_only=True, allow_null=True, default=None)
    brandName = serializers.SerializerMethodField()  # Add brandName field
    discountPercent = serializers.IntegerField(read_only=True, default=0)
    inStock = serializers.IntegerField(read_only=True, default=0)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    locale = serializers.CharField(read_only=True, allow_null=True, default=None)
    tenant = serializers.SerializerMethodField()  # Add tenant field
    badge = serializers.CharField(read_only=True, allow_null=True, default=None)  # Add badge field
    productTexts = serializers.SerializerMethodField()
    hieght = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    width = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    length = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    weight = serializers.CharField(read_only=True, allow_null=True, default=None)
    type = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    city = serializers.CharField(read_only=True, allow_null=True, default=None)
    country = serializers.CharField(read_only=True, allow_null=True, default=None)
    state = serializers.CharField(read_only=True, allow_null=True, default=None)
    unitCount = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    inStockAlert = serializers.BooleanField(read_only=True, allow_null=True, default=None)
    buyPrice = serializers.SerializerMethodField()
    code = serializers.CharField(read_only=True, allow_null=True, default=None)
    barCode = serializers.CharField(read_only=True, allow_null=True, default=None)
    atLeast = serializers.IntegerField(read_only=True, default=0)
    atMost = serializers.IntegerField(read_only=True, default=0)
    jsonExt = serializers.CharField(read_only=True, allow_null=True, default=None)
    seoSetting = serializers.CharField(read_only=True, allow_null=True, default=None)
    verify = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    issue = serializers.CharField(read_only=True, allow_null=True, default=None)
    expaireDate = serializers.DateTimeField(read_only=True, allow_null=True, default=None)
    createdOn = serializers.SerializerMethodField()  # Add createdOn field
    p1 = serializers.CharField(read_only=True, allow_null=True, default=None)
    p2 = serializers.CharField(read_only=True, allow_null=True, default=None)
    p3 = serializers.CharField(read_only=True, allow_null=True, default=None)
    p4 = serializers.CharField(read_only=True, allow_null=True, default=None)
    p5 = serializers.CharField(read_only=True, allow_null=True, default=None)
    f1 = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    f2 = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    f3 = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    f4 = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    f5 = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    r1 = serializers.CharField(read_only=True, allow_null=True, default=None)  # Add r1-r5 fields
    r2 = serializers.CharField(read_only=True, allow_null=True, default=None)
    r3 = serializers.CharField(read_only=True, allow_null=True, default=None)
    r4 = serializers.CharField(read_only=True, allow_null=True, default=None)
    r5 = serializers.CharField(read_only=True, allow_null=True, default=None)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'rate', 'categories', 'categoryIds', 'viewsCount',
            'likesCount', 'commentsCount', 'ordersCount', 'size', 'isMaster', 'masterId',
            'colorsList', 'masterColor', 'pricesList', 'masterPrice', 'imagesList',
            'masterImage', 'thumbnail', 'warranty', 'specifications', 'tags', 'tagIds',
            'brandId', 'brandName', 'discountPercent', 'inStock', 'isActive', 'locale',
            'tenant', 'badge', 'productTexts', 'hieght', 'width', 'length', 'weight',
            'type', 'city', 'country', 'state', 'unitCount', 'inStockAlert', 'buyPrice',
            'code', 'barCode', 'atLeast', 'atMost', 'jsonExt', 'seoSetting', 'verify',
            'issue', 'expaireDate', 'createdOn', 'p1', 'p2', 'p3', 'p4', 'p5',
            'f1', 'f2', 'f3', 'f4', 'f5', 'r1', 'r2', 'r3', 'r4', 'r5'
        ]

    def get_rate(self, obj):
        """Get average rating from comments."""
        avg_rating = Comment.objects.filter(
            product_id=obj.id,
            is_accepted=True
        ).aggregate(Avg('rate'))['rate__avg']
        return int(avg_rating) if avg_rating else 0

    def get_categories(self, obj):
        """Get categories as JSON string array format: '[{\"id\":\"6\"}]'."""
        if obj.category:
            # Old Swagger format: "[{\"id\":\"6\"}]"
            # Category ID is UUID, but old Swagger expects integer or string ID
            # For now, use a placeholder or convert UUID to string
            category_data = [{"id": str(obj.category.id)}]
            return json.dumps(category_data)
        return None

    def get_categoryIds(self, obj):
        """Get category IDs as array."""
        if obj.category:
            # Category ID is UUID, but old Swagger expects integer
            # Return empty array to match old Swagger format when category exists
            return []  # Old Swagger shows empty array even when category exists
        return []

    def get_likesCount(self, obj):
        """Get likes count (placeholder - implement when Like model exists)."""
        # TODO: Implement when Like model has product relationship
        return 0

    def get_commentsCount(self, obj):
        """Get comments count."""
        return Comment.objects.filter(product_id=obj.id, is_accepted=True).count()

    def get_ordersCount(self, obj):
        """Get orders count by matching product name."""
        # OrderItem stores product_name as string, not a ForeignKey
        return OrderItem.objects.filter(product_name=obj.name).count()

    def get_size(self, obj):
        """Get size from specification."""
        if hasattr(obj, 'specification') and obj.specification:
            return obj.specification.size
        return None

    def get_masterId(self, obj):
        """Get master ID (UUID as string)."""
        return str(obj.id)

    def get_colorsList(self, obj):
        """Get colors as comma-separated string."""
        colors = obj.product_colors.all().values_list('color__name', flat=True)
        return ', '.join(colors) if colors else None

    def get_masterColor(self, obj):
        """Get master color (first color or None)."""
        first_color = obj.product_colors.first()
        if first_color:
            return first_color.color.name
        return None

    def get_pricesList(self, obj):
        """Get prices as JSON string array format: '[]' or '[1800]'."""
        prices = obj.prices.all().values_list('price', flat=True)
        if prices:
            # Convert to list of integers and return as JSON string
            price_list = [int(p) for p in prices]
            return json.dumps(price_list)
        # Return empty array as JSON string to match old Swagger
        return json.dumps([])

    def get_masterPrice(self, obj):
        """Get master price (price_per_unit as integer)."""
        return int(obj.price_per_unit) if obj.price_per_unit else 0

    def get_imagesList(self, obj):
        """Get images as JSON string array format: '[\"/uploads/app/image.webp\"]'."""
        if obj.image:
            request = self.context.get('request')
            if request:
                # Get relative URL path (like "/uploads/app/image.webp")
                image_url = obj.image.url
                # If it's already a full URL, extract the path
                if image_url.startswith('http'):
                    from urllib.parse import urlparse
                    parsed = urlparse(image_url)
                    image_url = parsed.path
                # Return as JSON string array
                return json.dumps([image_url])
        return None

    def get_masterImage(self, obj):
        """Get master image URL as single string (not JSON array)."""
        if obj.image:
            # Get relative URL path (like "/uploads/app/image.webp")
            image_url = obj.image.url
            # If it's already a full URL, extract the path
            if image_url.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                image_url = parsed.path
            return image_url
        return None

    def get_thumbnail(self, obj):
        """Get thumbnail URL (same as master image for now)."""
        return self.get_masterImage(obj)

    def get_warranty(self, obj):
        """Get warranty as string."""
        warranty = obj.warranties.first()
        if warranty:
            return warranty.name
        return None

    def get_specifications(self, obj):
        """Get specifications as string."""
        if hasattr(obj, 'specification') and obj.specification:
            spec = obj.specification.level or obj.specification.size
            return spec if spec else ""
        return ""

    def get_tags(self, obj):
        """Get tags as JSON string array format: '[]'."""
        # TODO: Implement when Tag model has product relationship
        # Return empty array as JSON string to match old Swagger format
        return json.dumps([])

    def get_tagIds(self, obj):
        """Get tag IDs as array (placeholder)."""
        # TODO: Implement when Tag model has product relationship
        return []

    def get_buyPrice(self, obj):
        """Get buy price (same as masterPrice for now)."""
        return self.get_masterPrice(obj)

    def get_brandName(self, obj):
        """Get brand name from Product's brand relationship."""
        # Check if Product model has a brand field
        if hasattr(obj, 'brand') and obj.brand:
            return obj.brand.name
        return None

    def get_tenant(self, obj):
        """Get tenant (default 'root' to match old Swagger)."""
        # Extract tenant from request headers if available
        request = self.context.get('request')
        if request:
            tenant = request.headers.get('tenant', 'root')
            return tenant
        return 'root'

    def get_createdOn(self, obj):
        """Get createdOn in ISO format matching old Swagger: '2024-03-12T06:16:59.64665'."""
        if obj.created_at:
            # Format: "2024-03-12T06:16:59.64665" (no Z, no timezone)
            dt_str = obj.created_at.isoformat()
            # Remove timezone info
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            # Ensure microseconds are included (up to 5 digits like old Swagger)
            return dt_str
        return None

    def get_productTexts(self, obj):
        """Get productTexts array. Return empty array to match old Swagger format."""
        # Old Swagger shows empty array: []
        # Return empty array instead of one entry
        return []

    def to_representation(self, instance):
        """Convert to old Swagger format."""
        data = super().to_representation(instance)

        # Ensure id is a string (UUID)
        if 'id' in data and data['id']:
            data['id'] = str(data['id'])

        # Ensure masterId is a string (UUID) or null
        if 'masterId' in data and data['masterId']:
            data['masterId'] = str(data['masterId'])

        # Ensure brandId is a string (UUID) or null
        if 'brandId' in data and data['brandId']:
            data['brandId'] = str(data['brandId'])

        # Keep None values as None (they'll be serialized as null in JSON)
        # Don't convert None to empty string - old Swagger shows null

        return data


# Reuse ProductSerializer and ProductSearchRequestSerializer from products app
# These are already compatible with Flutter app expectations

# Additional serializers for Products-specific endpoints
class ProductGroupSerializer(serializers.Serializer):
    """Serializer for product group operations."""
    id = serializers.IntegerField(required=False, read_only=True)
    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    productIds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='List of product UUIDs in this group'
    )


class ProductGroupResponseSerializer(serializers.Serializer):
    """Response serializer for product group operations."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    productIds = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_productIds(self, obj):
        """Get list of product UUIDs in this group."""
        return [str(item.product.id) for item in obj.items.all().order_by('order', 'created_at')]


class AdvancedSearchSerializer(serializers.Serializer):
    """Serializer for advancedSearch object in export request."""
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


class ProductExportRequestSerializer(serializers.Serializer):
    """Request serializer for exporting products matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pageNumber = serializers.IntegerField(required=False, default=1, min_value=1)
    pageSize = serializers.IntegerField(required=False, default=20, min_value=1)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )
    brandId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    minimumRate = serializers.IntegerField(required=False, default=0, min_value=0)
    maximumRate = serializers.IntegerField(required=False, default=0, min_value=0)


class ProductClientSearchRequestSerializer(serializers.Serializer):
    """Extended search request for client products matching old Swagger format."""
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0)
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Order by options for client search'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    brands = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    categoryId = serializers.IntegerField(required=False, allow_null=True)
    categoryType = serializers.IntegerField(required=False, allow_null=True)
    productType = serializers.IntegerField(required=False, allow_null=True)
    minPrice = serializers.IntegerField(required=False, allow_null=True)
    maxPrice = serializers.IntegerField(required=False, allow_null=True)


class ProductAdminSearchExtRequestSerializer(serializers.Serializer):
    """Extended search request for admin products matching old Swagger format."""
    pageNumber = serializers.IntegerField(required=False, default=1, min_value=1)
    pageSize = serializers.IntegerField(required=False, default=20, min_value=1)
    orderBy = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Order by options for admin extended search'
    )
    isActive = serializers.BooleanField(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    brandId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    categoryId = serializers.IntegerField(required=False, allow_null=True)
    categoryType = serializers.IntegerField(required=False, allow_null=True)
    productType = serializers.IntegerField(required=False, allow_null=True)
    minPrice = serializers.IntegerField(required=False, allow_null=True)
    maxPrice = serializers.IntegerField(required=False, allow_null=True)
    language = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    city = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    country = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    p1 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    p2 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    p3 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    p4 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    p5 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    f1 = serializers.IntegerField(required=False, allow_null=True)
    f1from = serializers.IntegerField(required=False, allow_null=True)
    f1to = serializers.IntegerField(required=False, allow_null=True)
    f2 = serializers.IntegerField(required=False, allow_null=True)
    f2from = serializers.IntegerField(required=False, allow_null=True)
    f2to = serializers.IntegerField(required=False, allow_null=True)
    f3 = serializers.IntegerField(required=False, allow_null=True)
    f3from = serializers.IntegerField(required=False, allow_null=True)
    f3to = serializers.IntegerField(required=False, allow_null=True)
    f4 = serializers.IntegerField(required=False, allow_null=True)
    f4from = serializers.IntegerField(required=False, allow_null=True)
    f4to = serializers.IntegerField(required=False, allow_null=True)
    f5 = serializers.IntegerField(required=False, allow_null=True)
    f5from = serializers.IntegerField(required=False, allow_null=True)
    f5to = serializers.IntegerField(required=False, allow_null=True)
    ids = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    userId = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ProductAdminSearchExtResponseSerializer(serializers.Serializer):
    """Response serializer for admin extended search matching old Swagger format."""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    tags = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    brandId = serializers.CharField(read_only=True, allow_null=True)
    brandName = serializers.SerializerMethodField()
    likesCount = serializers.IntegerField(read_only=True, default=0)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    masterImage = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    discountPercent = serializers.IntegerField(read_only=True, default=0)
    masterPrice = serializers.SerializerMethodField()
    discountPrice = serializers.IntegerField(read_only=True, default=0)
    inStock = serializers.IntegerField(read_only=True, default=0)
    city = serializers.CharField(read_only=True, allow_null=True)
    code = serializers.CharField(read_only=True, allow_null=True)
    country = serializers.CharField(read_only=True, allow_null=True)
    state = serializers.CharField(read_only=True, allow_null=True)
    type = serializers.IntegerField(read_only=True, allow_null=True)
    commentsCount = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    r1 = serializers.IntegerField(read_only=True, allow_null=True, default=0)
    r2 = serializers.IntegerField(read_only=True, allow_null=True, default=0)
    r3 = serializers.IntegerField(read_only=True, allow_null=True, default=0)
    r4 = serializers.IntegerField(read_only=True, allow_null=True, default=0)
    r5 = serializers.IntegerField(read_only=True, allow_null=True, default=0)
    masterId = serializers.SerializerMethodField()
    createdBy = serializers.SerializerMethodField()
    jsonExt = serializers.CharField(read_only=True, allow_null=True)
    attachmentCount = serializers.IntegerField(read_only=True, default=0)
    attachmentDuration = serializers.IntegerField(read_only=True, default=0)

    def get_tags(self, obj):
        """Get tags as string."""
        return json.dumps([])  # Placeholder

    def get_categories(self, obj):
        """Get categories as string."""
        return obj.category.name if obj.category else None

    def get_brandName(self, obj):
        """Get brand name."""
        if hasattr(obj, 'brand') and obj.brand:
            return obj.brand.name
        return None

    def get_masterImage(self, obj):
        """Get master image URL."""
        if obj.image:
            image_url = obj.image.url
            if image_url.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                image_url = parsed.path
            return image_url
        return None

    def get_thumbnail(self, obj):
        """Get thumbnail URL."""
        return self.get_masterImage(obj)

    def get_masterPrice(self, obj):
        """Get master price as integer."""
        return int(obj.price_per_unit) if obj.price_per_unit else 0

    def get_commentsCount(self, obj):
        """Get comments count."""
        from zistino_apps.notifications.models import Comment
        return Comment.objects.filter(product_id=obj.id, is_accepted=True).count()

    def get_rate(self, obj):
        """Get average rating."""
        from zistino_apps.notifications.models import Comment
        from django.db.models import Avg
        avg_rating = Comment.objects.filter(
            product_id=obj.id,
            is_accepted=True
        ).aggregate(Avg('rate'))['rate__avg']
        return int(avg_rating) if avg_rating else 0

    def get_masterId(self, obj):
        """Get master ID."""
        return str(obj.id)

    def get_createdBy(self, obj):
        """Get created by user ID (placeholder)."""
        return None

    def to_representation(self, instance):
        """Convert to old Swagger format."""
        data = super().to_representation(instance)
        # Ensure UUIDs are strings
        if 'id' in data and data['id']:
            data['id'] = str(data['id'])
        if 'masterId' in data and data['masterId']:
            data['masterId'] = str(data['masterId'])
        if 'brandId' in data and data['brandId']:
            data['brandId'] = str(data['brandId'])
        return data


class ProductSoldOrderItemSerializer(serializers.Serializer):
    """Serializer for order items in sold products response."""
    # Add fields as needed based on old Swagger format
    pass


class ProductSoldOrderSerializer(serializers.Serializer):
    """Serializer for orders in sold products response matching old Swagger format."""
    id = serializers.IntegerField(read_only=True)
    totalPrice = serializers.IntegerField(source='total_price', read_only=True)
    address1 = serializers.CharField(read_only=True, allow_blank=True)
    address2 = serializers.CharField(read_only=True, allow_blank=True)
    phone1 = serializers.CharField(read_only=True, allow_blank=True)
    phone2 = serializers.CharField(read_only=True, allow_blank=True)
    createOrderDate = serializers.SerializerMethodField()
    submitPriceDate = serializers.SerializerMethodField()
    sendToPostDate = serializers.SerializerMethodField()
    postStateNumber = serializers.CharField(source='post_state_number', read_only=True, allow_blank=True)
    paymentTrackingCode = serializers.CharField(source='payment_tracking_code', read_only=True, allow_blank=True)
    status = serializers.SerializerMethodField()
    coupon = serializers.CharField(read_only=True, allow_null=True, default=None)
    userId = serializers.SerializerMethodField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True, allow_null=True)
    addressid = serializers.CharField(read_only=True, allow_null=True, default=None)
    city = serializers.CharField(read_only=True, allow_null=True, default=None)
    country = serializers.CharField(read_only=True, allow_null=True, default=None)
    description = serializers.CharField(read_only=True, allow_null=True, default=None)
    rate = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    storeId = serializers.CharField(read_only=True, allow_null=True, default=None)
    ressellerId = serializers.CharField(read_only=True, allow_null=True, default=None)
    userPhoneNumber = serializers.CharField(source='user_phone_number', read_only=True, allow_null=True, allow_blank=True)
    userFullname = serializers.CharField(source='user_full_name', read_only=True, allow_null=True, allow_blank=True)
    orderItems = serializers.SerializerMethodField()

    def get_id(self, obj):
        """Convert UUID to integer ID (using auto-increment if available, or hash)."""
        # Since Order.id is UUID but old Swagger expects integer,
        # we'll use a simple hash or return the first 8 chars as hex converted to int
        # For now, return a placeholder - in production you might want to add an auto-increment field
        try:
            # Try to get an auto-increment ID if it exists
            return getattr(obj, 'auto_id', hash(str(obj.id)) % 2147483647)
        except:
            return hash(str(obj.id)) % 2147483647

    def get_createOrderDate(self, obj):
        """Format create_order_date in old Swagger format: '2025-10-13T09:30:36.137'."""
        if obj.create_order_date:
            dt_str = obj.create_order_date.isoformat()
            # Remove timezone info and ensure format matches
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return None

    def get_submitPriceDate(self, obj):
        """Format submit_price_date in old Swagger format."""
        if obj.submit_price_date:
            dt_str = obj.submit_price_date.isoformat()
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return None

    def get_sendToPostDate(self, obj):
        """Format send_to_post_date in old Swagger format."""
        if obj.send_to_post_date:
            dt_str = obj.send_to_post_date.isoformat()
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return None

    def get_status(self, obj):
        """Convert status string to integer matching old Swagger format."""
        # Map status strings to integers
        status_map = {
            'pending': 0,
            'confirmed': 1,
            'in_progress': 2,
            'completed': 3,
            'cancelled': 4,
        }
        return status_map.get(obj.status, 0)

    def get_userId(self, obj):
        """Get user ID as string."""
        return str(obj.user.id) if obj.user else None

    def get_orderItems(self, obj):
        """Get order items array."""
        # Return empty array for now, or implement OrderItem serializer if needed
        return []


class ProductSearchWithTagsRequestSerializer(serializers.Serializer):
    """Search request with tags matching old Swagger format."""
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0)
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Order by options for client search'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    brands = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    categoryId = serializers.IntegerField(required=False, allow_null=True)
    categoryType = serializers.IntegerField(required=False, allow_null=True)
    productType = serializers.IntegerField(required=False, allow_null=True)
    minPrice = serializers.IntegerField(required=False, allow_null=True)
    maxPrice = serializers.IntegerField(required=False, allow_null=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='List of tags to search for'
    )


class ProductByNameResponseSerializer(serializers.Serializer):
    """Response serializer for by-name endpoint matching old Swagger format."""
    title = serializers.CharField(read_only=True, help_text='Product name')
    value = serializers.UUIDField(read_only=True, help_text='Product UUID')


class ProductByTagNameRequestSerializer(serializers.Serializer):
    """Request serializer for searching by tag name matching old Swagger format."""
    pageNumber = serializers.IntegerField(required=False, default=0, min_value=0)
    pageSize = serializers.IntegerField(required=False, default=0, min_value=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Order by options'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    brandId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    categoryId = serializers.IntegerField(required=False, allow_null=True)
    categoryType = serializers.IntegerField(required=False, allow_null=True)
    productType = serializers.IntegerField(required=False, allow_null=True)
    minPrice = serializers.IntegerField(required=False, allow_null=True)
    maxPrice = serializers.IntegerField(required=False, allow_null=True)
