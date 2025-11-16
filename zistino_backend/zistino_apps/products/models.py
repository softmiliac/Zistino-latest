from django.db import models
import uuid


class Category(models.Model):
    """Product category model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    type = models.IntegerField(default=0, help_text='Category type (0-32)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model for recyclable items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')  # kg, piece, etc.
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class Color(models.Model):
    """Product color - matches ColorsModel fields (name, code, locale)."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    locale = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'colors'
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'

    def __str__(self):
        return self.name


class ProductColor(models.Model):
    """Many-to-many relation between Product and Color."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='product_colors')

    class Meta:
        db_table = 'product_colors'
        unique_together = ('product', 'color')


class Price(models.Model):
    """Localized price for a product - matches PriceModel (price, locale)."""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price = models.IntegerField(default=0)
    locale = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'prices'
        verbose_name = 'Price'
        verbose_name_plural = 'Prices'


class Specification(models.Model):
    """Simple specification - matches SpecificationModel (size, level)."""
    id = models.AutoField(primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='specification')
    size = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'specifications'
        verbose_name = 'Specification'
        verbose_name_plural = 'Specifications'


class ProductCode(models.Model):
    """Inventory of redeemable codes for code-based products (e.g., recharge codes)."""
    STATUS_CHOICES = [
        ('unused', 'Unused'),
        ('assigned', 'Assigned'),
        ('used', 'Used'),
    ]

    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='codes')
    code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unused')
    assigned_to = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_codes')
    assigned_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_codes'
        verbose_name = 'Product Code'
        verbose_name_plural = 'Product Codes'
        indexes = [
            models.Index(fields=['product', 'status']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.code} ({self.status})"


class Warranty(models.Model):
    """Product warranty - matches WarrantiesModel (name, image_url, description, locale)."""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warranties')
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    locale = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'warranties'
        verbose_name = 'Warranty'
        verbose_name_plural = 'Warranties'


class FAQ(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'faqs'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'


class Problem(models.Model):
    """Problem model for product repair/maintenance issues."""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon_url = models.CharField(max_length=500, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', 
                               help_text='Parent problem (optional). Use to create hierarchical problem categories. Leave empty for top-level problems.')
    repair_duration = models.IntegerField(default=0, help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='problems',
                               help_text='Product this problem is associated with. Required.')
    priority = models.IntegerField(default=0, 
                                   help_text='Display priority (higher number = shown first). 0 = lowest priority. Used for ordering: problems are sorted by priority (descending), then by title.')
    locale = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'problems'
        verbose_name = 'Problem'
        verbose_name_plural = 'Problems'
        ordering = ['-priority', 'title']

    def __str__(self):
        return self.title


class ProductSection(models.Model):
    """CMS ProductSection for home page banners/sections - matches ProductSectionModel."""
    SECTION_TYPE_CHOICES = [
        (0, 'banner'),
        (1, 'horizontal'),
        (2, 'countDown'),
        (3, 'lazy'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    page = models.CharField(max_length=50, default='home')
    group_name = models.CharField(max_length=100, blank=True)
    version = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sections', blank=True, null=True)
    image_path = models.URLField(blank=True)
    setting_type = models.IntegerField(choices=SECTION_TYPE_CHOICES, default=0)
    expire_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    link_url = models.URLField(blank=True)
    locale = models.CharField(max_length=10, default='en')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_sections'
        verbose_name = 'Product Section'
        verbose_name_plural = 'Product Sections'
        indexes = [
            models.Index(fields=['page', 'is_active']),
            models.Index(fields=['group_name', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.page})"


class Bookmark(models.Model):
    """Bookmark model - links users to products they want to save."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookmarks'
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        # Ensure a user can only bookmark a product once
        unique_together = ['user', 'product']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.product.name}"


class Brand(models.Model):
    """Brand model for product manufacturers/brands."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)
    locale = models.CharField(max_length=10, default='fa')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['locale', 'is_active']),
        ]

    def __str__(self):
        return self.name


class Like(models.Model):
    """
    Like model - allows users to like products and other items.
    Supports different content types (product, item, etc.)
    """
    LIKE_TYPE_CHOICES = [
        ('product', 'Product'),
        ('item', 'Item'),
        ('blog', 'Blog Post'),
        ('comment', 'Comment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='likes'
    )
    # Content type and ID (generic foreign key approach)
    item_id = models.UUIDField(help_text='ID of the liked item (product, blog post, etc.)')
    item_type = models.CharField(max_length=50, choices=LIKE_TYPE_CHOICES, default='product')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'likes'
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        # Ensure a user can only like an item once
        unique_together = ['user', 'item_id', 'item_type']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'item_type', 'created_at']),
            models.Index(fields=['item_id', 'item_type']),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.item_type} {self.item_id}"