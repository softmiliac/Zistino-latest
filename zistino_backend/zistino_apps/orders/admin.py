from django.contrib import admin
from .models import Order, OrderItem, Basket, BasketItem


class OrderItemInline(admin.TabularInline):
    """Inline for OrderItems in Order admin"""
    model = OrderItem
    extra = 1  # Show 1 empty row by default
    readonly_fields = ('id', 'total_price', 'created_at')
    fields = ('product_name', 'quantity', 'unit_price', 'total_price', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders"""
    list_display = ('id', 'user', 'total_price', 'status', 'create_order_date', 'user_full_name', 'created_at')
    list_filter = ('status', 'create_order_date', 'created_at')
    search_fields = ('id', 'user__phone_number', 'user__username', 'user_full_name', 
                     'user_phone_number', 'payment_tracking_code', 'post_state_number')
    readonly_fields = ('id', 'create_order_date', 'created_at', 'updated_at')
    autocomplete_fields = ('user',)  # Better UI - shows searchable dropdown
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    def save_formset(self, request, form, formset, change):
        """Auto-calculate total_price for OrderItems"""
        instances = formset.save(commit=False)
        for instance in instances:
            # Auto-calculate total_price = quantity × unit_price
            instance.total_price = instance.quantity * instance.unit_price
            instance.save()
        formset.save_m2m()
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'total_price', 'status', 'external_user_id')
        }),
        ('Delivery Address', {
            'fields': ('address1', 'address2', 'phone1', 'phone2', 'latitude', 'longitude')
        }),
        ('User Details', {
            'fields': ('user_full_name', 'user_phone_number')
        }),
        ('Waste Delivery Request', {
            'fields': ('estimated_weight_range', 'preferred_delivery_date'),
            'description': 'Weight range selected by customer and preferred delivery date/time'
        }),
        ('Status Dates', {
            'fields': ('create_order_date', 'submit_price_date', 'send_to_post_date')
        }),
        ('Tracking', {
            'fields': ('post_state_number', 'payment_tracking_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for order items"""
    list_display = ('product_name', 'order', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product_name', 'order__id', 'order__user__phone_number')
    readonly_fields = ('id', 'total_price', 'created_at')
    raw_id_fields = ('order',)
    ordering = ('-created_at',)


class BasketItemInline(admin.TabularInline):
    """Inline for BasketItems in Basket admin"""
    model = BasketItem
    extra = 1
    readonly_fields = ('id', 'item_total', 'created_at')
    fields = ('product_id', 'name', 'quantity', 'price', 'discount_percent', 'item_total', 'master_image')


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """Admin for shopping baskets"""
    list_display = ('id', 'user', 'is_empty', 'total_items', 'total_unique_items', 'cart_total', 'created_at')
    list_filter = ('is_empty', 'created_at')
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('user',)  # Better UI - shows searchable dropdown
    ordering = ('-created_at',)
    inlines = [BasketItemInline]
    
    fieldsets = (
        ('Basket Information', {
            'fields': ('user', 'is_empty', 'total_items', 'total_unique_items', 'cart_total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    """Admin for basket items"""
    list_display = ('name', 'basket', 'quantity', 'price', 'discount_percent', 'item_total', 'created_at')
    list_filter = ('created_at', 'discount_percent')
    search_fields = ('name', 'product_id', 'basket__user__phone_number')
    readonly_fields = ('id', 'item_total', 'created_at')
    autocomplete_fields = ('basket',)  # Better UI - shows meaningful basket name with search
    ordering = ('-created_at',)

