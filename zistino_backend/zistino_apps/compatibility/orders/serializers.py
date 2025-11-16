"""
Serializers for Orders endpoints.
These import from orders app serializers and add compatibility request/response serializers.
"""
from zistino_apps.orders.serializers import OrderSerializer, OrderItemSerializer, BasketSerializer, BasketItemSerializer
from zistino_apps.orders.models import Order, OrderItem
from zistino_apps.products.models import Product
from zistino_apps.compatibility.products.serializers import ProductCompatibilitySerializer
from rest_framework import serializers
import hashlib


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields serializer."""
    fields = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Search keyword')
    groupBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Group by fields'
    )


class OrderSearchRequestSerializer(serializers.Serializer):
    """Request serializer for order search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by options'
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID or string)')
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Order status (0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled)')
    categoryId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Category ID (UUID or integer string)')
    ressellerId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Reseller ID (UUID or string)')
    isOrder = serializers.BooleanField(required=False, allow_null=True, default=True, help_text='Is order flag')
    remainday = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Remaining days')
    productType = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Product type')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID or string)')


class OrderSearchUserRequestSerializer(serializers.Serializer):
    """Request serializer for searching orders by user matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by options'
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID or string)')
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Order status (0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled)')
    categoryId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Category ID (UUID or integer string)')
    ressellerId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Reseller ID (UUID or string)')
    isOrder = serializers.BooleanField(required=False, allow_null=True, default=True, help_text='Is order flag')
    remainday = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Remaining days')
    productType = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Product type')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID or string)')


class OrderCheckInStockRequestSerializer(serializers.Serializer):
    """Request serializer for checking products in stock."""
    productIds = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text='List of product IDs to check'
    )


class OrderHandyOrderRequestSerializer(serializers.Serializer):
    """Request serializer for handy order creation."""
    # Define fields based on what's needed for handy order
    # This is a placeholder - adjust based on actual requirements
    pass


class OrderByDateRequestSerializer(serializers.Serializer):
    """Request serializer for getting orders by date."""
    startDate = serializers.DateTimeField(required=False)
    endDate = serializers.DateTimeField(required=False)
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)


class OrderStatusUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for updating order status."""
    status = serializers.ChoiceField(
        choices=['pending', 'confirmed', 'in_progress', 'completed', 'cancelled'],
        required=True
    )


class OrderItemStatusUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for updating order item status."""
    status = serializers.CharField(required=True)


class OrderSearchStaticsRequestSerializer(serializers.Serializer):
    """Request serializer for order statistics search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True)
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by options'
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID or string)')
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Order status (0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled)')
    categoryId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Category ID (UUID or integer string)')
    ressellerId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Reseller ID (UUID or string)')
    isOrder = serializers.BooleanField(required=False, allow_null=True, default=True, help_text='Is order flag')
    remainday = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Remaining days')
    productType = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Product type')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID or string)')


class OrderAdminGetByUserIdRequestSerializer(serializers.Serializer):
    """Request serializer for admin to get orders by user ID."""
    userId = serializers.CharField(required=True)
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        help_text='Order by options'
    )
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Order status (0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled)')


class OrderMappingRequestSerializer(serializers.Serializer):
    """Request serializer for order mapping matching old Swagger format."""
    orderId = serializers.CharField(required=True, help_text='Order ID (UUID or integer)')
    orderPersonId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Order person ID (UUID or string)')
    basketId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Basket ID (UUID or integer)')
    basketUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Basket user ID (UUID or string)')
    procced = serializers.IntegerField(required=False, default=0, help_text='Process flag (0 or 1)')


