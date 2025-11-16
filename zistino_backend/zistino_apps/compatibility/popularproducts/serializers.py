"""
Serializers for PopularProducts endpoints.
These import from products app serializers and add compatibility request/response serializers.
"""
from zistino_apps.products.serializers import ProductSerializer
from zistino_apps.compatibility.products.serializers import (
    ProductExportRequestSerializer,
    ProductClientSearchRequestSerializer,
    ProductCompatibilitySerializer,
    ProductAdminSearchExtResponseSerializer,
)
from rest_framework import serializers


# Reuse ProductExportRequestSerializer from products compatibility app for search endpoint
PopularProductSearchRequestSerializer = ProductExportRequestSerializer

# Reuse ProductClientSearchRequestSerializer from products compatibility app for client/search endpoint
PopularProductClientSearchRequestSerializer = ProductClientSearchRequestSerializer

