from django.contrib import admin
from .models import Wallet, Transaction, Coupon, BasketDiscount, DepositRequest


class TransactionInline(admin.TabularInline):
    """Inline for Transactions in Wallet admin"""
    model = Transaction
    extra = 0
    readonly_fields = ('id', 'created_at')
    fields = ('amount', 'transaction_type', 'status', 'description', 'reference_id', 'created_at')
    can_delete = False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin for user wallets"""
    list_display = ('user', 'balance', 'transaction_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__phone_number', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('user',)  # Search by phone/username/email
    ordering = ('-created_at',)
    inlines = [TransactionInline]
    
    fieldsets = (
        ('Wallet Information', {
            'fields': ('user', 'balance')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def transaction_count(self, obj):
        return obj.transactions.count()
    transaction_count.short_description = 'Transactions'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for wallet transactions"""
    list_display = ('id', 'wallet', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('wallet__user__phone_number', 'wallet__user__username', 
                     'reference_id', 'description')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('wallet',)  # Search by wallet (shows user's phone)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('wallet', 'amount', 'transaction_type', 'status')
        }),
        ('Details', {
            'fields': ('description', 'reference_id')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin for discount coupons"""
    list_display = ('key', 'amount', 'status', 'valid_from', 'valid_to', 'usage_limit', 'used_count', 'created_at')
    list_filter = ('status', 'valid_from', 'valid_to', 'created_at')
    search_fields = ('key',)
    readonly_fields = ('id', 'created_at', 'used_count')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('key', 'amount', 'status')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'usage_limit', 'used_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(BasketDiscount)
class BasketDiscountAdmin(admin.ModelAdmin):
    list_display = ('basket', 'coupon', 'amount', 'created_at')
    search_fields = ('basket__id', 'coupon__key')
    readonly_fields = ('id', 'created_at')


@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    """Admin for deposit requests"""
    list_display = ('id', 'user', 'amount', 'status', 'verified_by', 'verified_at', 'created_at')
    list_filter = ('status', 'created_at', 'verified_at')
    search_fields = ('user__phone_number', 'user__username', 'reference_id', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'verified_at')
    autocomplete_fields = ('user', 'verified_by')
    
    fieldsets = (
        ('Deposit Request Information', {
            'fields': ('id', 'user', 'amount', 'status')
        }),
        ('Details', {
            'fields': ('reference_id', 'description')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at', 'transaction')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make status readonly if already processed."""
        if obj and obj.status != 'pending':
            return self.readonly_fields + ('status',)
        return self.readonly_fields