class OrderItemCreateRequestSerializer(serializers.Serializer):
    """Request serializer for order item creation matching old Swagger format."""
    productId = serializers.UUIDField(required=True, help_text='Product UUID')
    unitPrice = serializers.IntegerField(required=False, default=0, help_text='Unit price in Rials')
    unitDiscountPrice = serializers.IntegerField(required=False, default=0, help_text='Unit discount price in Rials')
    itemCount = serializers.IntegerField(required=False, default=1, min_value=1, help_text='Item quantity')
    status = serializers.IntegerField(required=False, default=0, help_text='Item status (0 = pending)')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Item description')


class OrderCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating order matching old Swagger format."""
    totalPrice = serializers.IntegerField(required=True, min_value=0, help_text='Total order price in Rials')
    address1 = serializers.CharField(required=True, help_text='Primary address')
    address2 = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Secondary address')
    phone1 = serializers.CharField(required=True, help_text='Primary phone number')
    phone2 = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Secondary phone number')
    createOrderDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Order creation date')
    submitPriceDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Price submission date')
    sendToPostDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Send to post date')
    postStateNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Post state tracking number')
    paymentTrackingCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Payment tracking code')
    status = serializers.IntegerField(required=False, default=0, help_text='Order status (0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled)')
    couponId = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Coupon ID (0 if no coupon)')
    couponKey = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Coupon key/code')
    userId = serializers.UUIDField(required=True, help_text='User UUID')
    userFullname = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User full name')
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True, help_text='Delivery latitude')
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True, help_text='Delivery longitude')
    addressid = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Address ID from addresses table (0 if not using saved address)')
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='City name')
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Country name')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Order description/notes')
    rate = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Order rating (0-5)')
    storeId = serializers.IntegerField(required=False, default=0, allow_null=True, help_text='Store ID (0 if not applicable)')
    ressellerId = serializers.UUIDField(required=False, allow_null=True, help_text='Reseller ID (UUID, nullable - use null if no reseller)')
    orderItems = serializers.ListField(
        child=OrderItemCreateRequestSerializer(),
        required=True,
        min_length=1,
        help_text='List of order items (at least one item required)'
    )


class OrderItemCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for OrderItem that matches old Swagger output format."""
    id = serializers.SerializerMethodField()
    productId = serializers.SerializerMethodField()
    productName = serializers.CharField(source='product_name', read_only=True)
    productImage = serializers.SerializerMethodField()
    productDetails = serializers.SerializerMethodField()
    unitPrice = serializers.IntegerField(source='unit_price', read_only=True)
    unitDiscountPrice = serializers.IntegerField(read_only=True, default=0)
    itemCount = serializers.IntegerField(source='quantity', read_only=True)
    status = serializers.IntegerField(read_only=True, default=0)
    description = serializers.CharField(read_only=True, allow_blank=True, default='')
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True, allow_null=True, default=None)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True, allow_null=True, default=None)
    addressid = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    city = serializers.CharField(read_only=True, allow_null=True, default=None)
    country = serializers.CharField(read_only=True, allow_null=True, default=None)
    rate = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    storeId = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    ressellerId = serializers.CharField(read_only=True, allow_null=True, default=None)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'productId', 'productName', 'productImage', 'productDetails', 'unitPrice', 'unitDiscountPrice',
            'itemCount', 'status', 'description', 'latitude', 'longitude', 'addressid',
            'city', 'country', 'rate', 'storeId', 'ressellerId'
        ]

    def get_id(self, obj):
        """Convert UUID to integer ID using deterministic hash."""
        uuid_str = str(obj.id)
        hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % 2147483647  # Max 32-bit integer

    def get_productId(self, obj):
        """Get product ID by matching product_name with Product model."""
        # Try to find product by name
        try:
            product = Product.objects.get(name=obj.product_name)
            return str(product.id)
        except (Product.DoesNotExist, Product.MultipleObjectsReturned):
            # If not found or multiple matches, return None
            return None

    def get_productImage(self, obj):
        """Get product image URL if available."""
        # Try to find product by name and get image
        try:
            product = Product.objects.get(name=obj.product_name)
            if product.image:
                request = self.context.get('request')
                if request:
                    image_url = product.image.url
                    # If it's already a full URL, extract the path
                    if image_url.startswith('http'):
                        from urllib.parse import urlparse
                        parsed = urlparse(image_url)
                        image_url = parsed.path
                    return image_url
        except (Product.DoesNotExist, Product.MultipleObjectsReturned):
            pass
        return None

    def get_productDetails(self, obj):
        """Get full product details using ProductCompatibilitySerializer."""
        # Try to find product by name
        try:
            product = Product.objects.get(name=obj.product_name)
            # Use ProductCompatibilitySerializer to get full product details
            serializer = ProductCompatibilitySerializer(product, context=self.context)
            return serializer.data
        except (Product.DoesNotExist, Product.MultipleObjectsReturned):
            # If product not found, return None
            return None


