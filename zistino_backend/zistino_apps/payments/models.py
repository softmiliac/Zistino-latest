from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Wallet(models.Model):
    """User wallet model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return f"Wallet {self.user.phone_number} - {self.balance}"


class Transaction(models.Model):
    """Transaction model for wallet operations"""
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"Transaction {self.id} - {self.amount} {self.transaction_type}"


class Coupon(models.Model):
    """Coupon/discount codes - matches CouponsModel (status, key, amount)."""
    STATUS_CHOICES = (
        (0, 'inactive'),
        (1, 'active'),
        (2, 'expired'),
        (3, 'used'),
    )

    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    usage_limit = models.IntegerField(blank=True, null=True)
    used_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return f"{self.key} ({self.amount})"


class BasketDiscount(models.Model):
    """Applied coupon discount for a basket without changing basket schema."""
    id = models.AutoField(primary_key=True)
    basket = models.OneToOneField('orders.Basket', on_delete=models.CASCADE, related_name='discount')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='basket_discounts')
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'basket_discounts'
        verbose_name = 'Basket Discount'
        verbose_name_plural = 'Basket Discounts'


class DepositRequest(models.Model):
    """Deposit request model for customers to request wallet deposits."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposit_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Amount to deposit in Rials')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_id = models.CharField(max_length=100, blank=True, help_text='Bank receipt or reference number (optional)')
    description = models.TextField(blank=True, help_text='Additional notes or description')
    verified_at = models.DateTimeField(blank=True, null=True, help_text='When admin verified the deposit')
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_deposits',
        help_text='Admin user who verified this deposit'
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deposit_request',
        help_text='Transaction created when deposit is approved'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deposit_requests'
        verbose_name = 'Deposit Request'
        verbose_name_plural = 'Deposit Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Deposit Request {self.id} - {self.user.phone_number} - {self.amount} Rials - {self.status}"