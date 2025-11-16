from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Order(models.Model):
    """Order model for recycling requests - matches Flutter OrderModel exactly"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        help_text='Order status: pending, confirmed, in_progress, completed, or cancelled'
    )
    external_user_id = models.CharField(max_length=255, blank=True)
    address1 = models.TextField(blank=True)
    address2 = models.TextField(blank=True)
    phone1 = models.CharField(max_length=15, blank=True)
    phone2 = models.CharField(max_length=15, blank=True)
    create_order_date = models.DateTimeField(auto_now_add=True)
    submit_price_date = models.DateTimeField(blank=True, null=True)
    send_to_post_date = models.DateTimeField(blank=True, null=True)
    post_state_number = models.CharField(max_length=100, blank=True)
    payment_tracking_code = models.CharField(max_length=100, blank=True)
    user_full_name = models.CharField(max_length=255, blank=True)
    user_phone_number = models.CharField(max_length=15, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text='Customer location latitude')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text='Customer location longitude')
    estimated_weight_range = models.CharField(max_length=20, blank=True, null=True, help_text='Estimated weight range selected by customer (e.g., "2-5", "5-10", "10-20" in kg)')
    preferred_delivery_date = models.DateTimeField(blank=True, null=True, help_text='Preferred delivery date and time selected by customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.id} - {self.user.phone_number}"


class OrderItem(models.Model):
    """Order item model for individual products in an order - matches Flutter OrderItemModel"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, help_text='Weight in kg for waste/recyclable items')
    unit_price = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.product_name} x {self.quantity} - {self.order.id}"


class Basket(models.Model):
    """Shopping cart prior to order creation - matches BasketModel."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    is_empty = models.BooleanField(default=True)
    total_items = models.IntegerField(default=0)
    total_unique_items = models.IntegerField(default=0)
    cart_total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'baskets'
        verbose_name = 'Basket'
        verbose_name_plural = 'Baskets'

    def __str__(self):
        """Return meaningful basket representation"""
        user_info = self.user.phone_number if self.user else "No User"
        return f"Basket #{self.id} - {user_info} ({self.total_items} items, {self.cart_total:,} total)"


class BasketItem(models.Model):
    """Items inside a basket - matches BasketItemModel fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    master_image = models.URLField(blank=True)
    discount_percent = models.IntegerField(default=0)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    item_total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'basket_items'
        verbose_name = 'Basket Item'
        verbose_name_plural = 'Basket Items'