from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta
import random
import string

from .models import VerificationCode
from .serializers import (
    VerificationCodeSerializer,
    SendCodeRequestSerializer,
    VerifyCodeRequestSerializer,
    LoginRequestSerializer,
    RegisterRequestSerializer,
    ForgotPasswordRequestSerializer,
    ResetPasswordRequestSerializer,
)
from .models import User
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


@extend_schema(tags=['Auth'])
class VerificationCodeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing verification codes"""
    queryset = VerificationCode.objects.all()
    serializer_class = VerificationCodeSerializer
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Auth'])
class SendCodeView(APIView):
    """Send verification code to phone number"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=SendCodeRequestSerializer,
        examples=[
            OpenApiExample(
                'Send verification code',
                value={
                    'phone_number': '+989121234567'
                }
            )
        ],
        responses={
            200: {
                'description': 'Verification code sent successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'success': {
                                'summary': 'Code sent',
                                'value': {
                                    'message': 'Verification code sent successfully',
                                    'code': '123456'  # Remove in production
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'example': {
                            'error': 'Phone number is required'
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {'error': 'Phone number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Set expiration time (5 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=5)
        
        # Create or update verification code
        verification_code, created = VerificationCode.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                'code': code,
                'is_used': False,
                'expires_at': expires_at
            }
        )
        
        # TODO: Send SMS using SMS service
        # For now, we'll just return the code (remove this in production)
        
        return Response({
            'message': 'Verification code sent successfully',
            'code': code  # Remove this in production
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Auth'])
class VerifyCodeView(APIView):
    """Verify phone number with code"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyCodeRequestSerializer,
        examples=[
            OpenApiExample(
                'Verify code',
                value={
                    'phone_number': '+989121234567',
                    'code': '123456'
                }
            )
        ],
        responses={
            200: {
                'description': 'Code verified successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Code verified successfully'
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'examples': {
                            'missing_fields': {
                                'summary': 'Missing fields',
                                'value': {
                                    'error': 'Phone number and code are required'
                                }
                            },
                            'invalid_code': {
                                'summary': 'Invalid code',
                                'value': {
                                    'error': 'Invalid or expired code'
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        
        if not phone_number or not code:
            return Response(
                {'error': 'Phone number and code are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            verification_code = VerificationCode.objects.get(
                phone_number=phone_number,
                code=code
            )
            
            if not verification_code.is_valid():
                return Response(
                    {'error': 'Invalid or expired code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Don't mark code as used here - it will be marked as used in register/login
            # This allows the flow: send-code -> verify-code -> register/login
            
            return Response({
                'message': 'Code verified successfully'
            }, status=status.HTTP_200_OK)
            
        except VerificationCode.DoesNotExist:
            return Response(
                {'error': 'Invalid code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Auth'])
class LoginView(APIView):
    """Login with phone number and verification code"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginRequestSerializer,
        examples=[
            OpenApiExample(
                'Login with phone and code',
                value={
                    'phone_number': '+989121234567',
                    'code': '123456'
                }
            )
        ],
        responses={
            200: {
                'description': 'Login successful',
                'content': {
                    'application/json': {
                        'examples': {
                            'success': {
                                'summary': 'Login successful',
                                'value': {
                                    'token': 'abc123def456ghi789jkl012mno345pqr678stu901vwx234yz',
                                    'user': {
                                        'id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                        'phone_number': '+989121234567',
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'is_active': True,
                                        'email_confirmed': True
                                    },
                                    'message': 'Login successful'
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'examples': {
                            'missing_fields': {
                                'summary': 'Missing fields',
                                'value': {
                                    'error': 'Phone number and code are required'
                                }
                            },
                            'invalid_code': {
                                'summary': 'Invalid code',
                                'value': {
                                    'error': 'Invalid or expired code'
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        
        if not phone_number or not code:
            return Response(
                {'error': 'Phone number and code are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            verification_code = VerificationCode.objects.get(
                phone_number=phone_number,
                code=code
            )
            
            if not verification_code.is_valid():
                return Response(
                    {'error': 'Invalid or expired code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark code as used (single-use security)
            verification_code.is_used = True
            verification_code.save()
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'username': phone_number,
                    'is_active': True,
                    'email_confirmed': True
                }
            )
            
            if created:
                user.is_active = True
                user.email_confirmed = True
                user.save()
            
            # Generate token (you might want to use JWT here)
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': str(user.id),
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'email_confirmed': user.email_confirmed,
                },
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            
        except VerificationCode.DoesNotExist:
            return Response(
                {'error': 'Invalid code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Auth'])
class RegisterView(APIView):
    """Register new user with verification code"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterRequestSerializer,
        examples=[
            OpenApiExample(
                'Register new user',
                value={
                    'phone_number': '+989121234567',
                    'code': '123456',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com'
                }
            ),
            OpenApiExample(
                'Register with minimal fields',
                value={
                    'phone_number': '+989121234567',
                    'code': '123456'
                }
            )
        ],
        responses={
            201: {
                'description': 'Registration successful',
                'content': {
                    'application/json': {
                        'examples': {
                            'success': {
                                'summary': 'Registration successful',
                                'value': {
                                    'token': 'abc123def456ghi789jkl012mno345pqr678stu901vwx234yz',
                                    'user': {
                                        'id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                        'phone_number': '+989121234567',
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'is_active': True,
                                        'email_confirmed': True
                                    },
                                    'message': 'Registration successful'
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'examples': {
                            'missing_fields': {
                                'summary': 'Missing fields',
                                'value': {
                                    'error': 'Phone number and code are required'
                                }
                            },
                            'user_exists': {
                                'summary': 'User already exists',
                                'value': {
                                    'error': 'User with this phone number already exists'
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', '')
        
        if not phone_number or not code:
            return Response(
                {'error': 'Phone number and code are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            verification_code = VerificationCode.objects.get(
                phone_number=phone_number,
                code=code
            )
            
            if not verification_code.is_valid():
                return Response(
                    {'error': 'Invalid or expired code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already exists
            if User.objects.filter(phone_number=phone_number).exists():
                return Response(
                    {'error': 'User with this phone number already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark code as used
            verification_code.is_used = True
            verification_code.save()
            
            # Create user
            user = User.objects.create_user(
                phone_number=phone_number,
                username=phone_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_active=True,
                email_confirmed=True
            )
            
            # Handle referral code if provided
            referral_code = request.data.get('referral_code', '').strip()
            if referral_code:
                try:
                    from zistino_apps.points.models import ReferralCode, Referral
                    # Find referrer by code
                    referrer_code_obj = ReferralCode.objects.filter(code=referral_code).first()
                    if referrer_code_obj and referrer_code_obj.user != user:
                        # Create referral record (pending until first order)
                        Referral.objects.get_or_create(
                            referrer=referrer_code_obj.user,
                            referred=user,
                            defaults={
                                'referral_code': referral_code,
                                'status': 'pending'
                            }
                        )
                except Exception as e:
                    # Log error but don't fail registration
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to process referral code {referral_code} for user {user.id}: {str(e)}")
            
            # Generate token
            from rest_framework.authtoken.models import Token
            token = Token.objects.create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': str(user.id),
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'email_confirmed': user.email_confirmed,
                },
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
        except VerificationCode.DoesNotExist:
            return Response(
                {'error': 'Invalid code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['Auth'])
class LogoutView(APIView):
    """Logout user"""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(description='Logout successful')})
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Auth'])
class ForgotPasswordView(APIView):
    """Send password reset code"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=ForgotPasswordRequestSerializer,
        responses={200: OpenApiResponse(description='Reset code sent')}
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {'error': 'Phone number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone_number=phone_number)
            
            # Generate reset code
            code = ''.join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Create verification code for password reset
            VerificationCode.objects.create(
                phone_number=phone_number,
                code=code,
                expires_at=expires_at
            )
            
            # TODO: Send SMS
            return Response({
                'message': 'Password reset code sent successfully',
                'code': code  # Remove this in production
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this phone number does not exist'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Auth'])
class ResetPasswordView(APIView):
    """Reset password with verification code"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResetPasswordRequestSerializer,
        responses={200: OpenApiResponse(description='Password reset successful')}
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not phone_number or not code or not new_password:
            return Response(
                {'error': 'Phone number, code, and new password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            verification_code = VerificationCode.objects.get(
                phone_number=phone_number,
                code=code
            )
            
            if not verification_code.is_valid():
                return Response(
                    {'error': 'Invalid or expired code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = User.objects.get(phone_number=phone_number)
            user.set_password(new_password)
            user.save()
            
            # Mark code as used
            verification_code.is_used = True
            verification_code.save()
            
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
            
        except (VerificationCode.DoesNotExist, User.DoesNotExist):
            return Response(
                {'error': 'Invalid code or user not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