class OrderAllSerializer(serializers.Serializer):
    """Simplified serializer for GET /api/v1/orders/all matching old Swagger format (no orderItems)."""
    
    def get_phone1(self, obj):
        """Get phone1 from order or user."""
        # Order model has phone1 field
        if hasattr(obj, 'phone1') and obj.phone1:
            return obj.phone1
        # Fallback to user phone number
        if obj.user and hasattr(obj.user, 'phone_number'):
            return obj.user.phone_number
        return None
    
    def get_userFullname(self, obj):
        """Get user full name."""
        # Order model has user_full_name field
        if hasattr(obj, 'user_full_name') and obj.user_full_name:
            return obj.user_full_name
        # Fallback to user's name
        if obj.user:
            if hasattr(obj.user, 'full_name') and obj.user.full_name:
                return obj.user.full_name
            if hasattr(obj.user, 'first_name') or hasattr(obj.user, 'last_name'):
                first = getattr(obj.user, 'first_name', '') or ''
                last = getattr(obj.user, 'last_name', '') or ''
                return f"{first} {last}".strip() or ' '
        return ' '
    
    def get_latitude(self, obj):
        """Get latitude as number."""
        if hasattr(obj, 'latitude') and obj.latitude is not None:
            try:
                return float(obj.latitude)
            except (ValueError, TypeError):
                return None
        return None
    
    def get_longitude(self, obj):
        """Get longitude as number."""
        if hasattr(obj, 'longitude') and obj.longitude is not None:
            try:
                return float(obj.longitude)
            except (ValueError, TypeError):
                return None
        return None
    
    def get_addressid(self, obj):
        """Get address ID - Order model doesn't have address field, return None."""
        # Order model doesn't have an address ForeignKey
        # Return None as per old Swagger format
        return None
    
    def get_storeId(self, obj):
        """Get store ID - Order model doesn't have store_id field."""
        # Order model doesn't have store_id field
        return None
    
    def get_ressellerId(self, obj):
        """Get reseller ID - Order model doesn't have resseller_id field."""
        # Order model doesn't have resseller_id field
        return None
    
    def get_city(self, obj):
        """Get city - Order model doesn't have city field."""
        # Order model doesn't have city field
        return None
    
    def get_country(self, obj):
        """Get country - Order model doesn't have country field."""
        # Order model doesn't have country field
        return None
    
    def get_description(self, obj):
        """Get description - Order model doesn't have description field."""
        # Order model doesn't have description field
        return None
    
    def get_rate(self, obj):
        """Get rate - Order model doesn't have rate field."""
        # Order model doesn't have rate field
        return None
    
    def to_representation(self, instance):
        """Convert to representation matching old Swagger format."""
        # Convert UUID to integer ID
        import hashlib
        order_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
        
        # Format createOrderDate - use create_order_date or created_at
        create_order_date = getattr(instance, 'create_order_date', None) or getattr(instance, 'created_at', None)
        if create_order_date:
            # Format as "2025-11-10T10:51:40.943" (without timezone)
            if hasattr(create_order_date, 'strftime'):
                create_order_date_str = create_order_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            else:
                create_order_date_str = str(create_order_date)
        else:
            create_order_date_str = None
        
        # Get status - convert string to integer if needed
        status_value = getattr(instance, 'status', 'pending')
        if isinstance(status_value, str):
            status_map = {
                'pending': 0,
                'confirmed': 1,
                'in_progress': 2,
                'completed': 3,
                'cancelled': 4,
            }
            status_value = status_map.get(status_value, 0)
        else:
            status_value = int(status_value) if status_value is not None else 0
        
        return {
            'id': order_id_hash,
            'totalPrice': float(instance.total_price) if instance.total_price else 0,
            'createOrderDate': create_order_date_str,
            'paymentTrackingCode': getattr(instance, 'payment_tracking_code', None) or '-',
            'status': status_value,
            'userId': str(instance.user.id) if instance.user else None,
            'phone1': self.get_phone1(instance) or None,
            'userFullname': self.get_userFullname(instance),
            'latitude': self.get_latitude(instance),
            'longitude': self.get_longitude(instance),
            'addressid': self.get_addressid(instance),
            'city': self.get_city(instance),
            'country': self.get_country(instance),
            'description': self.get_description(instance),
            'rate': self.get_rate(instance),
            'storeId': self.get_storeId(instance),
            'ressellerId': self.get_ressellerId(instance)
        }


class OrderCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for Order that matches old Swagger output format."""
    id = serializers.SerializerMethodField()
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
    addressid = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    city = serializers.CharField(read_only=True, allow_null=True, default=None)
    country = serializers.CharField(read_only=True, allow_null=True, default=None)
    description = serializers.CharField(read_only=True, allow_null=True, default=None)
    rate = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    storeId = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    ressellerId = serializers.CharField(read_only=True, allow_null=True, default=None)
    userPhoneNumber = serializers.CharField(source='user_phone_number', read_only=True, allow_null=True, allow_blank=True)
    userFullname = serializers.CharField(source='user_full_name', read_only=True, allow_blank=True)
    orderItems = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'totalPrice', 'address1', 'address2', 'phone1', 'phone2',
            'createOrderDate', 'submitPriceDate', 'sendToPostDate', 'postStateNumber',
            'paymentTrackingCode', 'status', 'coupon', 'userId', 'latitude', 'longitude',
            'addressid', 'city', 'country', 'description', 'rate', 'storeId', 'ressellerId',
            'userPhoneNumber', 'userFullname', 'orderItems'
        ]

    def get_id(self, obj):
        """Convert UUID to integer ID using deterministic hash."""
        # Use MD5 hash for deterministic results (same UUID always maps to same integer)
        uuid_str = str(obj.id)
        hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % 2147483647  # Max 32-bit integer

    def get_createOrderDate(self, obj):
        """Format create_order_date in old Swagger format: '2024-03-13T08:22:26.523'."""
        if obj.create_order_date:
            dt_str = obj.create_order_date.isoformat()
            # Remove timezone info
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
        status_map = {
            'pending': 0,
            'confirmed': 1,
            'in_progress': 2,
            'completed': 3,
            'cancelled': 4,
        }
        return status_map.get(obj.status, 0)

    def get_userId(self, obj):
        """Return user ID as UUID string."""
        return str(obj.user.id) if obj.user else None

    def get_orderItems(self, obj):
        """Get order items as array matching old Swagger format."""
        order_items = obj.order_items.all()
        serializer = OrderItemCompatibilitySerializer(order_items, many=True, context=self.context)
        return serializer.data

    def to_representation(self, instance):
        """Convert to old Swagger format."""
        data = super().to_representation(instance)
        
        # Ensure userId is a string (UUID)
        if 'userId' in data and data['userId']:
            data['userId'] = str(data['userId'])
        
        # Ensure ressellerId is a string or null
        if 'ressellerId' in data and data['ressellerId']:
            data['ressellerId'] = str(data['ressellerId'])
        
        return data

