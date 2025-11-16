from rest_framework import serializers
from .models import Order, OrderItem, Basket, BasketItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'weight', 'unit_price', 'total_price', 'created_at']
        read_only_fields = ['id', 'total_price', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'total_price', 'status', 'external_user_id', 'address1', 'address2',
            'phone1', 'phone2', 'create_order_date', 'submit_price_date',
            'send_to_post_date', 'post_state_number', 'payment_tracking_code',
            'user_full_name', 'user_phone_number', 'created_at', 'updated_at', 'order_items'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = [
            'id', 'basket', 'product_id', 'name', 'description', 'master_image',
            'discount_percent', 'quantity', 'price', 'item_total', 'created_at'
        ]
        read_only_fields = ['id', 'basket', 'created_at']


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = [
            'id', 'user', 'is_empty', 'total_items', 'total_unique_items', 'cart_total',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
