"""
Payments compatibility URL routes for Flutter apps.
All 16 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Payments

Flutter expects: /api/v1/payments/{endpoint}
All endpoints are tagged with 'Payments' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/payments/paymentservice - Get payment service information
2. POST /api/v1/payments/payment - Process payment (generic)
3. POST /api/v1/payments/paymentstripe - Process Stripe payment
4. POST /api/v1/payments/stripe-verify-payment - Verify Stripe payment
5. POST /api/v1/payments/paymentpaypal - Process PayPal payment
6. POST /api/v1/payments/paypaltest - Test PayPal payment
7. POST /api/v1/payments/paypal-verify-capture - Verify PayPal capture
8. POST /api/v1/payments/paypal-verify-payment - Verify PayPal payment
9. POST /api/v1/payments/stripewebhook - Handle Stripe webhook
10. POST /api/v1/payments/proccesscallback - Process payment callback
11. POST /api/v1/payments/verify-payment - Verify payment
12. POST /api/v1/payments/client/verify-payment - Client verify payment
13. POST /api/v1/payments/checkout - Process checkout
14. GET /api/v1/payments/verify - Verify payment (GET)
15. POST /api/v1/payments/verify - Verify payment (POST)
16. POST /api/v1/payments/refund - Process refund
"""
from django.urls import path
from . import views

urlpatterns = [
    # PAYMENT SERVICE
    path('paymentservice', views.PaymentsPaymentServiceView.as_view(), name='payments-paymentservice'),
    
    # PAYMENT PROCESSING
    path('payment', views.PaymentsPaymentView.as_view(), name='payments-payment'),
    path('paymentstripe', views.PaymentsPaymentStripeView.as_view(), name='payments-paymentstripe'),
    path('stripe-verify-payment', views.PaymentsStripeVerifyPaymentView.as_view(), name='payments-stripe-verify-payment'),
    path('paymentpaypal', views.PaymentsPaymentPayPalView.as_view(), name='payments-paymentpaypal'),
    path('paypaltest', views.PaymentsPayPalTestView.as_view(), name='payments-paypaltest'),
    path('paypal-verify-capture', views.PaymentsPayPalVerifyCaptureView.as_view(), name='payments-paypal-verify-capture'),
    path('paypal-verify-payment', views.PaymentsPayPalVerifyPaymentView.as_view(), name='payments-paypal-verify-payment'),
    
    # WEBHOOKS AND CALLBACKS
    path('stripewebhook', views.PaymentsStripeWebhookView.as_view(), name='payments-stripewebhook'),
    path('proccesscallback', views.PaymentsProcessCallbackView.as_view(), name='payments-proccesscallback'),
    
    # VERIFICATION
    path('verify-payment', views.PaymentsVerifyPaymentView.as_view(), name='payments-verify-payment'),
    path('client/verify-payment', views.PaymentsClientVerifyPaymentView.as_view(), name='payments-client-verify-payment'),
    # Note: /verify endpoint handles both GET and POST - we'll create a combined view
    path('verify', views.PaymentsVerifyCombinedView.as_view(), name='payments-verify'),
    
    # CHECKOUT AND REFUND
    path('checkout', views.PaymentsCheckoutView.as_view(), name='payments-checkout'),
    path('refund', views.PaymentsRefundView.as_view(), name='payments-refund'),
]

