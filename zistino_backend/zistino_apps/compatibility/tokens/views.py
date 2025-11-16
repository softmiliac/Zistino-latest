"""
Views for Tokens compatibility layer.
Matches old Swagger format exactly with response wrapper.
"""
import secrets
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    # Fallback: will use DRF Token instead

from zistino_apps.authentication.models import User, VerificationCode
from zistino_apps.compatibility.utils import (
    create_success_response,
    create_error_response,
    generate_refresh_token,
    calculate_refresh_token_expiry
)
from .models import RefreshToken
from .serializers import (
    CredentialsSerializer,
    TokenByEmailSerializer,
    ExternalLoginSerializer,
    TokenWithPermissionsSerializer,
    TokenByCodeSerializer,
    TokenByCodeConfirmationSerializer,
    RefreshTokenRequestSerializer,
    TokenResponseSerializer,
)


# JWT Secret Key (should be in settings, but using default for now)
JWT_SECRET_KEY = getattr(settings, 'SECRET_KEY', 'django-insecure-change-this-in-production')
JWT_ALGORITHM = 'HS256'


def generate_jwt_token(user, tenant='root'):
    """
    Generate a JWT token for the user.
    If PyJWT is not installed, falls back to DRF Token.
    """
    if JWT_AVAILABLE:
        # Get user roles (simplified - adjust based on your role system)
        roles = []
        if user.is_superuser:
            roles.append('Admin')
        if user.is_staff:
            roles.append('Manager')
        if user.is_driver:
            roles.append('Driver')
        
        # Get IP address from request if available
        ip_address = getattr(user, '_last_login_ip', '0.0.0.0')
        
        # Create JWT payload matching old Swagger format
        payload = {
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier': str(user.id),
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': user.email or '',
            'fullName': f"{user.first_name} {user.last_name}".strip() or user.username,
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': user.email or user.username,
            'ipAddress': ip_address,
            'tenant': tenant,
            'roles': str(roles),
            'cid': '0',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/mobilephone': user.phone_number or '',
            'exp': int((timezone.now() + timedelta(days=7)).timestamp())  # 7 days expiry
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    else:
        # Fallback: Use DRF Token (simpler, but not JWT format)
        # Note: Install PyJWT for JWT tokens: pip install PyJWT
        from rest_framework.authtoken.models import Token
        token_obj, created = Token.objects.get_or_create(user=user)
        return token_obj.key


@extend_schema(tags=['Tokens'])
class TokensViewSet(viewsets.ViewSet):
    """
    ViewSet for Tokens endpoints.
    POST /api/v1/tokens - Submit Credentials with Tenant Key to generate valid Access Token.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_create',
        summary='Submit Credentials with Tenant Key to generate valid Access Token',
        request=CredentialsSerializer,
        responses={
            200: TokenResponseSerializer,
            400: {'description': 'Bad Request'},
            401: {'description': 'Unauthorized'}
        },
    )
    def create(self, request):
        """
        POST /api/v1/tokens
        Request: { "email": "...", "password": "..." }
        Header: tenant: root
        Response: { "data": { "token": "...", "refreshToken": "...", "refreshTokenExpiryTime": "..." }, "messages": [], "succeeded": true }
        """
        # Get tenant from header (required in old Swagger)
        tenant = request.headers.get('tenant', 'root')
        
        serializer = CredentialsSerializer(data=request.data)
        if not serializer.is_valid():
            # Return 400 error in old Swagger format
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate user by email
        # Since USERNAME_FIELD is phone_number, we need to find user by email first
        # then authenticate using phone_number
        try:
            user_obj = User.objects.get(email=email)
            # Authenticate using phone_number (USERNAME_FIELD) and password
            user = authenticate(request, username=user_obj.phone_number, password=password)
            
            # If authenticate returns None, try checking password directly
            # (in case user exists but authentication fails for other reasons)
            if user is None and user_obj.check_password(password):
                user = user_obj
        except User.DoesNotExist:
            user = None
        except Exception as e:
            # Log error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Authentication error: {e}")
            user = None
        
        if user is None:
            return create_error_response(
                error_message='Invalid email or password',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is active
        if not user.is_active:
            return create_error_response(
                error_message='User account is inactive',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT token
        try:
            jwt_token = generate_jwt_token(user, tenant)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JWT token generation error: {e}")
            return create_error_response(
                error_message=f'Token generation failed: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create refresh token
        try:
            refresh_token_obj = RefreshToken.create_for_user(user)
            refresh_token_expiry = refresh_token_obj.expires_at
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Refresh token creation error: {e}")
            return create_error_response(
                error_message=f'Refresh token creation failed: {str(e)}. Please run migrations: python manage.py migrate',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return response in old Swagger format
        return create_success_response(
            data={
                'token': jwt_token,
                'refreshToken': refresh_token_obj.token,
                'refreshTokenExpiryTime': refresh_token_expiry.isoformat() + 'Z'
            }
        )


@extend_schema(tags=['Tokens'])
class TokensByEmailView(APIView):
    """POST /api/v1/tokens/tokenbyemail - Submit Credentials with Tenant Key to generate valid Access Token (by email)."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_by_email',
        summary='Submit Credentials with Tenant Key to generate valid Access Token (by email)',
        request=TokenByEmailSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        tenant = request.headers.get('tenant', 'root')
        serializer = TokenByEmailSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user_obj = User.objects.get(email=email)
            # Authenticate using phone_number (USERNAME_FIELD) and password
            user = authenticate(request, username=user_obj.phone_number, password=password)
            
            # If authenticate returns None, try checking password directly
            if user is None and user_obj.check_password(password):
                user = user_obj
        except User.DoesNotExist:
            user = None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Authentication error: {e}")
            user = None
        
        if user is None:
            return create_error_response(
                error_message='Invalid email or password',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return create_error_response(
                error_message='User account is inactive',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        jwt_token = generate_jwt_token(user, tenant)
        refresh_token_obj = RefreshToken.create_for_user(user)
        
        return create_success_response(
            data={
                'token': jwt_token,
                'refreshToken': refresh_token_obj.token,
                'refreshTokenExpiryTime': refresh_token_obj.expires_at.isoformat() + 'Z'
            }
        )


@extend_schema(tags=['Tokens'])
class TokensExternalLoginView(APIView):
    """POST /api/v1/tokens/externallogin - Submit External Login Credentials with Tenant Key to generate valid Access Token."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_external_login',
        summary='Submit External Login Credentials with Tenant Key to generate valid Access Token',
        request=ExternalLoginSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        # TODO: Implement actual external login logic (verify external_token with provider)
        return create_error_response(
            error_message='External login not implemented yet',
            status_code=status.HTTP_501_NOT_IMPLEMENTED
        )


@extend_schema(tags=['Tokens'])
class TokensWithPermissionsView(APIView):
    """POST /api/v1/tokens/token-with-permissions - Submit Credentials with Tenant Key to generate valid Access Token and user permissions."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_with_permissions',
        summary='Submit Credentials with Tenant Key to generate valid Access Token and user permissions',
        request=TokenWithPermissionsSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        tenant = request.headers.get('tenant', 'root')
        serializer = TokenWithPermissionsSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data['password']
        
        user = None
        if username:
            # Try username as phone_number first (since USERNAME_FIELD is phone_number)
            user = authenticate(request, username=username, password=password)
            # If that fails, try finding by username field
            if user is None:
                try:
                    user_obj = User.objects.get(username=username)
                    if user_obj.check_password(password):
                        user = user_obj
                except User.DoesNotExist:
                    pass
        elif email:
            try:
                user_obj = User.objects.get(email=email)
                # Authenticate using phone_number (USERNAME_FIELD)
                user = authenticate(request, username=user_obj.phone_number, password=password)
                # If authenticate returns None, try checking password directly
                if user is None and user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        if user is None:
            return create_error_response(
                error_message='Invalid credentials',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return create_error_response(
                error_message='User account is inactive',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        jwt_token = generate_jwt_token(user, tenant)
        refresh_token_obj = RefreshToken.create_for_user(user)
        
        # Get user permissions
        permissions = list(user.user_permissions.values_list('codename', flat=True))
        for group in user.groups.all():
            permissions.extend(group.permissions.values_list('codename', flat=True))
        
        return create_success_response(
            data={
                'token': jwt_token,
                'refreshToken': refresh_token_obj.token,
                'refreshTokenExpiryTime': refresh_token_obj.expires_at.isoformat() + 'Z',
                'permissions': permissions
            }
        )


@extend_schema(tags=['Tokens'])
class TokensByCodeView(APIView):
    """POST /api/v1/tokens/token-by-code - Submit Code with Tenant Key to generate valid Access Token."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_by_code',
        summary='Submit Code with Tenant Key to generate valid Access Token',
        request=TokenByCodeSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        tenant = request.headers.get('tenant', 'root')
        serializer = TokenByCodeSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        code = serializer.validated_data['code']
        phone_number = serializer.validated_data['phonenumber']  # Match old Swagger field name
        token = serializer.validated_data.get('token', '')  # Optional token field
        
        try:
            verification_code = VerificationCode.objects.get(
                phone_number=phone_number,
                code=code
            )
            
            if not verification_code.is_valid():
                return create_error_response(
                    error_message='Invalid or expired code',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            verification_code.is_used = True
            verification_code.save()
            
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'username': phone_number,
                    'is_active': True,
                    'email_confirmed': True
                }
            )
            
            jwt_token = generate_jwt_token(user, tenant)
            refresh_token_obj = RefreshToken.create_for_user(user)
            
            return create_success_response(
                data={
                    'token': jwt_token,
                    'refreshToken': refresh_token_obj.token,
                    'refreshTokenExpiryTime': refresh_token_obj.expires_at.isoformat() + 'Z'
                }
            )
            
        except VerificationCode.DoesNotExist:
            return create_error_response(
                error_message='Invalid code',
                status_code=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['Tokens'])
class TokensByCodeConfirmationView(APIView):
    """POST /api/v1/tokens/token-by-code-confirmation - Confirm Code with Tenant Key to generate valid Access Token."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_by_code_confirmation',
        summary='Confirm Code with Tenant Key to generate valid Access Token',
        request=TokenByCodeConfirmationSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        tenant = request.headers.get('tenant', 'root')
        serializer = TokenByCodeConfirmationSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        code = serializer.validated_data['code']
        phone_number = serializer.validated_data['phonenumber']  # Match token-by-code format
        token = serializer.validated_data.get('token', '')  # Optional token field
        
        try:
            verification_code = VerificationCode.objects.get(
                phone_number=phone_number,
                code=code
            )
            
            if not verification_code.is_valid():
                return create_error_response(
                    error_message='Invalid or expired code',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            verification_code.is_used = True
            verification_code.save()
            
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'username': phone_number,
                    'is_active': True,
                    'email_confirmed': True
                }
            )
            
            jwt_token = generate_jwt_token(user, tenant)
            refresh_token_obj = RefreshToken.create_for_user(user)
            
            return create_success_response(
                data={
                    'token': jwt_token,
                    'refreshToken': refresh_token_obj.token,
                    'refreshTokenExpiryTime': refresh_token_obj.expires_at.isoformat() + 'Z'
                }
            )
            
        except VerificationCode.DoesNotExist:
            return create_error_response(
                error_message='Invalid code',
                status_code=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['Tokens'])
class TokensRefreshView(APIView):
    """POST /api/v1/tokens/refresh - Refresh Access Token."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Tokens'],
        operation_id='tokens_refresh',
        summary='Refresh Access Token',
        request=RefreshTokenRequestSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        tenant = request.headers.get('tenant', 'root')
        serializer = RefreshTokenRequestSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        token = serializer.validated_data['token']  # Current access token (may be used for validation)
        refresh_token = serializer.validated_data['refreshToken']
        
        try:
            refresh_token_obj = RefreshToken.objects.get(token=refresh_token)
            
            if not refresh_token_obj.is_valid():
                return create_error_response(
                    error_message='Invalid or expired refresh token',
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            user = refresh_token_obj.user
            
            # Revoke old refresh token
            refresh_token_obj.is_revoked = True
            refresh_token_obj.save()
            
            # Generate new tokens
            jwt_token = generate_jwt_token(user, tenant)
            new_refresh_token_obj = RefreshToken.create_for_user(user)
            
            return create_success_response(
                data={
                    'token': jwt_token,
                    'refreshToken': new_refresh_token_obj.token,
                    'refreshTokenExpiryTime': new_refresh_token_obj.expires_at.isoformat() + 'Z'
                }
            )
            
        except RefreshToken.DoesNotExist:
            return create_error_response(
                error_message='Invalid refresh token',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
