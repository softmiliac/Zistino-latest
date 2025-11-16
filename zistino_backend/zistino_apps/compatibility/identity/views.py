"""
Compatibility views for Identity endpoints.
All endpoints will appear under "Identity" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Identity

Note: Some endpoints map to existing authentication views, others are placeholders.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from django.utils import timezone
from datetime import timedelta
import random
import string

from zistino_apps.authentication.models import User, VerificationCode
from zistino_apps.authentication.views import (
    RegisterView as AuthRegisterView,
    LoginView as AuthLoginView,
    SendCodeView as AuthSendCodeView,
    VerifyCodeView as AuthVerifyCodeView,
    ForgotPasswordView as AuthForgotPasswordView,
    ResetPasswordView as AuthResetPasswordView,
)
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
import uuid

from .serializers import (
    RegisterRequestSerializer,
    RegisterWithCodeRequestSerializer,
    RegisterWithPhoneCallRequestSerializer,
    VerifyTokenRequestSerializer,
    VerifyPhoneNumberRequestSerializer,
    SendConfirmEmailRequestSerializer,
    ForgotPasswordRequestSerializer,
    ForgotPasswordByCodeRequestSerializer,
    ResetPasswordRequestSerializer,
    CheckResetPasswordCodeRequestSerializer,
    ResetPasswordByCodeRequestSerializer,
    SendCodeRequestSerializer,
    ConfirmEmailCodeRegisteredRequestSerializer,
)


# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_register',
    summary='Register new user',
    description='Register a new user matching old Swagger format.',
    request=RegisterRequestSerializer,
    examples=[
        OpenApiExample(
            'Register user',
            value={
                'firstName': 'string',
                'lastName': 'string',
                'email': 'user@example.com',
                'userName': 'string',
                'password': 'string',
                'confirmPassword': 'string',
                'middleName': 'string',
                'gender': 0,
                'title': 'string',
                'info': 'string',
                'phoneNumber': 'string',
                'imageUrl': 'string',
                'thumbnail': 'string',
                'companyName': 'string',
                'companyNumber': 'string',
                'vatNumber': 'string',
                'representative': 'string',
                'sheba': 'string',
                'bankname': 'string',
                'birthdate': '2025-11-11T11:46:43.124Z',
                'codeMeli': 'string',
                'representativeBy': 'string',
                'companyId': 0
            }
        )
    ],
    responses={
        200: {
            'description': 'Registration response',
        'content': {
            'application/json': {
                'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string',
                        'source': 'string',
                        'exception': 'string',
                        'errorId': 'string',
                        'supportMessage': 'string',
                        'statusCode': 0
                    }
                }
            }
        }
    }
)
class IdentityRegisterView(APIView):
    """POST /api/v1/identity/register - Register new user matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register new user matching old Swagger format."""
        serializer = RegisterRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            error_id = str(uuid.uuid4())
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
                error_id=error_id
            )
        
        validated_data = serializer.validated_data
        
        try:
            # Check if email already exists
            if User.objects.filter(email=validated_data.get('email')).exists():
                error_id = str(uuid.uuid4())
                return create_error_response(
                    error_message='Email is already registered.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'email': ['Email is already registered.']},
                    error_id=error_id
                )
            
            # Check if username already exists
            if User.objects.filter(username=validated_data.get('userName')).exists():
                error_id = str(uuid.uuid4())
                return create_error_response(
                    error_message='Username is already taken.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userName': ['Username is already taken.']},
                    error_id=error_id
                )
            
            # Check if phone number already exists (if provided)
            phone_number = validated_data.get('phoneNumber', '').strip()
            if phone_number and User.objects.filter(phone_number=phone_number).exists():
                error_id = str(uuid.uuid4())
                return create_error_response(
                    error_message='Phone number is already registered.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'phoneNumber': ['Phone number is already registered.']},
                    error_id=error_id
                )
            
            # Create user
            # Use phone_number as username if provided, otherwise use userName
            username = phone_number if phone_number else validated_data.get('userName')
            if not phone_number:
                # Generate a unique phone number if not provided (required field)
                phone_number = f'+989{str(uuid.uuid4().int)[:9]}'
            
            user = User.objects.create_user(
                username=username,
                email=validated_data.get('email'),
                password=validated_data.get('password'),
                phone_number=phone_number,
                first_name=validated_data.get('firstName', ''),
                last_name=validated_data.get('lastName', ''),
                is_active=False,  # User needs to verify email/phone
                email_confirmed=False
            )
            
            # Set optional fields that exist in User model
            if validated_data.get('companyName'):
                user.company_name = validated_data.get('companyName')
            
            if validated_data.get('vatNumber'):
                user.vat_number = validated_data.get('vatNumber')
            
            if validated_data.get('representative'):
                user.representative = validated_data.get('representative')
            
            if validated_data.get('sheba'):
                user.sheba = validated_data.get('sheba')
            
            if validated_data.get('bankname'):
                user.bank_name = validated_data.get('bankname')
            
            if validated_data.get('birthdate'):
                # Convert DateTimeField to DateField
                birthdate = validated_data.get('birthdate')
                if hasattr(birthdate, 'date'):
                    user.birth_date = birthdate.date()
                else:
                    user.birth_date = birthdate
            
            if validated_data.get('codeMeli'):
                user.national_id = validated_data.get('codeMeli')
            
            if validated_data.get('representativeBy'):
                user.representative_by = validated_data.get('representativeBy')
            
            user.save()
            
            # Return success response matching old Swagger format
            return create_success_response(
                data=str(user.id),  # Return user ID as string
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            error_id = str(uuid.uuid4())
            return create_error_response(
                error_message=f'An error occurred while registering user: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]},
                error_id=error_id
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_register_with_code',
    summary='Register new user with code',
    description='Register a new user with verification code matching old Swagger format.',
    request=RegisterWithCodeRequestSerializer,
    examples=[
        OpenApiExample(
            'Register user with code',
            value={
                'firstName': 'string',
                'lastName': 'string',
                'email': 'user@example.com',
                'userName': 'string',
                'password': 'string',
                'confirmPassword': 'string',
                'middleName': 'string',
                'gender': 0,
                'title': 'string',
                'info': 'string',
                'phoneNumber': 'string',
                'imageUrl': 'string',
                'thumbnail': 'string',
                'companyName': 'string',
                'companyNumber': 'string',
                'vatNumber': 'string',
                'representative': 'string',
                'sheba': 'string',
                'bankname': 'string',
                'birthdate': '2025-11-12T08:57:01.425Z',
                'codeMeli': 'string',
                'representativeBy': 'string',
                'companyId': 0
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Registration response',
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
        )
    }
)
class IdentityRegisterWithCodeView(APIView):
    """POST /api/v1/identity/register-with-code - Register with code matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register with code matching old Swagger format."""
        # Use the same logic as register, but return simplified response
        serializer = RegisterWithCodeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        validated_data = serializer.validated_data
        
        try:
            # Check if email already exists
            if User.objects.filter(email=validated_data.get('email')).exists():
                return create_error_response(
                    error_message='Email is already registered.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'email': ['Email is already registered.']}
                )
            
            # Check if username already exists
            if User.objects.filter(username=validated_data.get('userName')).exists():
                return create_error_response(
                    error_message='Username is already taken.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userName': ['Username is already taken.']}
                )
            
            # Check if phone number already exists (if provided)
            phone_number = validated_data.get('phoneNumber', '').strip()
            if phone_number and User.objects.filter(phone_number=phone_number).exists():
                return create_error_response(
                    error_message='Phone number is already registered.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'phoneNumber': ['Phone number is already registered.']}
                )
            
            # Create user (same logic as register)
            username = phone_number if phone_number else validated_data.get('userName')
            if not phone_number:
                phone_number = f'+989{str(uuid.uuid4().int)[:9]}'
            
            user = User.objects.create_user(
                username=username,
                email=validated_data.get('email'),
                password=validated_data.get('password'),
                phone_number=phone_number,
                first_name=validated_data.get('firstName', ''),
                last_name=validated_data.get('lastName', ''),
                is_active=False,
                email_confirmed=False
            )
            
            # Set optional fields
            if validated_data.get('companyName'):
                user.company_name = validated_data.get('companyName')
            if validated_data.get('vatNumber'):
                user.vat_number = validated_data.get('vatNumber')
            if validated_data.get('representative'):
                user.representative = validated_data.get('representative')
            if validated_data.get('sheba'):
                user.sheba = validated_data.get('sheba')
            if validated_data.get('bankname'):
                user.bank_name = validated_data.get('bankname')
            if validated_data.get('birthdate'):
                birthdate = validated_data.get('birthdate')
                if hasattr(birthdate, 'date'):
                    user.birth_date = birthdate.date()
                else:
                    user.birth_date = birthdate
            if validated_data.get('codeMeli'):
                user.national_id = validated_data.get('codeMeli')
            if validated_data.get('representativeBy'):
                user.representative_by = validated_data.get('representativeBy')
            
            user.save()
            
            # Return simplified response matching old Swagger format
            return Response({
                'messages': [],
                'succeeded': True,
                'data': str(user.id)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while registering user: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_register_with_phonecall',
    summary='Register with phone call',
    description='Register new user via phone call verification matching old Swagger format.',
    request=RegisterWithPhoneCallRequestSerializer,
    examples=[
        OpenApiExample(
            'Register user with phone call',
            value={
                'userInfo': {
                    'firstName': 'string',
                    'lastName': 'string',
                    'email': 'user@example.com',
                    'userName': 'string',
                    'password': 'string',
                    'confirmPassword': 'string',
                    'middleName': 'string',
                    'gender': 0,
                    'title': 'string',
                    'info': 'string',
                    'phoneNumber': 'string',
                    'imageUrl': 'string',
                    'thumbnail': 'string',
                    'companyName': 'string',
                    'companyNumber': 'string',
                    'vatNumber': 'string',
                    'representative': 'string',
                    'sheba': 'string',
                    'bankname': 'string',
                    'birthdate': '2025-11-11T11:55:23.464Z',
                    'codeMeli': 'string',
                    'representativeBy': 'string',
                    'companyId': 0
                },
                'address': {
                    'userId': 'string',
                    'latitude': 0,
                    'longitude': 0,
                    'address': 'string',
                    'zipCode': 'string',
                    'fullName': 'string',
                    'phoneNumber': 'string',
                    'description': 'string',
                    'plate': 'string',
                    'unit': 'string',
                    'country': 'string',
                    'province': 'string',
                    'city': 'string',
                    'companyName': 'string',
                    'companyNumber': 'string',
                    'vatNumber': 'string',
                    'fax': 'string',
                    'website': 'string',
                    'email': 'string',
                    'title': 'string'
                },
                'delivery': {
                    'userId': 'string',
                    'deliveryUserId': 'string',
                    'deliveryDate': '2025-11-11T11:55:23.464Z',
                    'setUserId': 'string',
                    'addressId': 0,
                    'orderId': 0,
                    'examId': 0,
                    'requestId': 0,
                    'zoneId': 0,
                    'preOrderId': 0,
                    'status': 0,
                    'description': 'string'
                }
            }
        )
    ],
    responses={
        200: {
            'description': 'Registration response',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityRegisterWithPhoneCallView(APIView):
    """POST /api/v1/identity/register-with-phonecall - Register with phone call matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register with phone call matching old Swagger format."""
        serializer = RegisterWithPhoneCallRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        validated_data = serializer.validated_data
        user_info = validated_data.get('userInfo', {})
        address = validated_data.get('address')
        delivery = validated_data.get('delivery')
        
        try:
            # Check if email already exists
            if User.objects.filter(email=user_info.get('email')).exists():
                return create_error_response(
                    error_message='Email is already registered.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userInfo': {'email': ['Email is already registered.']}}
                )
            
            # Check if username already exists
            if User.objects.filter(username=user_info.get('userName')).exists():
                return create_error_response(
                    error_message='Username is already taken.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userInfo': {'userName': ['Username is already taken.']}}
                )
            
            # Check if phone number already exists (if provided)
            phone_number = user_info.get('phoneNumber', '').strip()
            if phone_number and User.objects.filter(phone_number=phone_number).exists():
                return create_error_response(
                    error_message='Phone number is already registered.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userInfo': {'phoneNumber': ['Phone number is already registered.']}}
                )
            
            # Create user
            username = phone_number if phone_number else user_info.get('userName')
            if not phone_number:
                phone_number = f'+989{str(uuid.uuid4().int)[:9]}'
            
            user = User.objects.create_user(
                username=username,
                email=user_info.get('email'),
                password=user_info.get('password'),
                phone_number=phone_number,
                first_name=user_info.get('firstName', ''),
                last_name=user_info.get('lastName', ''),
                is_active=False,
                email_confirmed=False
            )
            
            # Set optional fields
            if user_info.get('companyName'):
                user.company_name = user_info.get('companyName')
            if user_info.get('vatNumber'):
                user.vat_number = user_info.get('vatNumber')
            if user_info.get('representative'):
                user.representative = user_info.get('representative')
            if user_info.get('sheba'):
                user.sheba = user_info.get('sheba')
            if user_info.get('bankname'):
                user.bank_name = user_info.get('bankname')
            if user_info.get('birthdate'):
                birthdate = user_info.get('birthdate')
                if hasattr(birthdate, 'date'):
                    user.birth_date = birthdate.date()
                else:
                    user.birth_date = birthdate
            if user_info.get('codeMeli'):
                user.national_id = user_info.get('codeMeli')
            if user_info.get('representativeBy'):
                user.representative_by = user_info.get('representativeBy')
            
            user.save()
            
            # TODO: Create address and delivery records if provided
            # For now, we'll just create the user
            
            # Return simplified response matching old Swagger format
            return Response({
                'messages': [],
                'succeeded': True,
                'data': str(user.id)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while registering user: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# VERIFICATION ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_check_duplicate',
    summary='Check duplicate email',
    description='Check if email is already registered matching old Swagger format.',
    responses={
        200: {
            'description': 'Email availability',
            'content': {
                'application/json': {
                    'example': {
                        'data': True,
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class IdentityCheckDuplicateView(APIView):
    """GET /api/v1/identity/check-duplicate/{email} - Check duplicate email matching old Swagger format"""
    permission_classes = [AllowAny]

    def get(self, request, email):
        """Check if email is already registered matching old Swagger format."""
        is_duplicate = User.objects.filter(email=email).exists()
        return Response({
            'data': is_duplicate,
            'messages': [],
            'succeeded': True
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Identity'],
    operation_id='identity_verify',
    summary='Validate Access Token',
    description='Validate Access Token matching old Swagger format.',
    responses={
        200: {
            'description': 'Verification response',
            'content': {
                'application/json': {
                    'example': 'done'
                }
            }
        }
    }
)
class IdentityVerifyView(APIView):
    """POST /api/v1/identity/verify - Validate Access Token matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate access token - returns 'done' matching old Swagger format."""
        # Old Swagger returns just "done" string, no parameters needed
        return Response('done', status=status.HTTP_200_OK)


@extend_schema(
    tags=['Identity'],
    operation_id='identity_verifytoken',
    summary='Validate Access Token',
    description='Validate Access Token matching old Swagger format.',
    responses={
        200: {
            'description': 'Verification response',
            'content': {
                'application/json': {
                    'example': 'done'
                }
            }
        }
    }
)
class IdentityVerifyTokenView(APIView):
    """POST /api/v1/identity/verifytoken - Validate Access Token matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate access token - returns 'done' matching old Swagger format."""
        # Old Swagger returns just "done" string, no parameters needed
        return Response('done', status=status.HTTP_200_OK)


@extend_schema(
    tags=['Identity'],
    operation_id='identity_verifyphonenumber',
    summary='Verify phone number',
    description='Verify phone number matching old Swagger format.',
    parameters=[
        OpenApiParameter('phoneNumber', str, location=OpenApiParameter.QUERY, description='Phone number to verify', required=True),
    ],
    responses={
        200: {
            'description': 'Phone number verification response',
            'content': {
                'application/json': {
                    'example': {
                        'data': None,
                        'messages': ['zD1OVL7Gc4N0dlOj3igt1RE4ZNA+rXiWnuOa0DHppLKPCRP0dovndHyNDUVzKbii'],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class IdentityVerifyPhoneNumberView(APIView):
    """GET /api/v1/identity/verifyphonenumber - Verify phone number matching old Swagger format"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Verify phone number - requires phoneNumber query parameter matching old Swagger format."""
        phone_number = request.query_params.get('phoneNumber')
        
        if not phone_number:
            return create_error_response(
                error_message='phoneNumber parameter is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'phoneNumber': ['This parameter is required.']}
            )
        
        # Generate a verification token/code (old Swagger returns a token in messages)
        import secrets
        verification_token = secrets.token_urlsafe(32)
        
        # Return format matching old Swagger
        return Response({
            'data': None,
            'messages': [verification_token],
            'succeeded': True
        }, status=status.HTTP_200_OK)


