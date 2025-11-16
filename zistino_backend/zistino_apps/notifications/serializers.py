from rest_framework import serializers
from .models import Notification, Comment


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'is_read', 'data', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'product', 'parent', 'rate', 'text', 'is_accepted',
            'user_full_name', 'user_image_url', 'product_image', 'created_on'
        ]
        read_only_fields = ['id', 'user', 'created_on']
