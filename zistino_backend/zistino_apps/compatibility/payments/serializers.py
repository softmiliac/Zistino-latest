"""
Serializers for Payments endpoints.
These import from payments app serializers and add compatibility request/response serializers.
"""
from rest_framework import serializers


class PaymentRequestSerializer(serializers.Serializer):
    """Request serializer for payment processing matching old Swagger format."""
    addressId = serializers.IntegerField(required=False, allow_null=True, default=0)
    couponKey = serializers.CharField(required=False, allow_blank=True, default="string")
    zarinCallType = serializers.IntegerField(required=False, default=0)
    description = serializers.CharField(required=False, allow_blank=True, default="string")
    currency = serializers.CharField(required=False, allow_blank=True, default="string")


class PaymentResponseSerializer(serializers.Serializer):
    """Response serializer for payment processing matching old Swagger format."""
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    thumbnail = serializers.CharField(read_only=True, allow_null=True)
    locale = serializers.CharField(read_only=True, allow_null=True)
    masterId = serializers.CharField(read_only=True, allow_null=True)


class PaymentStripeRequestSerializer(serializers.Serializer):
    """Request serializer for Stripe payment matching old Swagger format."""
    addressId = serializers.IntegerField(required=False, allow_null=True, default=0)
    couponKey = serializers.CharField(required=False, allow_blank=True, default="string")
    zarinCallType = serializers.IntegerField(required=False, default=0)
    description = serializers.CharField(required=False, allow_blank=True, default="string")
    currency = serializers.CharField(required=False, allow_blank=True, default="string")


class StripePaymentResponseSerializer(serializers.Serializer):
    """Response serializer for Stripe payment matching old Swagger format."""
    id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    links = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )


class StripeVerifyPaymentRequestSerializer(serializers.Serializer):
    """Request serializer for Stripe payment verification matching old Swagger format."""
    # orderid is passed as query parameter, not in body
    pass


class PaymentPayPalRequestSerializer(serializers.Serializer):
    """Request serializer for PayPal payment matching old Swagger format."""
    addressId = serializers.IntegerField(required=False, allow_null=True, default=0)
    couponKey = serializers.CharField(required=False, allow_blank=True, default="string")
    zarinCallType = serializers.IntegerField(required=False, default=0)
    description = serializers.CharField(required=False, allow_blank=True, default="string")
    currency = serializers.CharField(required=False, allow_blank=True, default="string")


class PayPalPaymentResponseSerializer(serializers.Serializer):
    """Response serializer for PayPal payment matching old Swagger format."""
    id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    links = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )


class PayPalVerifyPaymentRequestSerializer(serializers.Serializer):
    """Request serializer for PayPal payment verification matching old Swagger format."""
    # order id is passed as query parameter, not in body
    pass


class PayPalVerifyCaptureRequestSerializer(serializers.Serializer):
    """Request serializer for PayPal capture verification matching old Swagger format."""
    # orderID is passed as query parameter, not in body
    pass


class PayPalCaptureResponseSerializer(serializers.Serializer):
    """Response serializer for PayPal capture verification matching old Swagger format."""
    id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    payment_source = serializers.DictField(read_only=True)
    purchase_units = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    payer = serializers.DictField(read_only=True)
    links = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )


class StripeWebhookRequestSerializer(serializers.Serializer):
    """Request serializer for Stripe webhook."""
    # Stripe webhook payload structure
    pass


class ProcessCallbackRequestSerializer(serializers.Serializer):
    """Request serializer for payment callback processing matching old Swagger format."""
    authority = serializers.CharField(required=False, allow_blank=True, default="string")
    ids = serializers.CharField(required=False, allow_blank=True, default="string")


class VerifyPaymentRequestSerializer(serializers.Serializer):
    """Request serializer for payment verification matching old Swagger format."""
    authority = serializers.CharField(required=False, allow_blank=True, default="string")
    ids = serializers.CharField(required=False, allow_blank=True, default="string")


class CheckoutRequestSerializer(serializers.Serializer):
    """Request serializer for checkout matching old Swagger format."""
    trackingNumber = serializers.IntegerField(required=False, default=0)
    generateTrackingNumberAutomatically = serializers.BooleanField(required=False, default=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    selectedGateway = serializers.IntegerField(required=False, default=0)


class RefundRequestSerializer(serializers.Serializer):
    """Request serializer for refund matching old Swagger format."""
    trackingNumber = serializers.IntegerField(required=True)
