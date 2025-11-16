"""
Identity compatibility URL routes for Flutter apps.
All 23 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Identity

Flutter expects: /api/v1/identity/{endpoint}
All endpoints are tagged with 'Identity' to appear grouped in Swagger UI.

Endpoints:
1. POST /api/v1/identity/register - Register new user
2. POST /api/v1/identity/register-with-code - Register with code
3. POST /api/v1/identity/register-with-phonecall - Register with phone call
4. GET /api/v1/identity/check-duplicate/{email} - Check duplicate email
5. POST /api/v1/identity/verify - Validate Access Token
6. POST /api/v1/identity/verifytoken - Validate Access Token
7. POST /api/v1/identity/verifyphonenumber - Verify phone number
8. POST /api/v1/identity/sendconfirmemail - Send confirmation email
9. GET /api/v1/identity/confirm-email-by-admin - Confirm email by admin
10. GET /api/v1/identity/confirm-email - Confirm email
11. GET /api/v1/identity/confirm-email-by-code - Confirm email by code
12. GET /api/v1/identity/verify-email-by-code - Verify email by code
13. POST /api/v1/identity/confirm-email-code-registerd - Confirm email code for registered user
14. GET /api/v1/identity/confirm-phone-number - Confirm phone number
15. GET /api/v1/identity/confirm-phone-number-by-admin - Confirm phone number by admin
16. POST /api/v1/identity/forgot-password - Forgot password
17. POST /api/v1/identity/forgot-password-by-code - Forgot password by code
18. POST /api/v1/identity/send-code - Send code
19. GET /api/v1/identity/send-code-representative/{phoneNumber}/{RepresentativeCode} - Send code representative
20. POST /api/v1/identity/reset-password - Reset password
21. POST /api/v1/identity/check-reset-password-code - Check reset password code
22. POST /api/v1/identity/reset-password-by-code - Reset password by code
23. GET /api/v1/identity/test-email/{email} - Test email
"""
from django.urls import path
from . import views

urlpatterns = [
    # REGISTRATION ENDPOINTS
    path('register', views.IdentityRegisterView.as_view(), name='identity-register'),
    path('register-with-code', views.IdentityRegisterWithCodeView.as_view(), name='identity-register-with-code'),
    path('register-with-phonecall', views.IdentityRegisterWithPhoneCallView.as_view(), name='identity-register-with-phonecall'),
    
    # VERIFICATION ENDPOINTS
    path('check-duplicate/<str:email>', views.IdentityCheckDuplicateView.as_view(), name='identity-check-duplicate'),
    path('verify', views.IdentityVerifyView.as_view(), name='identity-verify'),
    path('verifytoken', views.IdentityVerifyTokenView.as_view(), name='identity-verifytoken'),
    path('verifyphonenumber', views.IdentityVerifyPhoneNumberView.as_view(), name='identity-verifyphonenumber'),  # GET method
    
    # EMAIL CONFIRMATION ENDPOINTS
    path('sendconfirmemail', views.IdentitySendConfirmEmailView.as_view(), name='identity-send-confirm-email'),
    path('confirm-email-by-admin', views.IdentityConfirmEmailByAdminView.as_view(), name='identity-confirm-email-by-admin'),
    path('confirm-email', views.IdentityConfirmEmailView.as_view(), name='identity-confirm-email'),
    path('confirm-email-by-code', views.IdentityConfirmEmailByCodeView.as_view(), name='identity-confirm-email-by-code'),
    path('verify-email-by-code', views.IdentityVerifyEmailByCodeView.as_view(), name='identity-verify-email-by-code'),
    path('confirm-email-code-registerd', views.IdentityConfirmEmailCodeRegisteredView.as_view(), name='identity-confirm-email-code-registered'),
    
    # PHONE NUMBER CONFIRMATION ENDPOINTS
    path('confirm-phone-number', views.IdentityConfirmPhoneNumberView.as_view(), name='identity-confirm-phone-number'),
    path('confirm-phone-number-by-admin', views.IdentityConfirmPhoneNumberByAdminView.as_view(), name='identity-confirm-phone-number-by-admin'),
    
    # PASSWORD RESET ENDPOINTS
    path('forgot-password', views.IdentityForgotPasswordView.as_view(), name='identity-forgot-password'),
    path('forgot-password-by-code', views.IdentityForgotPasswordByCodeView.as_view(), name='identity-forgot-password-by-code'),
    path('reset-password', views.IdentityResetPasswordView.as_view(), name='identity-reset-password'),
    path('check-reset-password-code', views.IdentityCheckResetPasswordCodeView.as_view(), name='identity-check-reset-password-code'),
    path('reset-password-by-code', views.IdentityResetPasswordByCodeView.as_view(), name='identity-reset-password-by-code'),
    
    # CODE SENDING ENDPOINTS
    path('send-code', views.IdentitySendCodeView.as_view(), name='identity-send-code'),
    path('send-code-representative/<str:phoneNumber>/<str:RepresentativeCode>', views.IdentitySendCodeRepresentativeView.as_view(), name='identity-send-code-representative'),
    
    # TEST ENDPOINTS
    path('test-email/<str:email>', views.IdentityTestEmailView.as_view(), name='identity-test-email'),
]

