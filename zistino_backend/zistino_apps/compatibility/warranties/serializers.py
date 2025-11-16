"""
Serializers for Warranties endpoints.
These import from products app serializers and add compatibility request/response serializers.
"""
from rest_framework import serializers
from zistino_apps.products.serializers import WarrantySerializer, WarrantySearchRequestSerializer
from zistino_apps.products.models import Warranty

# Reuse WarrantySerializer and WarrantySearchRequestSerializer from products app
# These are already compatible with Flutter app expectations


class WarrantyCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for Warranty matching old Swagger format (simplified for list)."""
    thumbnail = serializers.CharField(source='image_url', read_only=True, allow_null=True)
    
    class Meta:
        model = Warranty
        fields = ['id', 'name', 'thumbnail', 'locale']
        read_only_fields = ['id']


class WarrantyDetailSerializer(serializers.ModelSerializer):
    """Detailed compatibility serializer for Warranty matching old Swagger format (full details)."""
    imageUrl = serializers.CharField(source='image_url', read_only=True, allow_null=True)
    thumbnail = serializers.CharField(source='image_url', read_only=True, allow_null=True)
    
    class Meta:
        model = Warranty
        fields = ['id', 'name', 'imageUrl', 'thumbnail', 'description', 'locale']
        read_only_fields = ['id']


class WarrantyCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating warranty matching old Swagger format."""
    name = serializers.CharField(required=True, max_length=255, help_text='Warranty name')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Thumbnail URL')
    description = serializers.CharField(required=False, allow_blank=True, help_text='Warranty description')
    locale = serializers.CharField(required=False, allow_blank=True, max_length=10, help_text='Locale')

