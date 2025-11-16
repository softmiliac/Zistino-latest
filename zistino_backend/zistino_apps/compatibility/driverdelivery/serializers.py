"""
Serializers for DriverDelivery endpoints.
These import from deliveries app serializers and add compatibility request/response serializers.
"""
from rest_framework import serializers
from zistino_apps.deliveries.serializers import DeliverySerializer, DeliverySearchRequestSerializer
from zistino_apps.deliveries.models import Delivery

# Reuse DeliverySerializer and DeliverySearchRequestSerializer from deliveries app
# These are already compatible with Flutter app expectations


class DriverDeliveryCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating driver delivery matching old Swagger format."""
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    deliveryUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Delivery User ID (UUID string)')
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Delivery date')
    setUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Set User ID (UUID string)')
    addressId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Address ID')
    orderId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Order ID')
    examId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Exam ID')
    requestId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Request ID')
    zoneId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Zone ID')
    preOrderId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Pre Order ID')
    status = serializers.IntegerField(required=False, default=0, help_text='Delivery status (0=assigned, 1=in_progress, 2=completed, 3=cancelled)')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Description')


class DriverDeliveryUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for updating driver delivery matching old Swagger format."""
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    deliveryUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Delivery User ID (UUID string)')
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Delivery date')
    setUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Set User ID (UUID string)')
    addressId = serializers.IntegerField(required=False, allow_null=True, help_text='Address ID')
    orderId = serializers.IntegerField(required=False, allow_null=True, help_text='Order ID')
    examId = serializers.IntegerField(required=False, allow_null=True, help_text='Exam ID')
    requestId = serializers.IntegerField(required=False, allow_null=True, help_text='Request ID')
    zoneId = serializers.IntegerField(required=False, allow_null=True, help_text='Zone ID')
    preOrderId = serializers.IntegerField(required=False, allow_null=True, help_text='Pre Order ID')
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Delivery status (0=assigned, 1=in_progress, 2=completed, 3=cancelled)')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Description')


class DriverDeliverySearchRequestSerializer(serializers.Serializer):
    """Request serializer for driver delivery search matching old Swagger format."""
    advancedSearch = serializers.DictField(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True
    )
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Delivery status (0=assigned, 1=in_progress, 2=completed, 3=cancelled)')
    userid = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    fromDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Start date filter')
    toDate = serializers.DateTimeField(required=False, allow_null=True, help_text='End date filter')

