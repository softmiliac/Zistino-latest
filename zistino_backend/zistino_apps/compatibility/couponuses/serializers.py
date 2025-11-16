"""
Serializers for CouponUses endpoints.
CouponUses are represented by BasketDiscount model.
"""
from rest_framework import serializers
from zistino_apps.payments.models import BasketDiscount, Coupon
from zistino_apps.orders.models import Basket


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for coupon use search."""
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


class CouponUseSearchRequestSerializer(serializers.Serializer):
    """Request serializer for coupon use search matching old Swagger format."""
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


class CouponUseCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating coupon use matching old Swagger format."""
    couponId = serializers.IntegerField(required=True, help_text='Coupon ID')
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID as string)')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (not used, for compatibility only)')
    orderId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Order ID (not used, for compatibility only)')


class CouponUseSerializer(serializers.ModelSerializer):
    """Serializer for CouponUse (BasketDiscount)."""
    couponId = serializers.IntegerField(source='coupon.id', read_only=True)
    couponKey = serializers.CharField(source='coupon.key', read_only=True)
    couponAmount = serializers.IntegerField(source='coupon.amount', read_only=True)
    userId = serializers.UUIDField(source='basket.user.id', read_only=True, allow_null=True)
    userPhone = serializers.CharField(source='basket.user.phone_number', read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    # For create/update - define with proper queryset
    coupon = serializers.PrimaryKeyRelatedField(queryset=Coupon.objects.all(), required=False)
    basket = serializers.PrimaryKeyRelatedField(queryset=Basket.objects.all(), required=False)

    class Meta:
        model = BasketDiscount
        fields = [
            'id', 'couponId', 'couponKey', 'couponAmount',
            'userId', 'userPhone', 'amount', 'createdAt',
            'coupon', 'basket'  # For create/update
        ]
        read_only_fields = ['id', 'createdAt', 'couponId', 'couponKey', 'couponAmount', 'userId', 'userPhone']


class CouponUseDetailSerializer(serializers.Serializer):
    """Compatibility serializer for CouponUse full details matching old Swagger format."""
    id = serializers.IntegerField(read_only=True)
    couponId = serializers.IntegerField(source='coupon.id', read_only=True)
    couponKey = serializers.CharField(source='coupon.key', read_only=True)
    userId = serializers.SerializerMethodField()
    userFullname = serializers.SerializerMethodField()
    userEmail = serializers.SerializerMethodField()
    userPhoneNumber = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    
    def get_userId(self, obj):
        """Return user ID as UUID string."""
        if obj.basket and obj.basket.user:
            return str(obj.basket.user.id)
        return None
    
    def get_userFullname(self, obj):
        """Return user full name."""
        if obj.basket and obj.basket.user:
            name_parts = [obj.basket.user.first_name, obj.basket.user.last_name]
            return ' '.join(filter(None, name_parts)) or obj.basket.user.username or ''
        return ' '
    
    def get_userEmail(self, obj):
        """Return user email."""
        if obj.basket and obj.basket.user:
            return obj.basket.user.email
        return None
    
    def get_userPhoneNumber(self, obj):
        """Return user phone number."""
        if obj.basket and obj.basket.user:
            return obj.basket.user.phone_number or ''
        return ''
    
    def get_order(self, obj):
        """Get order associated with this basket (if exists)."""
        if not obj.basket or not obj.basket.user:
            return None
        
        # Try to find an order for this user that was created around the same time as the coupon use
        # or find the most recent order for this user
        from zistino_apps.orders.models import Order
        from datetime import timedelta
        
        # Look for orders created within 1 hour of coupon use
        time_window_start = obj.created_at - timedelta(hours=1)
        time_window_end = obj.created_at + timedelta(hours=1)
        
        # Try to find order by user and time window
        orders = Order.objects.filter(
            user=obj.basket.user,
            created_at__gte=time_window_start,
            created_at__lte=time_window_end
        ).prefetch_related('order_items').order_by('-created_at')
        
        if orders.exists():
            order = orders.first()
            # Use OrderCompatibilitySerializer to format the order
            from zistino_apps.compatibility.orders.serializers import OrderCompatibilitySerializer
            serializer = OrderCompatibilitySerializer(order, context=self.context)
            return serializer.data
        
        # If no order found in time window, try to get the most recent order for this user
        recent_order = Order.objects.filter(
            user=obj.basket.user
        ).prefetch_related('order_items').order_by('-created_at').first()
        
        if recent_order:
            from zistino_apps.compatibility.orders.serializers import OrderCompatibilitySerializer
            serializer = OrderCompatibilitySerializer(recent_order, context=self.context)
            return serializer.data
        
        return None