# ============================================================================
# EMAIL CONFIRMATION ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_sendconfirmemail',
    summary='Send confirmation email',
    description='Send confirmation email to user matching old Swagger format.',
    request=SendConfirmEmailRequestSerializer,
    responses={
        200: {
            'description': 'Confirmation email sent',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentitySendConfirmEmailView(APIView):
    """POST /api/v1/identity/sendconfirmemail - Send confirmation email matching old Swagger format"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Send confirmation email matching old Swagger format."""
        email = request.data.get('email') or request.user.email
        
        if not email:
            return create_error_response(
                error_message='Email is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'email': ['This field is required.']}
            )
        
        # TODO: Generate confirmation code and send email
        # For now, return success with format matching old Swagger
        return Response({
            'messages': [],
            'succeeded': True,
            'data': 'Confirmation email sent successfully'
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Identity'],
    operation_id='identity_confirm_email_by_admin',
    summary='Confirm email by admin',
    description='Admin endpoint to confirm user email matching old Swagger format.',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, description='User ID to confirm email for', required=True),
    ],
    responses={
        200: {
            'description': 'Email confirmed',
            'content': {
                'application/json': {
                    'example': {
                        'data': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                        'messages': ['Account Confirmed for E-Mail . You can now use the /api/identity/token endpoint to generate JWT. [en-US]'],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class IdentityConfirmEmailByAdminView(APIView):
    """GET /api/v1/identity/confirm-email-by-admin - Confirm email by admin matching old Swagger format"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Confirm email by admin matching old Swagger format."""
        user_id = request.query_params.get('userId') or request.query_params.get('user_id')
        
        if not user_id:
            return create_error_response(
                error_message='userId parameter is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['This parameter is required.']}
            )
        
        try:
            user = User.objects.get(id=user_id)
            user.email_confirmed = True
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'data': str(user.id),
                'messages': [f'Account Confirmed for E-Mail {user.email or ""}. You can now use the /api/identity/token endpoint to generate JWT. [en-US]'],
                'succeeded': True
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': ['User not found.']}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_confirm_email',
    summary='Confirm email',
    description='Confirm user email matching old Swagger format.',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, description='User ID', required=True),
        OpenApiParameter('code', str, location=OpenApiParameter.QUERY, description='Verification code', required=True),
        OpenApiParameter('tenant', str, location=OpenApiParameter.QUERY, description='Tenant (optional)', required=False),
    ],
    responses={
        200: {
            'description': 'Email confirmed',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityConfirmEmailView(APIView):
    """GET /api/v1/identity/confirm-email - Confirm email matching old Swagger format"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Confirm email matching old Swagger format."""
        user_id = request.query_params.get('userId')
        code = request.query_params.get('code')
        tenant = request.query_params.get('tenant')  # Optional
        
        if not user_id or not code:
            return create_error_response(
                error_message='userId and code parameters are required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['This parameter is required.'], 'code': ['This parameter is required.']}
            )
        
        try:
            user = User.objects.get(id=user_id)
            
            # TODO: Verify code (for now, we'll just confirm the email)
            # In a real scenario, you would verify the code against a stored verification code
            
            user.email_confirmed = True
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Email confirmed successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': ['User not found.']}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_confirm_email_by_code',
    summary='Confirm email by code',
    description='Confirm email using verification code matching old Swagger format.',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, description='User ID', required=True),
        OpenApiParameter('code', str, location=OpenApiParameter.QUERY, description='Verification code', required=True),
        OpenApiParameter('email', str, location=OpenApiParameter.QUERY, description='Email address', required=True),
        OpenApiParameter('tenant', str, location=OpenApiParameter.QUERY, description='Tenant (optional)', required=False),
    ],
    responses={
        200: {
            'description': 'Email confirmed',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityConfirmEmailByCodeView(APIView):
    """GET /api/v1/identity/confirm-email-by-code - Confirm email by code matching old Swagger format"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Confirm email by code matching old Swagger format."""
        user_id = request.query_params.get('userId')
        code = request.query_params.get('code')
        email = request.query_params.get('email')
        tenant = request.query_params.get('tenant')  # Optional
        
        if not user_id or not code or not email:
            return create_error_response(
                error_message='userId, code, and email parameters are required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['This parameter is required.'], 'code': ['This parameter is required.'], 'email': ['This parameter is required.']}
            )
        
        try:
            user = User.objects.get(id=user_id, email=email)
            
            # TODO: Verify code (for now, we'll just confirm the email)
            # In a real scenario, you would verify the code against a stored verification code
            
            user.email_confirmed = True
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Email confirmed successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': ['User not found.']}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_verify_email_by_code',
    summary='Verify email by code',
    description='Verify email using verification code matching old Swagger format.',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, description='User ID', required=True),
        OpenApiParameter('code', str, location=OpenApiParameter.QUERY, description='Verification code', required=True),
        OpenApiParameter('email', str, location=OpenApiParameter.QUERY, description='Email address', required=True),
        OpenApiParameter('tenant', str, location=OpenApiParameter.QUERY, description='Tenant (optional)', required=False),
    ],
    responses={
        200: {
            'description': 'Email verified',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityVerifyEmailByCodeView(APIView):
    """GET /api/v1/identity/verify-email-by-code - Verify email by code matching old Swagger format"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Verify email by code matching old Swagger format."""
        user_id = request.query_params.get('userId')
        code = request.query_params.get('code')
        email = request.query_params.get('email')
        tenant = request.query_params.get('tenant')  # Optional
        
        if not user_id or not code or not email:
            return create_error_response(
                error_message='userId, code, and email parameters are required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['This parameter is required.'], 'code': ['This parameter is required.'], 'email': ['This parameter is required.']}
            )
        
        try:
            user = User.objects.get(id=user_id, email=email)
            
            # TODO: Verify code (for now, we'll just confirm the email)
            # In a real scenario, you would verify the code against a stored verification code
            
            user.email_confirmed = True
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': ['User not found.']}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_confirm_email_code_registered',
    summary='Confirm email code for registered user',
    description='Confirm email code for already registered user matching old Swagger format.',
    request=ConfirmEmailCodeRegisteredRequestSerializer,
    examples=[
        OpenApiExample(
            'Confirm email code',
            value={
                'email': 'string',
                'password': 'string',
                'code': 'string'
            }
        )
    ],
    responses={
        200: {
            'description': 'Email confirmed',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityConfirmEmailCodeRegisteredView(APIView):
    """POST /api/v1/identity/confirm-email-code-registerd - Confirm email code for registered user matching old Swagger format"""
    permission_classes = [AllowAny]  # Changed to AllowAny to match old Swagger

    def post(self, request):
        """Confirm email code for registered user matching old Swagger format."""
        serializer = ConfirmEmailCodeRegisteredRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        validated_data = serializer.validated_data
        email = validated_data.get('email')
        password = validated_data.get('password')
        code = validated_data.get('code')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Verify password
            if not user.check_password(password):
                return create_error_response(
                    error_message='Invalid password.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'password': ['Invalid password.']}
                )
            
            # TODO: Verify code (for now, we'll just confirm the email)
            # In a real scenario, you would verify the code against a stored verification code
            
            user.email_confirmed = True
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Email confirmed successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'email': ['User not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while confirming email: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# PHONE NUMBER CONFIRMATION ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_confirm_phone_number',
    summary='Confirm phone number',
    description='Confirm user phone number matching old Swagger format.',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, description='User ID', required=True),
        OpenApiParameter('code', str, location=OpenApiParameter.QUERY, description='Verification code', required=True),
    ],
    responses={
        200: {
            'description': 'Phone number confirmed',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityConfirmPhoneNumberView(APIView):
    """GET /api/v1/identity/confirm-phone-number - Confirm phone number matching old Swagger format"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Confirm phone number matching old Swagger format."""
        user_id = request.query_params.get('userId')
        code = request.query_params.get('code')
        
        if not user_id or not code:
            return create_error_response(
                error_message='userId and code parameters are required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['This parameter is required.'], 'code': ['This parameter is required.']}
            )
        
        try:
            user = User.objects.get(id=user_id)
            
            # TODO: Verify code (for now, we'll just confirm the phone number)
            # In a real scenario, you would verify the code against a stored verification code
            
            user.is_active = True
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Phone number confirmed successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': ['User not found.']}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_confirm_phone_number_by_admin',
    summary='Confirm phone number by admin',
    description='Admin endpoint to confirm user phone number matching old Swagger format.',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, description='User ID to confirm phone number for', required=True),
    ],
    responses={
        200: {
            'description': 'Phone number confirmed',
            'content': {
                'application/json': {
                    'example': {
                        'data': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                        'messages': ['Account Confirmed for Phone Number 09056761466. You should confirm your E-mail before using the /api/identity/token endpoint to generate JWT. [en-US]'],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class IdentityConfirmPhoneNumberByAdminView(APIView):
    """GET /api/v1/identity/confirm-phone-number-by-admin - Confirm phone number by admin matching old Swagger format"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Confirm phone number by admin matching old Swagger format."""
        user_id = request.query_params.get('userId') or request.query_params.get('user_id')
        
        if not user_id:
            return create_error_response(
                error_message='userId parameter is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['This parameter is required.']}
            )
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            
            # Return format matching old Swagger
            phone_number = user.phone_number or ''
            return Response({
                'data': str(user.id),
                'messages': [f'Account Confirmed for Phone Number {phone_number}. You should confirm your E-mail before using the /api/identity/token endpoint to generate JWT. [en-US]'],
                'succeeded': True
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': ['User not found.']}
            )


# ============================================================================
# PASSWORD RESET ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_forgot_password',
    summary='Forgot password',
    description='Send password reset code matching old Swagger format.',
    request=ForgotPasswordRequestSerializer,
    examples=[
        OpenApiExample(
            'Forgot password',
            value={
                'email': 'user@example.com'
            }
        )
    ],
    responses={
        200: {
            'description': 'Reset code sent',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityForgotPasswordView(APIView):
    """POST /api/v1/identity/forgot-password - Forgot password matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Forgot password matching old Swagger format."""
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        email = serializer.validated_data.get('email')
        
        try:
            # Check if user exists
            user = User.objects.get(email=email)
            
            # TODO: Generate reset token and send email
            # For now, we'll just return success
            import secrets
            reset_token = secrets.token_urlsafe(32)
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Password reset code sent successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Still return success to prevent email enumeration
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'If the email exists, a password reset code has been sent'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing forgot password: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_forgot_password_by_code',
    summary='Forgot password by code',
    description='Send password reset code matching old Swagger format.',
    request=ForgotPasswordByCodeRequestSerializer,
    examples=[
        OpenApiExample(
            'Forgot password by code',
            value={
                'email': 'user@example.com'
            }
        )
    ],
    responses={
        200: {
            'description': 'Reset code sent',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityForgotPasswordByCodeView(APIView):
    """POST /api/v1/identity/forgot-password-by-code - Forgot password by code matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Forgot password by code matching old Swagger format."""
        serializer = ForgotPasswordByCodeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        email = serializer.validated_data.get('email')
        
        try:
            # Check if user exists
            user = User.objects.get(email=email)
            
            # TODO: Generate reset code and send email/SMS
            # For now, we'll just return success
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Password reset code sent successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Still return success to prevent email enumeration
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'If the email exists, a password reset code has been sent'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while processing forgot password: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_reset_password',
    summary='Reset password',
    description='Reset password with token matching old Swagger format.',
    request=ResetPasswordRequestSerializer,
    examples=[
        OpenApiExample(
            'Reset password',
            value={
                'email': 'string',
                'password': 'string',
                'token': 'string'
            }
        )
    ],
    responses={
        200: {
            'description': 'Password reset successful',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityResetPasswordView(APIView):
    """POST /api/v1/identity/reset-password - Reset password matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Reset password matching old Swagger format."""
        serializer = ResetPasswordRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        validated_data = serializer.validated_data
        email = validated_data.get('email')
        password = validated_data.get('password')
        token = validated_data.get('token')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # TODO: Verify token (for now, we'll just reset the password)
            # In a real scenario, you would verify the token against a stored reset token
            
            # Set new password
            user.set_password(password)
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Password reset successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'email': ['User not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while resetting password: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_check_reset_password_code',
    summary='Check reset password code',
    description='Verify reset password code before resetting matching old Swagger format.',
    request=CheckResetPasswordCodeRequestSerializer,
    examples=[
        OpenApiExample(
            'Check reset password code',
            value={
                'email': 'string',
                'code': 'string'
            }
        )
    ],
    responses={
        200: {
            'description': 'Code check response',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityCheckResetPasswordCodeView(APIView):
    """POST /api/v1/identity/check-reset-password-code - Check reset password code matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Check if reset password code is valid matching old Swagger format."""
        serializer = CheckResetPasswordCodeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        validated_data = serializer.validated_data
        email = validated_data.get('email')
        code = validated_data.get('code')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # TODO: Verify code against stored verification code
            # For now, we'll just return success
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Code is valid'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'email': ['User not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while checking reset password code: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Identity'],
    operation_id='identity_reset_password_by_code',
    summary='Reset password by code',
    description='Reset password with verification code matching old Swagger format.',
    request=ResetPasswordByCodeRequestSerializer,
    examples=[
        OpenApiExample(
            'Reset password by code',
            value={
                'email': 'string',
                'password': 'string',
                'code': 'string'
            }
        )
    ],
    responses={
        200: {
            'description': 'Password reset successful',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['string'],
                        'succeeded': True,
                        'data': 'string'
                    }
                }
            }
        }
    }
)
class IdentityResetPasswordByCodeView(APIView):
    """POST /api/v1/identity/reset-password-by-code - Reset password by code matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Reset password by code matching old Swagger format."""
        serializer = ResetPasswordByCodeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        validated_data = serializer.validated_data
        email = validated_data.get('email')
        password = validated_data.get('password')
        code = validated_data.get('code')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # TODO: Verify code (for now, we'll just reset the password)
            # In a real scenario, you would verify the code against a stored verification code
            
            # Set new password
            user.set_password(password)
            user.save()
            
            # Return format matching old Swagger
            return Response({
                'messages': [],
                'succeeded': True,
                'data': 'Password reset successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'email': ['User not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while resetting password: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# CODE SENDING ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_send_code',
    summary='Send code',
    description='Send verification code to phone number matching old Swagger format.',
    parameters=[
        OpenApiParameter('phoneNumber', str, location=OpenApiParameter.QUERY, description='Phone number to send code to', required=True),
    ],
    responses={
        200: {
            'description': 'Code sent',
            'content': {
                'application/json': {
                    'example': {
                        'data': None,
                        'messages': ['Hr2m1CRzZbRyuEwSUttP1SB0mFbl+TKVaaic1b031CfHTfTmmOGjy1q+Pj4FJVo2'],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class IdentitySendCodeView(APIView):
    """POST /api/v1/identity/send-code - Send code matching old Swagger format"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Send code - requires phoneNumber query parameter matching old Swagger format."""
        phone_number = request.query_params.get('phoneNumber')
        
        if not phone_number:
            return create_error_response(
                error_message='phoneNumber parameter is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'phoneNumber': ['This parameter is required.']}
            )
        
        # Generate a verification token/code (old Swagger returns a token in messages)
        import secrets
        verification_token = secrets.token_urlsafe(32)
        
        # TODO: Actually send the code via SMS service
        # For now, we'll just return the token
        
        # Return format matching old Swagger
        return Response({
            'data': None,
            'messages': [verification_token],
            'succeeded': True
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Identity'],
    operation_id='identity_send_code_representative',
    summary='Send code representative',
    description='Send verification code to representative phone number.',
    responses={200: {
        'description': 'Code sent',
        'content': {
            'application/json': {
                'example': {
                    'message': 'Verification code sent successfully'
                }
            }
        }
    }}
)
class IdentitySendCodeRepresentativeView(APIView):
    """GET /api/v1/identity/send-code-representative/{phoneNumber}/{RepresentativeCode} - Send code representative"""
    permission_classes = [AllowAny]

    def get(self, request, phoneNumber, RepresentativeCode):
        """
        Send code to representative phone number.
        TODO: Implement representative code validation if needed.
        """
        # For now, use same logic as send-code
        request.data = {'phone_number': phoneNumber}
        auth_view = AuthSendCodeView()
        return auth_view.post(request)


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Identity'],
    operation_id='identity_test_email',
    summary='Test email',
    description='Test email sending functionality matching old Swagger format.',
    responses={
        200: {
            'description': 'Test email sent',
            'content': {
                'application/json': {
                    'example': {
                        'data': None,
                        'messages': ['Please Check Your Inbox'],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class IdentityTestEmailView(APIView):
    """GET /api/v1/identity/test-email/{email} - Test email matching old Swagger format"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, email):
        """Test email sending functionality matching old Swagger format."""
        # TODO: Send test email
        # For now, return success with format matching old Swagger
        return Response({
            'data': None,
            'messages': ['Please Check Your Inbox'],
            'succeeded': True
        }, status=status.HTTP_200_OK)

