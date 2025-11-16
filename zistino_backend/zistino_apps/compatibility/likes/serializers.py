"""
Serializers for Likes endpoints.
"""
from rest_framework import serializers
from .models import Like
import uuid


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like."""
    itemId = serializers.UUIDField(source='item_id', read_only=True)
    itemType = serializers.CharField(source='item_type', read_only=True)
    userId = serializers.UUIDField(source='user.id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'itemId', 'itemType', 'userId', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class LikeCreateSerializer(serializers.Serializer):
    """Request serializer for creating a like matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Like ID (not used, for compatibility only)')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID as string)')
    itemId = serializers.IntegerField(required=False, default=0, help_text='Item ID (not used, for compatibility only)')
    type = serializers.IntegerField(required=False, default=0, help_text='Type: 0=product, 1=item, 2=blog, 3=comment')
    
    def validate(self, data):
        """Validate that either productId is provided."""
        product_id = data.get('productId')
        if not product_id or product_id == 'string' or product_id.strip() == '':
            raise serializers.ValidationError({'productId': 'productId is required and must be a valid UUID.'})
        
        # Validate UUID format
        try:
            uuid.UUID(product_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError({'productId': 'productId must be a valid UUID.'})
        
        return data
    
    def get_item_type(self):
        """Map integer type to string item_type."""
        type_mapping = {
            0: 'product',
            1: 'item',
            2: 'blog',
            3: 'comment'
        }
        type_value = self.validated_data.get('type', 0)
        return type_mapping.get(type_value, 'product')


class LikeStatusSerializer(serializers.Serializer):
    """Serializer for like status response."""
    isLiked = serializers.BooleanField()
    likeCount = serializers.IntegerField()
    itemId = serializers.UUIDField()
    itemType = serializers.CharField()

