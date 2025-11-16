"""
Serializers for Baskets compatibility layer.
"""
from rest_framework import serializers
from zistino_apps.orders.models import Basket, BasketItem
import json


class BasketCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating basket matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Basket ID (ignored, always 0 for new baskets)')
    userId = serializers.UUIDField(required=True, help_text='User UUID')
    items = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Items as JSON string (optional)')
    isEmpty = serializers.BooleanField(required=False, default=True, help_text='Is basket empty')
    totalItems = serializers.IntegerField(required=False, default=0, help_text='Total items count')
    totalUniqueItems = serializers.IntegerField(required=False, default=0, help_text='Total unique items count')
    cartTotal = serializers.IntegerField(required=False, default=0, help_text='Cart total price')


class BasketClientRequestSerializer(serializers.Serializer):
    """Request serializer for client basket POST endpoint matching old Swagger format."""
    items = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Items as JSON string (optional)')
    isEmpty = serializers.BooleanField(required=False, default=True, help_text='Is basket empty')
    totalItems = serializers.IntegerField(required=False, default=0, help_text='Total items count')
    totalUniqueItems = serializers.IntegerField(required=False, default=0, help_text='Total unique items count')
    cartTotal = serializers.IntegerField(required=False, default=0, help_text='Cart total price')


class BasketCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for Basket that matches old Swagger output format."""
    userId = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField(help_text='Items as JSON string')
    isEmpty = serializers.BooleanField(source='is_empty', read_only=True)
    totalItems = serializers.IntegerField(source='total_items', read_only=True)
    totalUniqueItems = serializers.IntegerField(source='total_unique_items', read_only=True)
    cartTotal = serializers.IntegerField(source='cart_total', read_only=True)

    class Meta:
        model = Basket
        fields = ['id', 'userId', 'items', 'isEmpty', 'totalItems', 'totalUniqueItems', 'cartTotal']
        read_only_fields = ['id']

    def get_userId(self, obj):
        """Return user ID as UUID string."""
        return str(obj.user.id) if obj.user else None

    def get_items(self, obj):
        """Return items as JSON string matching old Swagger format."""
        items = obj.items.all()
        if items:
            items_data = []
            for item in items:
                items_data.append({
                    'id': str(item.id),
                    'product_id': item.product_id,
                    'name': item.name,
                    'description': item.description,
                    'master_image': item.master_image,
                    'discount_percent': item.discount_percent,
                    'quantity': item.quantity,
                    'price': item.price,
                    'item_total': item.item_total
                })
            return json.dumps(items_data)
        return "string"  # Old Swagger shows "string" when empty
    
    def to_representation(self, instance):
        """Override to ensure items is always a string in the response."""
        data = super().to_representation(instance)
        # Ensure items is always a string (not parsed as JSON)
        if 'items' in data:
            # items is already a string from get_items, but ensure it's not None
            if data['items'] is None:
                data['items'] = "string"
        return data

