from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from zistino_apps.products.models import Product
import uuid

User = get_user_model()


class Notification(models.Model):
    """Notification model for push notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('order', 'Order'),
        ('delivery', 'Delivery'),
        ('payment', 'Payment'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    data = models.JSONField(blank=True, null=True)  # Additional data for the notification
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"Notification {self.id} - {self.title}"


class Comment(models.Model):
    """Product comments with optional threading - maps CommentModel/CommentsItemsModel."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    rate = models.IntegerField(default=0)
    text = models.TextField(blank=True)
    is_accepted = models.BooleanField(default=False)
    user_full_name = models.CharField(max_length=255, blank=True)
    user_image_url = models.URLField(blank=True)
    product_image = models.URLField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment {self.id} on {self.product_id}"
