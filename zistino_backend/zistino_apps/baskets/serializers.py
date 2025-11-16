from rest_framework import serializers
from zistino_apps.orders.models import Basket, BasketItem


class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = [
            "id",
            "product_id",
            "name",
            "description",
            "master_image",
            "discount_percent",
            "quantity",
            "price",
            "item_total",
            "created_at",
        ]
        read_only_fields = ["id", "item_total", "created_at"]


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = [
            "id",
            "is_empty",
            "total_items",
            "total_unique_items",
            "cart_total",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ApplyCouponRequestSerializer(serializers.Serializer):
    """Request schema for applying/removing coupon on basket."""
    code = serializers.CharField(required=False, allow_blank=True)
    key = serializers.CharField(required=False, allow_blank=True)


