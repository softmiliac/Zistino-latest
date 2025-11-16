"""Models for Products compatibility layer."""
from zistino_apps.products.models import Product, Category
from django.db import models
import uuid


class ProductGroup(models.Model):
    """Product group model for grouping products together."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_groups'
        verbose_name = 'Product Group'
        verbose_name_plural = 'Product Groups'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductGroupItem(models.Model):
    """Many-to-many relation between ProductGroup and Product."""
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='groups')
    order = models.IntegerField(default=0, help_text='Order within the group')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_group_items'
        unique_together = ('group', 'product')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.group.name} - {self.product.name}"


__all__ = ['Product', 'Category', 'ProductGroup', 'ProductGroupItem']

