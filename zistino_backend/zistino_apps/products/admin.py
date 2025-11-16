from django.contrib import admin
from .models import Category, Product, Color, ProductColor, Price, Specification, Warranty, ProductSection, FAQ, Problem, ProductCode, Bookmark, Brand, Like


# Inline classes (must be defined before ProductAdmin)
class ProductColorInline(admin.TabularInline):
    """Inline for ProductColor in Product admin"""
    model = ProductColor
    extra = 1
    verbose_name = 'Color'
    verbose_name_plural = 'Product Colors'


class PriceInline(admin.TabularInline):
    """Inline for Prices in Product admin"""
    model = Price
    extra = 1
    verbose_name = 'Localized Price'
    verbose_name_plural = 'Prices'


class WarrantyInline(admin.TabularInline):
    """Inline for Warranties in Product admin"""
    model = Warranty
    extra = 1
    verbose_name = 'Warranty'
    verbose_name_plural = 'Warranties'


class SpecificationInline(admin.StackedInline):
    """Inline for Specification in Product admin (OneToOne relationship)"""
    model = Specification
    extra = 0
    max_num = 1  # Only one specification per product (OneToOne)
    can_delete = False
    verbose_name = 'Specification'
    verbose_name_plural = 'Specification'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for product categories"""
    list_display = ('name', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at')
    ordering = ('name',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for products"""
    list_display = ('name', 'category', 'price_per_unit', 'unit', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'unit', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('id', 'created_at')
    # Removed raw_id_fields to show dropdown instead of search widget
    ordering = ('-created_at',)
    inlines = [ProductColorInline, PriceInline, WarrantyInline, SpecificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_per_unit', 'unit')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    """Admin for product colors"""
    list_display = ('name', 'code', 'locale', 'product_count')
    list_filter = ('locale',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    
    def product_count(self, obj):
        return obj.product_colors.count()
    product_count.short_description = 'Products'


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    """Admin for product specifications"""
    list_display = ('product', 'size', 'level')
    search_fields = ('product__name', 'size', 'level')
    autocomplete_fields = ('product',)  # Better UI - searchable by product name
    ordering = ('product__name',)


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    """Admin for product-color relationships"""
    list_display = ('product', 'color')
    list_filter = ('color',)
    search_fields = ('product__name', 'color__name')
    raw_id_fields = ('product', 'color')


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Admin for product prices"""
    list_display = ('product', 'price', 'locale')
    list_filter = ('locale',)
    search_fields = ('product__name',)
    raw_id_fields = ('product',)
    ordering = ('product__name', 'locale')


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    """Admin for product warranties"""
    list_display = ('product', 'name', 'locale')
    list_filter = ('locale',)
    search_fields = ('product__name', 'name', 'description')
    raw_id_fields = ('product',)
    ordering = ('product__name',)


@admin.register(ProductCode)
class ProductCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'code', 'status', 'assigned_to', 'assigned_at', 'used_at', 'created_at')
    list_filter = ('status', 'product')
    search_fields = ('code', 'product__name', 'assigned_to__phone_number')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('product', 'assigned_to')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin for FAQs"""
    list_display = ('question', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'product', 'product_id_display', 'priority', 'price', 'locale', 'created_at']
    list_filter = ['locale', 'priority']
    search_fields = ['title', 'description', 'product__id', 'product__name']
    raw_id_fields = ['product', 'parent']
    readonly_fields = ['id', 'created_at', 'product_id_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon_url', 'locale')
        }),
        ('Product & Relationship', {
            'fields': ('product', 'product_id_display', 'parent'),
            'description': 'Product: Required - links problem to a product. Parent: Optional - creates hierarchical problem structure (e.g., "Screen Issues" → "Cracked Screen").'
        }),
        ('Pricing & Settings', {
            'fields': ('repair_duration', 'price', 'priority'),
            'description': 'Priority: Higher number = shown first (0 = lowest). Problems are sorted by priority (descending), then by title.'
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at')
        }),
    )
    
    def product_id_display(self, obj):
        """Display product UUID in admin."""
        if obj.product:
            return str(obj.product.id)
        return '-'
    product_id_display.short_description = 'Product ID (UUID)'
    product_id_display.admin_order_field = 'product__id'


@admin.register(ProductSection)
class ProductSectionAdmin(admin.ModelAdmin):
    """Admin for CMS Product Sections"""
    list_display = ('name', 'page', 'group_name', 'setting_type', 'is_active', 'created_at')
    list_filter = ('page', 'group_name', 'setting_type', 'is_active', 'created_at')
    search_fields = ('name', 'page', 'group_name', 'description')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('product',)
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'page', 'group_name', 'is_active')
        }),
        ('Content', {
            'fields': ('product', 'image_path', 'description', 'link_url', 'locale')
        }),
        ('Settings', {
            'fields': ('setting_type', 'expire_date', 'version')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """Admin interface for Bookmark model."""
    list_display = ['id', 'user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__phone_number', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user', 'product']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for Like model."""
    list_display = ['id', 'user', 'item_id', 'item_type', 'created_at']
    list_filter = ['item_type', 'created_at']
    search_fields = ['user__username', 'user__phone_number', 'item_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user']
    ordering = ['-created_at']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin interface for Brand model."""
    list_display = ['name', 'locale', 'is_active', 'created_at']
    list_filter = ['is_active', 'locale', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['name']

