"""
Compatibility views for Payments endpoints.
All endpoints will appear under "Payments" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Payments

Note: Most payment gateway endpoints (Stripe, PayPal) are placeholders and need actual integration.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from zistino_apps.users.permissions import IsManager

from zistino_apps.payments.models import Wallet, Transaction
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    PaymentRequestSerializer,
    PaymentResponseSerializer,
    PaymentStripeRequestSerializer,
    StripePaymentResponseSerializer,
    StripeVerifyPaymentRequestSerializer,
    PaymentPayPalRequestSerializer,
    PayPalPaymentResponseSerializer,
    PayPalVerifyPaymentRequestSerializer,
    PayPalVerifyCaptureRequestSerializer,
    PayPalCaptureResponseSerializer,
    StripeWebhookRequestSerializer,
    ProcessCallbackRequestSerializer,
    VerifyPaymentRequestSerializer,
    CheckoutRequestSerializer,
    RefundRequestSerializer,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


# ============================================================================
# PAYMENT SERVICE ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Payments'],
    operation_id='payments_paymentservice',
    summary='Get Payment Service',
    description='Get payment service information.',
    responses={200: {
        'description': 'Payment service information',
        'content': {
            'application/json': {
                'example': {
                    'serviceName': 'Zistino Payment Gateway',
                    'supportedMethods': ['stripe', 'paypal', 'wallet'],
                    'isActive': True
                }
            }
        }
    }}
)
class PaymentsPaymentServiceView(APIView):
    """GET /api/v1/payments/paymentservice - Get payment service information"""
    permission_classes = [AllowAny]  # Public endpoint

    def get(self, request):
        """Get payment service information."""
        return Response({
            'serviceName': 'Zistino Payment Gateway',
            'supportedMethods': ['stripe', 'paypal', 'wallet', 'cash'],
            'isActive': True
        })


# ============================================================================
# PAYMENT PROCESSING ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Payments'],
    operation_id='payments_payment',
    summary='Process Payment',
    description='Process a payment matching old Swagger format.',
    request=PaymentRequestSerializer,
    examples=[
        OpenApiExample(
            'Process payment',
            value={
                'addressId': 0,
                'couponKey': 'string',
                'zarinCallType': 0,
                'description': 'string',
                'currency': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PaymentResponseSerializer,
            description='Payment processed successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'id': 'string',
                            'name': 'string',
                            'thumbnail': 'string',
                            'locale': 'string',
                            'masterId': 'string'
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsPaymentView(APIView):
    """POST /api/v1/payments/payment - Process payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process a payment matching old Swagger format."""
        try:
            serializer = PaymentRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            address_id = validated_data.get('addressId', 0)
            coupon_key = validated_data.get('couponKey', 'string')
            zarin_call_type = validated_data.get('zarinCallType', 0)
            description = validated_data.get('description', 'string')
            currency = validated_data.get('currency', 'string')
            
            # Get user's basket/order for payment
            from zistino_apps.orders.models import Basket
            try:
                basket = Basket.objects.get(user=request.user, is_empty=False)
            except Basket.DoesNotExist:
                return create_error_response(
                    error_message='No active basket found. Please add items to your basket first.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'basket': ['No active basket found.']}
                )
            
            # Handle coupon if provided
            coupon = None
            if coupon_key and coupon_key != 'string' and coupon_key.strip():
                from zistino_apps.payments.models import Coupon
                try:
                    coupon = Coupon.objects.get(key=coupon_key, status=1)
                except Coupon.DoesNotExist:
                    return create_error_response(
                        error_message=f'Invalid coupon key: {coupon_key}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'couponKey': [f'Invalid coupon key: {coupon_key}']}
                    )
            
            # TODO: Implement actual payment processing based on zarinCallType
            # For now, return a placeholder response matching old Swagger format
            # The response format suggests it might be returning order/product information
            
            # Generate a placeholder payment ID (UUID as string)
            import uuid
            payment_id = str(uuid.uuid4())
            
            # Return response matching old Swagger format
            payment_data = {
                'id': payment_id,
                'name': 'Payment',  # Placeholder
                'thumbnail': None,
                'locale': None,
                'masterId': None
            }
            
            return create_success_response(
                data=payment_data,
                messages=['Payment processed successfully']
            )
        
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the payment: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_paymentstripe',
    summary='Process Stripe Payment',
    description='Process a payment using Stripe matching old Swagger format.',
    request=PaymentStripeRequestSerializer,
    examples=[
        OpenApiExample(
            'Process Stripe payment',
            value={
                'addressId': 0,
                'couponKey': 'string',
                'zarinCallType': 0,
                'description': 'string',
                'currency': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=StripePaymentResponseSerializer,
            description='Stripe payment initiated successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'id': 'string',
                            'status': 'string',
                            'links': [
                                {
                                    'href': 'string',
                                    'rel': 'string',
                                    'method': 'string'
                                }
                            ]
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsPaymentStripeView(APIView):
    """POST /api/v1/payments/paymentstripe - Process Stripe payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process a Stripe payment matching old Swagger format."""
        try:
            serializer = PaymentStripeRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # TODO: Implement actual Stripe payment processing
            # For now, return placeholder response matching old Swagger format
            import uuid
            payment_id = str(uuid.uuid4())
            
            payment_data = {
                'id': payment_id,
                'status': 'pending',
                'links': [
                    {
                        'href': 'https://stripe.com/checkout',
                        'rel': 'approval_url',
                        'method': 'GET'
                    }
                ]
            }
            
            return create_success_response(
                data=payment_data,
                messages=['Stripe payment initiated successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the Stripe payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_stripe_verify_payment',
    summary='Verify Stripe Payment',
    description='Verify a Stripe payment transaction matching old Swagger format. Accepts orderid as query parameter.',
    parameters=[
        OpenApiParameter(
            name='orderid',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Order ID to verify'
        )
    ],
    request=StripeVerifyPaymentRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Payment verified successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsStripeVerifyPaymentView(APIView):
    """POST /api/v1/payments/stripe-verify-payment - Verify Stripe payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify a Stripe payment matching old Swagger format."""
        try:
            orderid = request.query_params.get('orderid', None)
            
            # TODO: Implement actual Stripe payment verification
            # For now, return placeholder response matching old Swagger format
            verification_result = f'Payment verified for order: {orderid}' if orderid else 'Payment verified'
            
            return create_success_response(
                data=verification_result,
                messages=['Stripe payment verified successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while verifying the Stripe payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_paymentpaypal',
    summary='Process PayPal Payment',
    description='Process a payment using PayPal matching old Swagger format.',
    request=PaymentPayPalRequestSerializer,
    examples=[
        OpenApiExample(
            'Process PayPal payment',
            value={
                'addressId': 0,
                'couponKey': 'string',
                'zarinCallType': 0,
                'description': 'string',
                'currency': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PayPalPaymentResponseSerializer,
            description='PayPal payment initiated successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'id': 'string',
                            'status': 'string',
                            'links': [
                                {
                                    'href': 'string',
                                    'rel': 'string',
                                    'method': 'string'
                                }
                            ]
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsPaymentPayPalView(APIView):
    """POST /api/v1/payments/paymentpaypal - Process PayPal payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process a PayPal payment matching old Swagger format."""
        try:
            serializer = PaymentPayPalRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # TODO: Implement actual PayPal payment processing
            # For now, return placeholder response matching old Swagger format
            import uuid
            payment_id = str(uuid.uuid4())
            
            payment_data = {
                'id': payment_id,
                'status': 'pending',
                'links': [
                    {
                        'href': 'https://paypal.com/checkout',
                        'rel': 'approval_url',
                        'method': 'GET'
                    }
                ]
            }
            
            return create_success_response(
                data=payment_data,
                messages=['PayPal payment initiated successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the PayPal payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_paypaltest',
    summary='Test PayPal Payment',
    description='Test PayPal payment processing (sandbox mode) matching old Swagger format.',
    request=PaymentPayPalRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=PayPalPaymentResponseSerializer,
            description='PayPal test payment processed successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'id': 'string',
                            'status': 'string',
                            'links': [
                                {
                                    'href': 'string',
                                    'rel': 'string',
                                    'method': 'string'
                                }
                            ]
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsPayPalTestView(APIView):
    """POST /api/v1/payments/paypaltest - Test PayPal payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Test PayPal payment matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # TODO: Implement actual PayPal test payment processing
            # For now, return placeholder response matching old Swagger format
            import uuid
            payment_id = str(uuid.uuid4())
            
            payment_data = {
                'id': payment_id,
                'status': 'test_mode',
                'links': [
                    {
                        'href': 'https://paypal.com/sandbox/checkout',
                        'rel': 'approval_url',
                        'method': 'GET'
                    }
                ]
            }
            
            return create_success_response(
                data=payment_data,
                messages=['PayPal test payment processed successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the PayPal test payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_paypal_verify_capture',
    summary='Verify PayPal Capture',
    description='Verify a PayPal capture transaction matching old Swagger format. Accepts orderID as query parameter.',
    parameters=[
        OpenApiParameter(
            name='orderID',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Order ID to verify'
        )
    ],
    request=PayPalVerifyCaptureRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=PayPalCaptureResponseSerializer,
            description='PayPal capture verified successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'id': 'string',
                            'status': 'string',
                            'payment_source': {
                                'paypal': {
                                    'name': {
                                        'given_name': 'string',
                                        'surname': 'string'
                                    },
                                    'email_address': 'string',
                                    'account_id': 'string'
                                }
                            },
                            'purchase_units': [
                                {
                                    'amount': {
                                        'currency_code': 'string',
                                        'value': 'string'
                                    },
                                    'reference_id': 'string',
                                    'shipping': {
                                        'address': {
                                            'address_line_1': 'string',
                                            'address_line_2': 'string',
                                            'admin_area_2': 'string',
                                            'admin_area_1': 'string',
                                            'postal_code': 'string',
                                            'country_code': 'string'
                                        }
                                    },
                                    'payments': {
                                        'captures': [
                                            {
                                                'id': 'string',
                                                'status': 'string',
                                                'amount': {
                                                    'currency_code': 'string',
                                                    'value': 'string'
                                                },
                                                'seller_protection': {
                                                    'status': 'string',
                                                    'dispute_categories': ['string']
                                                },
                                                'final_capture': True,
                                                'disbursement_mode': 'string',
                                                'seller_receivable_breakdown': {
                                                    'gross_amount': {
                                                        'currency_code': 'string',
                                                        'value': 'string'
                                                    },
                                                    'paypal_fee': {
                                                        'currency_code': 'string',
                                                        'value': 'string'
                                                    },
                                                    'net_amount': {
                                                        'currency_code': 'string',
                                                        'value': 'string'
                                                    }
                                                },
                                                'create_time': '2025-11-10T08:11:23.485Z',
                                                'update_time': '2025-11-10T08:11:23.485Z',
                                                'links': [
                                                    {
                                                        'href': 'string',
                                                        'rel': 'string',
                                                        'method': 'string'
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                }
                            ],
                            'payer': {
                                'name': {
                                    'given_name': 'string',
                                    'surname': 'string'
                                },
                                'email_address': 'string',
                                'payer_id': 'string'
                            },
                            'links': [
                                {
                                    'href': 'string',
                                    'rel': 'string',
                                    'method': 'string'
                                }
                            ]
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsPayPalVerifyCaptureView(APIView):
    """POST /api/v1/payments/paypal-verify-capture - Verify PayPal capture"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify a PayPal capture matching old Swagger format."""
        try:
            order_id = request.query_params.get('orderID', None)
            
            # TODO: Implement actual PayPal capture verification
            # For now, return placeholder response matching old Swagger format
            import uuid
            capture_id = str(uuid.uuid4())
            
            capture_data = {
                'id': capture_id,
                'status': 'completed',
                'payment_source': {
                    'paypal': {
                        'name': {
                            'given_name': 'John',
                            'surname': 'Doe'
                        },
                        'email_address': 'buyer@example.com',
                        'account_id': 'string'
                    }
                },
                'purchase_units': [
                    {
                        'amount': {
                            'currency_code': 'USD',
                            'value': '100.00'
                        },
                        'reference_id': order_id or 'string',
                        'shipping': {
                            'address': {
                                'address_line_1': 'string',
                                'address_line_2': 'string',
                                'admin_area_2': 'string',
                                'admin_area_1': 'string',
                                'postal_code': 'string',
                                'country_code': 'US'
                            }
                        },
                        'payments': {
                            'captures': [
                                {
                                    'id': capture_id,
                                    'status': 'completed',
                                    'amount': {
                                        'currency_code': 'USD',
                                        'value': '100.00'
                                    },
                                    'seller_protection': {
                                        'status': 'ELIGIBLE',
                                        'dispute_categories': ['ITEM_NOT_RECEIVED', 'UNAUTHORIZED_TRANSACTION']
                                    },
                                    'final_capture': True,
                                    'disbursement_mode': 'INSTANT',
                                    'seller_receivable_breakdown': {
                                        'gross_amount': {
                                            'currency_code': 'USD',
                                            'value': '100.00'
                                        },
                                        'paypal_fee': {
                                            'currency_code': 'USD',
                                            'value': '3.20'
                                        },
                                        'net_amount': {
                                            'currency_code': 'USD',
                                            'value': '96.80'
                                        }
                                    },
                                    'create_time': '2025-11-10T08:11:23.485Z',
                                    'update_time': '2025-11-10T08:11:23.485Z',
                                    'links': [
                                        {
                                            'href': 'https://api.paypal.com/v2/payments/captures/' + capture_id,
                                            'rel': 'self',
                                            'method': 'GET'
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ],
                'payer': {
                    'name': {
                        'given_name': 'John',
                        'surname': 'Doe'
                    },
                    'email_address': 'buyer@example.com',
                    'payer_id': 'string'
                },
                'links': [
                    {
                        'href': 'https://api.paypal.com/v2/payments/captures/' + capture_id,
                        'rel': 'self',
                        'method': 'GET'
                    }
                ]
            }
            
            return create_success_response(
                data=capture_data,
                messages=['PayPal capture verified successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while verifying the PayPal capture: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_paypal_verify_payment',
    summary='Verify PayPal Payment',
    description='Verify a PayPal payment transaction matching old Swagger format. Accepts order id as query parameter.',
    parameters=[
        OpenApiParameter(
            name='order id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Order ID to verify (required)'
        )
    ],
    request=PayPalVerifyPaymentRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Payment verified successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsPayPalVerifyPaymentView(APIView):
    """POST /api/v1/payments/paypal-verify-payment - Verify PayPal payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify a PayPal payment matching old Swagger format."""
        try:
            order_id = request.query_params.get('order id', None) or request.query_params.get('orderid', None)
            
            if not order_id:
                return create_error_response(
                    error_message='order id is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'order id': ['This query parameter is required']}
                )
            
            # TODO: Implement actual PayPal payment verification
            # For now, return placeholder response matching old Swagger format
            verification_result = f'PayPal payment verified for order: {order_id}'
            
            return create_success_response(
                data=verification_result,
                messages=['PayPal payment verified successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while verifying the PayPal payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# WEBHOOK AND CALLBACK ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Payments'],
    operation_id='payments_stripewebhook',
    summary='Stripe Webhook',
    description='Handle Stripe webhook events matching old Swagger format.',
    request=StripeWebhookRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Webhook processed successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'}
    }
)
class PaymentsStripeWebhookView(APIView):
    """POST /api/v1/payments/stripewebhook - Handle Stripe webhook"""
    permission_classes = [AllowAny]  # Webhooks are public but should verify signature

    def post(self, request):
        """Handle Stripe webhook matching old Swagger format."""
        try:
            # TODO: Implement Stripe webhook handling with signature verification
            # import stripe
            # payload = request.body
            # sig_header = request.META['HTTP_STRIPE_SIGNATURE']
            # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            
            # For now, return placeholder response matching old Swagger format
            webhook_result = 'Webhook received and processed'
            
            return create_success_response(
                data=webhook_result,
                messages=['Stripe webhook processed successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the Stripe webhook: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_proccesscallback',
    summary='Process Payment Callback',
    description='Process payment callback from payment gateway matching old Swagger format.',
    request=ProcessCallbackRequestSerializer,
    examples=[
        OpenApiExample(
            'Process callback',
            value={
                'authority': 'string',
                'ids': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Callback processed successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'}
    }
)
class PaymentsProcessCallbackView(APIView):
    """POST /api/v1/payments/proccesscallback - Process payment callback"""
    permission_classes = [AllowAny]  # Callbacks are public but should verify signature

    def post(self, request):
        """Process payment callback matching old Swagger format."""
        try:
            serializer = ProcessCallbackRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            authority = validated_data.get('authority', 'string')
            ids = validated_data.get('ids', 'string')
            
            # TODO: Implement payment callback processing
            # For now, return placeholder response matching old Swagger format
            callback_result = f'Callback processed for authority: {authority}, ids: {ids}'
            
            return create_success_response(
                data=callback_result,
                messages=['Payment callback processed successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the payment callback: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# VERIFICATION ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Payments'],
    operation_id='payments_verify_payment',
    summary='Verify Payment',
    description='Verify a payment transaction matching old Swagger format.',
    request=VerifyPaymentRequestSerializer,
    examples=[
        OpenApiExample(
            'Verify payment',
            value={
                'authority': 'string',
                'ids': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Payment verified successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsVerifyPaymentView(APIView):
    """POST /api/v1/payments/verify-payment - Verify payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify a payment transaction matching old Swagger format."""
        try:
            serializer = VerifyPaymentRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            authority = validated_data.get('authority', 'string')
            ids = validated_data.get('ids', 'string')
            
            # TODO: Implement actual payment verification
            # For now, return placeholder response matching old Swagger format
            verification_result = f'Payment verified for authority: {authority}, ids: {ids}'
            
            return create_success_response(
                data=verification_result,
                messages=['Payment verified successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while verifying the payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_client_verify_payment',
    summary='Client Verify Payment',
    description='Verify payment for the authenticated user matching old Swagger format.',
    request=VerifyPaymentRequestSerializer,
    examples=[
        OpenApiExample(
            'Verify payment',
            value={
                'authority': 'string',
                'ids': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Payment verified successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsClientVerifyPaymentView(APIView):
    """POST /api/v1/payments/client/verify-payment - Client verify payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify payment for authenticated user matching old Swagger format."""
        try:
            serializer = VerifyPaymentRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            authority = validated_data.get('authority', 'string')
            ids = validated_data.get('ids', 'string')
            
            # TODO: Implement actual payment verification
            # For now, return placeholder response matching old Swagger format
            verification_result = f'Payment verified for authority: {authority}, ids: {ids}'
            
            return create_success_response(
                data=verification_result,
                messages=['Payment verified successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while verifying the payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_verify',
    summary='Verify Payment',
    description='Verify payment using GET or POST method matching old Swagger format. Accepts authority as query parameter.',
    parameters=[
        OpenApiParameter(
            name='authority',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Payment authority code to verify'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Payment verified successfully when authority is successful',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsVerifyCombinedView(APIView):
    """GET/POST /api/v1/payments/verify - Verify payment (handles both GET and POST)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Verify payment using GET method - checks authority query parameter."""
        return self._verify_payment(request)

    def post(self, request):
        """Verify payment using POST method - checks authority query parameter (no request body)."""
        return self._verify_payment(request)
    
    def _verify_payment(self, request):
        """Common verification logic for both GET and POST."""
        try:
            # Get authority from query parameters (not from request body)
            authority = request.query_params.get('authority', None)
            
            # If authority is provided and is successful, return data
            if authority:
                # TODO: Implement actual payment verification logic
                # Check if authority is valid and payment is successful
                # For now, if authority exists, consider it successful
                
                # Try to find transaction or order by authority
                verification_data = None
                try:
                    # Transaction is already imported at the top of the file
                    transaction = Transaction.objects.filter(
                        reference_id=authority
                    ).first()
                    
                    if transaction:
                        verification_data = {
                            'transactionId': str(transaction.id),
                            'status': transaction.status,
                            'amount': str(transaction.amount),
                            'authority': authority
                        }
                except:
                    pass
                
                # If no transaction found, return generic success
                if not verification_data:
                    verification_data = {
                        'authority': authority,
                        'status': 'verified'
                    }
                
                return create_success_response(
                    data=verification_data,
                    messages=['Payment verified successfully']
                )
            else:
                # No authority provided - return error or empty response
                return create_error_response(
                    error_message='Authority parameter is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'authority': ['Authority query parameter is required']}
                )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while verifying the payment: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# CHECKOUT AND REFUND ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Payments'],
    operation_id='payments_checkout',
    summary='Checkout',
    description='Process checkout for an order matching old Swagger format.',
    request=CheckoutRequestSerializer,
    examples=[
        OpenApiExample(
            'Process checkout',
            value={
                'trackingNumber': 0,
                'generateTrackingNumberAutomatically': True,
                'amount': 0,
                'selectedGateway': 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Checkout processed successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'checkoutId': 'chk_123456',
                            'status': 'pending',
                            'trackingNumber': 123456789,
                            'selectedGateway': 0
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'}
    }
)
class PaymentsCheckoutView(APIView):
    """POST /api/v1/payments/checkout - Process checkout"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process checkout for an order matching old Swagger format."""
        try:
            serializer = CheckoutRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            tracking_number = validated_data.get('trackingNumber', 0)
            generate_tracking_automatically = validated_data.get('generateTrackingNumberAutomatically', True)
            amount = validated_data.get('amount', 0)
            selected_gateway = validated_data.get('selectedGateway', 0)
            
            # Generate tracking number if needed
            if generate_tracking_automatically:
                # TODO: Implement actual tracking number generation logic
                import random
                tracking_number = random.randint(100000000, 999999999)
            
            # TODO: Implement checkout logic based on selectedGateway
            # - Gateway 0: wallet
            # - Gateway 1: stripe
            # - Gateway 2: paypal
            # - Gateway 3: cash
            # - If wallet: deduct from user's wallet
            # - If stripe/paypal: redirect to payment gateway
            # - If cash: mark as pending
            
            # For now, return placeholder response matching old Swagger format
            import uuid
            checkout_id = str(uuid.uuid4())
            
            checkout_data = {
                'checkoutId': checkout_id,
                'status': 'pending',
                'trackingNumber': tracking_number,
                'selectedGateway': selected_gateway
            }
            
            return create_success_response(
                data=checkout_data,
                messages=['Checkout processed successfully']
            )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the checkout: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Payments'],
    operation_id='payments_refund',
    summary='Refund Payment',
    description='Process a refund for a payment transaction matching old Swagger format.',
    request=RefundRequestSerializer,
    examples=[
        OpenApiExample(
            'Process refund',
            value={
                'trackingNumber': 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Refund processed successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'refundId': 'ref_123456',
                            'status': 'pending',
                            'amount': '50.00',
                            'trackingNumber': 0
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'},
        403: {'description': 'Permission denied - Manager role required'}
    }
)
class PaymentsRefundView(APIView):
    """POST /api/v1/payments/refund - Process refund"""
    permission_classes = [IsAuthenticated, IsManager]  # Only managers can refund

    def post(self, request):
        """Process a refund matching old Swagger format."""
        try:
            serializer = RefundRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            tracking_number = validated_data.get('trackingNumber')
            
            # Find order by payment_tracking_code
            # Convert tracking_number to string for comparison
            tracking_code_str = str(tracking_number)
            
            try:
                from zistino_apps.orders.models import Order
                order = Order.objects.get(payment_tracking_code=tracking_code_str)
                
                # Find related transaction if exists
                transaction = None
                try:
                    # Try to find transaction by reference_id or description containing order info
                    transaction = Transaction.objects.filter(
                        reference_id=tracking_code_str
                    ).first()
                except:
                    pass
                
                # TODO: Implement refund logic
                # - If Stripe: use Stripe refund API
                # - If PayPal: use PayPal refund API
                # - If wallet: credit back to wallet
                
                # For now, return placeholder response matching old Swagger format
                import uuid
                refund_id = str(uuid.uuid4())
                
                refund_amount = transaction.amount if transaction else order.total_price
                
                refund_data = {
                    'refundId': refund_id,
                    'status': 'pending',
                    'amount': str(refund_amount),
                    'trackingNumber': tracking_number
                }
                
                return create_success_response(
                    data=refund_data,
                    messages=['Refund processed successfully']
                )
            except Order.DoesNotExist:
                return create_error_response(
                    error_message=f'Order with tracking number "{tracking_number}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'trackingNumber': [f'Order with tracking number "{tracking_number}" not found.']}
                )
        
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing the refund: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

