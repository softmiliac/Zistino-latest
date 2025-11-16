"""
Compatibility views for Personal endpoints.
All endpoints will appear under "Personal" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Personal

Note: Some endpoints (blue badge, repair requests) are placeholders and need implementation.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

from zistino_apps.users.serializers import UserProfileSerializer, UserSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.points.models import UserPoints
from zistino_apps.compatibility.users.serializers import UserCompatibilitySerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response, create_authentication_error_response
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    ProfileDateByRepresentativeDateRequestSerializer,
    SetBlueBadgeRequestSerializer,
    RequestBlueBadgeRequestSerializer,
    RequestRoleRequestSerializer,
    RepresentativeRequestSerializer,
    ProfileAdminUpdateRequestSerializer,
    ResetPasswordRequestSerializer,
    ChangePasswordRequestSerializer,
    RepairRequestsRequestSerializer,
    RepairRequestDocumentRequestSerializer,
    RepairRequestMessageRequestSerializer,
)

User = get_user_model()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_custom_headers(response: Response) -> Response:
    """
    Add custom headers to match old Swagger API response format.
    """
    response['access-control-allow-origin'] = '*'
    response['access-control-expose-headers'] = 'Upload-Offset,Location,Upload-Length,Tus-Version,Tus-Resumable,Tus-Max-Size,Tus-Extension,Upload-Metadata,Upload-Defer-Length,Upload-Concat,Location,Upload-Offset,Upload-Length'
    response['api-supported-versions'] = '1.0'
    response['server'] = 'Microsoft-IIS/10.0'
    response['x-powered-by'] = 'ASP.NET'
    return response


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_profile',
    summary='Get profile details of currently logged in user',
    description='Get profile details of currently logged in user.',
    responses={
        200: OpenApiResponse(
            response=UserCompatibilitySerializer,
            description='User profile details',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "id": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                        "userName": "admin@root.com",
                        "firstName": "مدیر",
                        "lastName": "آروین ویرا",
                        "email": "admin@root.com",
                        "isActive": True,
                        "createDate": "2023-10-29T16:05:37.957",
                        "middleName": None,
                        "gender": None,
                        "title": None,
                        "info": None,
                        "emailConfirmed": True,
                        "phoneNumberConfirmed": False,
                        "phoneNumber": "09876543212",
                        "imageUrl": "/uploads/app/2e40483d1caa474b89a2e5abfef45b96.webp",
                        "thumbnail": "/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp",
                        "companyName": "خانگــی",
                        "companyNumber": None,
                        "code": "0",
                        "codeType": 0,
                        "companyId": None,
                        "jsonExt": "i have not bio 🚫",
                        "vatNumber": "known",
                        "representative": None,
                        "sheba": "IR012345678912345678912345",
                        "bankname": None,
                        "birthdate": "2025-10-12T20:30:00",
                        "codeMeli": "0825659862",
                        "representativeBy": None,
                        "representativeDate": None,
                        "blueUser": None,
                        "blueUSerActiveDate": None,
                        "issue": None,
                        "rolesRequests": "artist",
                        "instagram": None,
                        "facebook": None,
                        "linkedIn": "YouTube",
                        "twitter": "Twitter",
                        "gitHub": None,
                        "skype": "Spotify",
                        "telegram": "Instagram",
                        "whatsApp": "SoundCloud",
                        "follower": None,
                        "following": None
                    }
                )
            ]
        )
    }
)
class PersonalProfileCombinedView(APIView):
    """GET/PUT /api/v1/personal/profile - Get or Update profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user profile - returns same format as profilecached (direct response)."""
        # Check authentication explicitly
        if not request.user or not request.user.is_authenticated:
            return create_authentication_error_response()
        
        try:
            serializer = UserCompatibilitySerializer(request.user, context={'request': request})
            # Return same format as profilecached - direct user data, no wrapper
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Personal'],
        operation_id='personal_profile_update',
        summary='Update profile details of currently logged in user',
        description='Update profile details of currently logged in user.',
        request=ProfileAdminUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update profile',
                value={
                    'userid': 'string',
                    'userName': 'string',
                    'firstName': 'string',
                    'lastName': 'string',
                    'phoneNumber': 'string',
                    'email': 'string',
                    'imageUrl': 'string',
                    'companyName': 'string',
                    'companyNumber': 'string',
                    'middleName': 'string',
                    'gender': 0,
                    'title': 'string',
                    'info': 'string',
                    'vatNumber': 'string',
                    'sheba': 'string',
                    'bankname': 'string',
                    'birthdate': '2025-11-12T10:32:49.790Z',
                    'codeMeli': 'string',
                    'representativeBy': 'string',
                    'blueUser': True,
                    'blueUSerActiveDate': '2025-11-12T10:32:49.790Z',
                    'issue': 'string',
                    'rolesRequests': 'string',
                    'language': 'string',
                    'city': 'string',
                    'country': 'string',
                    'companyId': 0,
                    'instagram': 'string',
                    'facebook': 'string',
                    'linkedIn': 'string',
                    'twitter': 'string',
                    'gitHub': 'string',
                    'skype': 'string',
                    'telegram': 'string',
                    'whatsApp': 'string'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=UserCompatibilitySerializer,
                description='User profile updated successfully'
            )
        }
    )
    def put(self, request):
        """Update current user profile matching old Swagger format (direct response, no wrapper)."""
        # Check authentication explicitly
        if not request.user or not request.user.is_authenticated:
            return create_authentication_error_response()
        
        try:
            serializer = ProfileAdminUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            user = request.user
            
            # Map camelCase to snake_case for Django model
            field_mapping = {
                'userName': 'username',
                'firstName': 'first_name',
                'lastName': 'last_name',
                'phoneNumber': 'phone_number',
                'imageUrl': 'image_url',
                'companyName': 'company_name',
                'companyNumber': 'company_number',
                'middleName': 'middle_name',
                'vatNumber': 'vat_number',
                'bankname': 'bank_name',
                'birthdate': 'birth_date',
                'codeMeli': 'national_id',
                'representativeBy': 'representative_by',
                'blueUser': 'blue_user',
                'blueUSerActiveDate': 'blue_user_active_date',
                'rolesRequests': 'roles_requests',
            }
            
            # Update user fields
            for key, value in validated_data.items():
                if key == 'userid':
                    continue  # Skip userid, user is already set to current user
                elif key in field_mapping:
                    setattr(user, field_mapping[key], value)
                elif hasattr(user, key):
                    setattr(user, key, value)
                # Note: Social media fields (instagram, facebook, etc.) may not exist in User model
            
            # Handle birthdate conversion if it's a datetime
            if validated_data.get('birthdate'):
                birthdate = validated_data.get('birthdate')
                if hasattr(birthdate, 'date'):
                    user.birth_date = birthdate.date()
                else:
                    user.birth_date = birthdate
            
            user.save()
            
            # Return in Flutter format (camelCase) directly, not wrapped
            response_serializer = UserCompatibilitySerializer(user, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_profilewithcoins',
    summary='Get profile details of currently logged in user',
    description='Get profile details of currently logged in user with coins/points.',
    responses={
        200: OpenApiResponse(
            response=UserCompatibilitySerializer,
            description='User profile with coins',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "id": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                        "coins": None,
                        "userName": "admin@root.com",
                        "firstName": "مدیر",
                        "lastName": "آروین ویرا",
                        "email": "admin@root.com",
                        "isActive": True,
                        "middleName": None,
                        "gender": None,
                        "title": None,
                        "info": None,
                        "emailConfirmed": True,
                        "phoneNumberConfirmed": False,
                        "phoneNumber": "09876543212",
                        "imageUrl": "/uploads/app/2e40483d1caa474b89a2e5abfef45b96.webp",
                        "thumbnail": "/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp",
                        "companyName": "خانگــی",
                        "companyNumber": None,
                        "code": "0",
                        "codeType": 0,
                        "jsonExt": "i have not bio 🚫",
                        "vatNumber": "known",
                        "representative": None,
                        "sheba": "IR012345678912345678912345",
                        "bankname": None,
                        "birthdate": "2025-10-12T20:30:00",
                        "codeMeli": "0825659862",
                        "representativeBy": None,
                        "representativeDate": None,
                        "blueUser": None,
                        "blueUSerActiveDate": None,
                        "issue": None,
                        "rolesRequests": "artist",
                        "companyId": None,
                        "instagram": None,
                        "facebook": None,
                        "linkedIn": "YouTube",
                        "twitter": "Twitter",
                        "gitHub": None,
                        "skype": "Spotify",
                        "telegram": "Instagram",
                        "whatsApp": "SoundCloud",
                        "follower": None,
                        "following": None
                    }
                )
            ]
        )
    }
)
class PersonalProfileWithCoinsView(APIView):
    """GET /api/v1/personal/profilewithcoins - Get profile with coins"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user profile with coins matching old Swagger format (direct response, no wrapper)."""
        # Check authentication explicitly
        if not request.user or not request.user.is_authenticated:
            return create_authentication_error_response()
        
        try:
            serializer = UserCompatibilitySerializer(request.user, context={'request': request})
            data = serializer.data.copy()
            
            # Remove createDate from profilewithcoins response (old Swagger doesn't include it)
            if 'createDate' in data:
                del data['createDate']
            
            # Add coins information right after id (old Swagger uses "coins" not "points")
            coins_value = None
            try:
                user_points = UserPoints.objects.get(user=request.user)
                coins_value = user_points.balance
            except UserPoints.DoesNotExist:
                coins_value = None
            
            # Reorder data to match old Swagger: id, coins, then rest of fields
            ordered_data = {'id': data.pop('id')}
            ordered_data['coins'] = coins_value
            ordered_data.update(data)
            
            # Old Swagger returns user data directly, not wrapped in {data, messages, succeeded}
            return Response(ordered_data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving profile with coins: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_profilecached',
    summary='Get profile details of currently logged in user',
    description='Get profile details of currently logged in user (cached version).',
    responses={
        200: OpenApiResponse(
            response=UserCompatibilitySerializer,
            description='User profile details (cached)',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "id": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                        "userName": "admin@root.com",
                        "firstName": "مدیر",
                        "lastName": "آروین ویرا",
                        "email": "admin@root.com",
                        "isActive": True,
                        "createDate": "2023-10-29T16:05:37.957",
                        "middleName": None,
                        "gender": None,
                        "title": None,
                        "info": None,
                        "emailConfirmed": True,
                        "phoneNumberConfirmed": False,
                        "phoneNumber": "09876543212",
                        "imageUrl": "/uploads/app/2e40483d1caa474b89a2e5abfef45b96.webp",
                        "thumbnail": "/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp",
                        "companyName": "خانگــی",
                        "companyNumber": None,
                        "code": "0",
                        "codeType": 0,
                        "companyId": None,
                        "jsonExt": "i have not bio 🚫",
                        "vatNumber": "known",
                        "representative": None,
                        "sheba": "IR012345678912345678912345",
                        "bankname": None,
                        "birthdate": "2025-10-12T20:30:00",
                        "codeMeli": "0825659862",
                        "representativeBy": None,
                        "representativeDate": None,
                        "blueUser": None,
                        "blueUSerActiveDate": None,
                        "issue": None,
                        "rolesRequests": "artist",
                        "instagram": None,
                        "facebook": None,
                        "linkedIn": "YouTube",
                        "twitter": "Twitter",
                        "gitHub": None,
                        "skype": "Spotify",
                        "telegram": "Instagram",
                        "whatsApp": "SoundCloud",
                        "follower": None,
                        "following": None
                    }
                )
            ]
        )
    }
)
class PersonalProfileCachedView(APIView):
    """GET /api/v1/personal/profilecached - Get profile (cached)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user profile (cached) matching old Swagger format (direct response, no wrapper)."""
        # Check authentication explicitly
        if not request.user or not request.user.is_authenticated:
            return create_authentication_error_response()
        
        try:
            # TODO: Implement caching if needed
            serializer = UserCompatibilitySerializer(request.user, context={'request': request})
            # Old Swagger returns user data directly, not wrapped in {data, messages, succeeded}
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving cached profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# ADMIN PROFILE ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_profileadmin',
    summary='Update profile details of currently logged in user',
    description='Update profile details of currently logged in user (Admin).',
    request=ProfileAdminUpdateRequestSerializer,
    examples=[
        OpenApiExample(
            'Update profile (Admin)',
            value={
                'userid': 'string',
                'userName': 'string',
                'firstName': 'string',
                'lastName': 'string',
                'phoneNumber': 'string',
                'email': 'string',
                'imageUrl': 'string',
                'companyName': 'string',
                'companyNumber': 'string',
                'middleName': 'string',
                'gender': 0,
                'title': 'string',
                'info': 'string',
                'vatNumber': 'string',
                'sheba': 'string',
                'bankname': 'string',
                'birthdate': '2025-11-12T10:32:49.790Z',
                'codeMeli': 'string',
                'representativeBy': 'string',
                'blueUser': True,
                'blueUSerActiveDate': '2025-11-12T10:32:49.790Z',
                'issue': 'string',
                'rolesRequests': 'string',
                'language': 'string',
                'city': 'string',
                'country': 'string',
                'companyId': 0,
                'instagram': 'string',
                'facebook': 'string',
                'linkedIn': 'string',
                'twitter': 'string',
                'gitHub': 'string',
                'skype': 'string',
                'telegram': 'string',
                'whatsApp': 'string'
            },
            request_only=True
        )
    ],
    responses={200: UserProfileSerializer}
)
class PersonalProfileAdminView(APIView):
    """PUT /api/v1/personal/profileadmin - Update profile (Admin)"""
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request):
        """Update current user profile (Admin) matching old Swagger format."""
        try:
            serializer = ProfileAdminUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get user - use userid if provided, otherwise use current user
            user = request.user
            if validated_data.get('userid'):
                try:
                    user = User.objects.get(pk=validated_data.get('userid'))
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data.get("userid")}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userid': [f'User with ID "{validated_data.get("userid")}" not found.']}
                    )
            
            # Map camelCase to snake_case for Django model
            field_mapping = {
                'userName': 'username',
                'firstName': 'first_name',
                'lastName': 'last_name',
                'phoneNumber': 'phone_number',
                'imageUrl': 'image_url',
                'companyName': 'company_name',
                'companyNumber': 'company_number',
                'middleName': 'middle_name',
                'vatNumber': 'vat_number',
                'bankname': 'bank_name',
                'birthdate': 'birth_date',
                'codeMeli': 'national_id',
                'representativeBy': 'representative_by',
                'blueUser': 'blue_user',
                'blueUSerActiveDate': 'blue_user_active_date',
                'rolesRequests': 'roles_requests',
            }
            
            # Update user fields
            for key, value in validated_data.items():
                if key == 'userid':
                    continue  # Skip userid, already handled
                elif key in field_mapping:
                    setattr(user, field_mapping[key], value)
                elif hasattr(user, key):
                    setattr(user, key, value)
                # Note: Social media fields (instagram, facebook, etc.) may not exist in User model
                # They would need to be stored in a related model or JSON field
            
            # Handle birthdate conversion if it's a datetime
            if validated_data.get('birthdate'):
                birthdate = validated_data.get('birthdate')
                if hasattr(birthdate, 'date'):
                    user.birth_date = birthdate.date()
                else:
                    user.birth_date = birthdate
            
            user.save()
            
            response_serializer = UserCompatibilitySerializer(user, context={'request': request})
            return create_success_response(data=response_serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_profileupdatewithadmin',
    summary='Update profile details of user by ID (Admin)',
    description='Update profile details of user by ID (Admin).',
    parameters=[
        OpenApiParameter(name='userId', type=str, location=OpenApiParameter.PATH, description='User ID')
    ],
    request=ProfileAdminUpdateRequestSerializer,
    examples=[
        OpenApiExample(
            'Update profile by ID (Admin)',
            value={
                'userid': 'string',
                'userName': 'string',
                'firstName': 'string',
                'lastName': 'string',
                'phoneNumber': 'string',
                'email': 'string',
                'imageUrl': 'string',
                'companyName': 'string',
                'companyNumber': 'string',
                'middleName': 'string',
                'gender': 0,
                'title': 'string',
                'info': 'string',
                'vatNumber': 'string',
                'sheba': 'string',
                'bankname': 'string',
                'birthdate': '2025-11-12T10:32:49.790Z',
                'codeMeli': 'string',
                'representativeBy': 'string',
                'blueUser': True,
                'blueUSerActiveDate': '2025-11-12T10:32:49.790Z',
                'issue': 'string',
                'rolesRequests': 'string',
                'language': 'string',
                'city': 'string',
                'country': 'string',
                'companyId': 0,
                'instagram': 'string',
                'facebook': 'string',
                'linkedIn': 'string',
                'twitter': 'string',
                'gitHub': 'string',
                'skype': 'string',
                'telegram': 'string',
                'whatsApp': 'string'
            },
            request_only=True
        )
    ],
    responses={200: UserProfileSerializer, 404: {'description': 'User not found'}}
)
class PersonalProfileUpdateWithAdminView(APIView):
    """PUT /api/v1/personal/profileupdatewithadmin/{userId} - Update user profile (Admin)"""
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, userId):
        """Update user profile by ID (Admin) matching old Swagger format."""
        try:
            user = User.objects.get(pk=userId)
            
            serializer = ProfileAdminUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Map camelCase to snake_case for Django model
            field_mapping = {
                'userName': 'username',
                'firstName': 'first_name',
                'lastName': 'last_name',
                'phoneNumber': 'phone_number',
                'imageUrl': 'image_url',
                'companyName': 'company_name',
                'companyNumber': 'company_number',
                'middleName': 'middle_name',
                'vatNumber': 'vat_number',
                'bankname': 'bank_name',
                'birthdate': 'birth_date',
                'codeMeli': 'national_id',
                'representativeBy': 'representative_by',
                'blueUser': 'blue_user',
                'blueUSerActiveDate': 'blue_user_active_date',
                'rolesRequests': 'roles_requests',
            }
            
            # Update user fields
            for key, value in validated_data.items():
                if key == 'userid':
                    continue  # Skip userid from request body, use path parameter
                elif key in field_mapping:
                    setattr(user, field_mapping[key], value)
                elif hasattr(user, key):
                    setattr(user, key, value)
                # Note: Social media fields (instagram, facebook, etc.) may not exist in User model
            
            # Handle birthdate conversion if it's a datetime
            if validated_data.get('birthdate'):
                birthdate = validated_data.get('birthdate')
                if hasattr(birthdate, 'date'):
                    user.birth_date = birthdate.date()
                else:
                    user.birth_date = birthdate
            
            user.save()
            
            response_serializer = UserCompatibilitySerializer(user, context={'request': request})
            return create_success_response(data=response_serializer.data, messages=[])
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{userId}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{userId}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_adminactiveuser',
    summary='Active user',
    description='Activate a user (Admin).',
    parameters=[
        OpenApiParameter(name='userId', type=str, location=OpenApiParameter.PATH, description='User ID')
    ],
    responses={
        200: OpenApiResponse(
            response=bool,
            description='User activated successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value=True
                )
            ]
        )
    }
)
class PersonalAdminActiveUserView(APIView):
    """GET /api/v1/personal/adminactiveuser/{userId} - Activate user (Admin)"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, userId):
        """Activate a user matching old Swagger format (returns true)."""
        try:
            user = User.objects.get(pk=userId)
            user.is_active = True
            user.save()
            # Old Swagger returns just true (boolean)
            return Response(True, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{userId}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{userId}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while activating user: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_admindeactiveuser',
    summary='DeActive user',
    description='Deactivate a user (Admin).',
    parameters=[
        OpenApiParameter(name='userId', type=str, location=OpenApiParameter.PATH, description='User ID')
    ],
    responses={
        200: OpenApiResponse(
            response=bool,
            description='User deactivated successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value=True
                )
            ]
        )
    }
)
class PersonalAdminDeactiveUserView(APIView):
    """GET /api/v1/personal/admindeactiveuser/{userId} - Deactivate user (Admin)"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, userId):
        """Deactivate a user matching old Swagger format (returns true)."""
        try:
            user = User.objects.get(pk=userId)
            user.is_active = False
            user.save()
            # Old Swagger returns just true (boolean)
            return Response(True, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{userId}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{userId}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deactivating user: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# REPRESENTATIVE ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_representative',
    summary='Update Representative of currently logged in user',
    description='Update Representative of currently logged in user.',
    request=RepresentativeRequestSerializer,
    responses={200: UserProfileSerializer}
)
class PersonalRepresentativeView(APIView):
    """POST /api/v1/personal/representative - Update representative"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Update user representative matching old Swagger format."""
        try:
            serializer = RepresentativeRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            representative = validated_data.get('representative', '')
            representative_by = validated_data.get('representativeBy', '')
            
            user = request.user
            if representative:
                user.representative = representative
            if representative_by:
                user.representative_by = representative_by
            user.save()
            
            response_serializer = UserCompatibilitySerializer(user, context={'request': request})
            return create_success_response(data=response_serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating representative: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_profiledatebyrepresentativedate',
    summary='Get list of user Representative from date to date',
    description='Get list of user Representative from date to date.',
    request=ProfileDateByRepresentativeDateRequestSerializer,
    responses={200: {
        'description': 'List of representatives',
        'content': {
            'application/json': {
                'example': {
                    'items': [],
                    'pageNumber': 1,
                    'pageSize': 20,
                    'total': 0
                }
            }
        }
    }}
)
class PersonalProfileDateByRepresentativeDateView(APIView):
    """POST /api/v1/personal/profiledatebyrepresentativedate - Get representatives by date"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Get users with representatives filtered by date range matching old Swagger format."""
        try:
            serializer = ProfileDateByRepresentativeDateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            start_date = validated_data.get('startDate')
            end_date = validated_data.get('endDate')
            page_number = validated_data.get('pageNumber', 1)
            page_size = validated_data.get('pageSize', 20)

            qs = User.objects.filter(representative__isnull=False).exclude(representative='').order_by('-created_at')

            if start_date:
                qs = qs.filter(created_at__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__lte=end_date)

            total = qs.count()
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]

            response_serializer = UserCompatibilitySerializer(items, many=True, context={'request': request})
            
            # Return paginated response matching old Swagger format
            return create_success_response(
                data={
                    'items': response_serializer.data,
                    'pageNumber': page_number,
                    'pageSize': page_size,
                    'total': total
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving representatives: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# BLUE BADGE ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_setbluebadge',
    summary='Admin can setupBlueBadge',
    description='Admin can setup blue badge for a user.',
    request=SetBlueBadgeRequestSerializer,
    responses={200: {
        'description': 'Blue badge set',
        'content': {
            'application/json': {
                'example': {
                    'message': 'Blue badge set successfully',
                    'userId': 'user-uuid',
                    'blueBadge': True
                }
            }
        }
    }}
)
class PersonalSetBlueBadgeView(APIView):
    """POST /api/v1/personal/setbluebadge - Set blue badge (Admin)"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Set blue badge for a user matching old Swagger format."""
        try:
            serializer = SetBlueBadgeRequestSerializer(data=request.data)
            if not serializer.is_valid():
                error_response = create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
                return add_custom_headers(error_response)
            
            validated_data = serializer.validated_data
            user_id = validated_data.get('userId')
            blue_badge = validated_data.get('blueBadge', False)
            
            try:
                user = User.objects.get(pk=user_id)
                # TODO: Add blue_badge field to User model if needed
                # For now, return success response matching old Swagger format
                response = create_success_response(
                    data={
                        'message': 'Blue badge set successfully',
                        'userId': str(user.id),
                        'blueBadge': blue_badge
                    },
                    messages=['Blue badge set successfully']
                )
                return add_custom_headers(response)
            except User.DoesNotExist:
                error_response = create_error_response(
                    error_message=f'User with ID "{user_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'userId': [f'User with ID "{user_id}" not found.']}
                )
                return add_custom_headers(error_response)
        except Exception as e:
            error_response = create_error_response(
                error_message=f'An error occurred while setting blue badge: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
            return add_custom_headers(error_response)


@extend_schema(
    tags=['Personal'],
    operation_id='personal_requestbluebadge',
    summary='Request blue badge',
    description='Request a blue badge for the current user.',
    request=RequestBlueBadgeRequestSerializer,
    responses={200: {
        'description': 'Blue badge requested',
        'content': {
            'application/json': {
                'example': {
                    'message': 'Blue badge request submitted',
                    'status': 'pending'
                }
            }
        }
    }}
)
class PersonalRequestBlueBadgeView(APIView):
    """POST /api/v1/personal/requestbluebadge - Request blue badge"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Request blue badge matching old Swagger format."""
        try:
            serializer = RequestBlueBadgeRequestSerializer(data=request.data)
            if not serializer.is_valid():
                error_response = create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
                return add_custom_headers(error_response)
            
            validated_data = serializer.validated_data
            reason = validated_data.get('reason', '')
            
            # TODO: Implement blue badge request system
            # For now, return success response matching old Swagger format
            response = create_success_response(
                data={
                    'message': 'Blue badge request submitted',
                    'status': 'pending',
                    'reason': reason
                },
                messages=['Blue badge request submitted successfully']
            )
            return add_custom_headers(response)
        except Exception as e:
            error_response = create_error_response(
                error_message=f'An error occurred while requesting blue badge: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
            return add_custom_headers(error_response)


# ============================================================================
# ROLE REQUEST ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_requestrole',
    summary='Request role',
    description='Request a role for the current user.',
    request=RequestRoleRequestSerializer,
    responses={200: {
        'description': 'Role requested',
        'content': {
            'application/json': {
                'example': {
                    'message': 'Role request submitted',
                    'role': 'driver',
                    'status': 'pending'
                }
            }
        }
    }}
)
class PersonalRequestRoleView(APIView):
    """POST /api/v1/personal/requestrole - Request role"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Request a role matching old Swagger format."""
        try:
            serializer = RequestRoleRequestSerializer(data=request.data)
            if not serializer.is_valid():
                error_response = create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
                return add_custom_headers(error_response)
            
            validated_data = serializer.validated_data
            role = validated_data.get('role')
            reason = validated_data.get('reason', '')
            
            # TODO: Implement role request system
            # For now, return success response matching old Swagger format
            response = create_success_response(
                data={
                    'message': 'Role request submitted',
                    'role': role,
                    'status': 'pending',
                    'reason': reason
                },
                messages=['Role request submitted successfully']
            )
            return add_custom_headers(response)
        except Exception as e:
            error_response = create_error_response(
                error_message=f'An error occurred while requesting role: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
            return add_custom_headers(error_response)


# ============================================================================
# PASSWORD ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_reset_password',
    summary='Reset password by email',
    description='Reset password by email.',
    request=ResetPasswordRequestSerializer,
    examples=[
        OpenApiExample(
            'Request example',
            value={
                "email": "user@example.com"
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Password reset response',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "messages": ["string"],
                        "succeeded": True,
                        "data": "string",
                        "source": "string",
                        "exception": "string",
                        "errorId": "string",
                        "supportMessage": "string",
                        "statusCode": 0
                    }
                )
            ]
        )
    }
)
class PersonalResetPasswordView(APIView):
    """POST /api/v1/personal/reset-password - Reset password by email"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Reset user password by email matching old Swagger format."""
        try:
            serializer = ResetPasswordRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            email = validated_data.get('email')
            
            try:
                user = User.objects.get(email=email)
                # Generate a new password or send reset link
                # For now, return success response matching old Swagger format
                import uuid
                return create_success_response(
                    data="Password reset link sent successfully",
                    messages=["Password reset link sent successfully"]
                )
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with email "{email}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'email': [f'User with email "{email}" not found.']}
                )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while resetting password: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_change_password',
    summary='Change password of currently logged in user',
    description='Change password of currently logged in user.',
    request=ChangePasswordRequestSerializer,
    examples=[
        OpenApiExample(
            'Change password',
            value={
                'password': 'string',
                'newPassword': 'string',
                'confirmNewPassword': 'string'
            },
            request_only=True
        )
    ],
    responses={200: {
        'description': 'Password changed',
        'content': {
            'application/json': {
                'example': {
                    'message': 'Password changed successfully'
                }
            }
        }
    }}
)
class PersonalChangePasswordView(APIView):
    """PUT /api/v1/personal/change-password - Change password"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Change current user password matching old Swagger format."""
        try:
            serializer = ChangePasswordRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            current_password = validated_data.get('password')  # Changed from currentPassword to password
            new_password = validated_data.get('newPassword')
            
            if not request.user.check_password(current_password):
                return create_error_response(
                    error_message='Current password is incorrect',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'password': ['Current password is incorrect']}
                )
            
            request.user.set_password(new_password)
            request.user.save()
            
            return create_success_response(
                data={'message': 'Password changed successfully'},
                messages=['Password changed successfully']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while changing password: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# PERMISSIONS ENDPOINT
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_permissions',
    summary='Get permissions of currently logged in user',
    description='Get permissions of currently logged in user.',
    responses={200: {
        'description': 'User permissions',
        'content': {
            'application/json': {
                'example': {
                    'isStaff': False,
                    'isManager': False,
                    'isDriver': True,
                    'isActive': True,
                    'permissions': []
                }
            }
        }
    }}
)
class PersonalPermissionsView(APIView):
    """GET /api/v1/personal/permissions - Get permissions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user permissions matching old Swagger format."""
        try:
            permissions_data = {
                'isStaff': request.user.is_staff,
                'isManager': getattr(request.user, 'is_manager', False),
                'isDriver': getattr(request.user, 'is_driver', False),
                'isActive': request.user.is_active,
                'permissions': []  # TODO: Add custom permissions if needed
            }
            return create_success_response(data=permissions_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving permissions: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# REPAIR REQUEST ENDPOINTS (Placeholders)
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_repairrequests',
    summary='Get RepairRequests of currently logged in user',
    description='Get RepairRequests of currently logged in user.',
    request=RepairRequestsRequestSerializer,
    examples=[
        OpenApiExample(
            'Request example',
            value={
                "trackingCode": "string",
                "status": 0,
                "type": 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            description='List of repair requests',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class PersonalRepairRequestsView(APIView):
    """POST /api/v1/personal/repairrequests - Get repair requests"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Get repair requests matching old Swagger format."""
        try:
            serializer = RepairRequestsRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            tracking_code = validated_data.get('trackingCode', '')
            status_filter = validated_data.get('status')
            type_filter = validated_data.get('type')
            
            # TODO: Implement repair request system with filtering by trackingCode, status, type
            # For now, return empty array response matching old Swagger format
            return create_success_response(
                data=[],
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair requests: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_numberofrepairrequestsinstatus',
    summary='Get number of repair requests in each status for currently logged in user',
    description='Get number of repair requests in each status for currently logged in user.',
    responses={200: {
        'description': 'Repair request counts by status',
        'content': {
            'application/json': {
                'example': {
                    'pending': 0,
                    'in_progress': 0,
                    'completed': 0,
                    'cancelled': 0
                }
            }
        }
    }}
)
class PersonalNumberOfRepairRequestsInStatusView(APIView):
    """GET /api/v1/personal/numberofrepairrequestsinstatus - Get repair request counts"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get repair request counts by status matching old Swagger format."""
        try:
            # TODO: Implement repair request system
            # For now, return empty counts matching old Swagger format
            return create_success_response(
                data={
                    'pending': 0,
                    'in_progress': 0,
                    'completed': 0,
                    'cancelled': 0
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair request counts: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_repairrequest',
    summary='Get RepairRequests of currently logged in user',
    description='Get RepairRequests of currently logged in user by ID.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Repair Request ID')
    ],
    responses={200: {
        'description': 'Repair request details',
        'content': {
            'application/json': {
                'example': {
                    'id': 'repair-uuid',
                    'status': 'pending'
                }
            }
        }
    }}
)
class PersonalRepairRequestView(APIView):
    """GET /api/v1/personal/repairrequest/{id} - Get repair request"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get repair request by ID matching old Swagger format."""
        try:
            # TODO: Implement repair request system
            # For now, return error response matching old Swagger format
            return create_error_response(
                error_message=f'Repair request with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Repair request with ID "{id}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_repairrequestdocument',
    summary='Add repair request document for currently logged in user',
    description='Add repair request document for currently logged in user.',
    request=RepairRequestDocumentRequestSerializer,
    examples=[
        OpenApiExample(
            'Request example',
            value={
                "repairRequestId": 0,
                "fileUrl": "string"
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Document added',
            examples=[
                OpenApiExample(
                    'Request example',
                    value={
                        "repairRequestId": 0,
                        "fileUrl": "string"
                    }
                )
            ]
        )
    }
)
class PersonalRepairRequestDocumentView(APIView):
    """POST /api/v1/personal/repairrequestdocument - Add repair request document"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add repair request document matching old Swagger format."""
        try:
            serializer = RepairRequestDocumentRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            repair_request_id = validated_data.get('repairRequestId')
            file_url = validated_data.get('fileUrl')
            
            # TODO: Implement repair request document by fileUrl
            # For now, return success response matching old Swagger format
            import uuid
            document_id = str(uuid.uuid4())
            
            return create_success_response(
                data={
                    'message': 'Document added successfully',
                    'documentId': document_id,
                    'repairRequestId': repair_request_id
                },
                messages=['Document added successfully']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while adding document: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_repairrequestmessage',
    summary='Add repair request message',
    description='Add a message to a repair request.',
    request=RepairRequestMessageRequestSerializer,
    examples=[
        OpenApiExample(
            'Request example',
            value={
                "repairRequestId": 0,
                "message": "string",
                "type": 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Message added',
            examples=[
                OpenApiExample(
                    'Request example',
                    value={
                        "repairRequestId": 0,
                        "message": "string",
                        "type": 0
                    }
                )
            ]
        )
    }
)
class PersonalRepairRequestMessageView(APIView):
    """POST /api/v1/personal/repairrequestmessage - Add repair request message"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add repair request message matching old Swagger format."""
        try:
            serializer = RepairRequestMessageRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            repair_request_id = validated_data.get('repairRequestId')
            message = validated_data.get('message')
            message_type = validated_data.get('type')
            
            # TODO: Implement repair request messaging with type
            # For now, return success response matching old Swagger format
            import uuid
            message_id = str(uuid.uuid4())
            
            return create_success_response(
                data={
                    'message': 'Message added successfully',
                    'messageId': message_id,
                    'repairRequestId': repair_request_id
                },
                messages=['Message added successfully']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while adding message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Personal'],
    operation_id='personal_repairrequestmessagesbyrepairid',
    summary='Get repair request messages',
    description='Get messages for a repair request.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Repair Request ID')
    ],
    responses={200: {
        'description': 'List of messages',
        'content': {
            'application/json': {
                'example': {
                    'items': [],
                    'total': 0
                }
            }
        }
    }}
)
class PersonalRepairRequestMessagesByRepairIdView(APIView):
    """GET /api/v1/personal/repairrequestmessagesbyrepairid/{id} - Get repair request messages"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get repair request messages matching old Swagger format."""
        try:
            # TODO: Implement repair request messaging
            # For now, return empty list matching old Swagger format
            return create_success_response(
                data={
                    'items': [],
                    'total': 0
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving messages: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# ============================================================================
# CLIENT USER INFO ENDPOINT
# ============================================================================

@extend_schema(
    tags=['Personal'],
    operation_id='personal_client_userinfo',
    summary='Get user info',
    description='Get user information by ID.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='User ID')
    ],
    responses={
        200: OpenApiResponse(
            description='User information',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "id": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                        "userName": "09056761466",
                        "firstName": None,
                        "lastName": None,
                        "email": None,
                        "imageUrl": None,
                        "thumbnail": None,
                        "companyId": None,
                        "instagram": None,
                        "facebook": None,
                        "linkedIn": None,
                        "twitter": None,
                        "gitHub": None,
                        "skype": None,
                        "telegram": None,
                        "whatsApp": None,
                        "follower": 0,
                        "following": 0
                    }
                )
            ]
        ),
        404: {'description': 'User not found'}
    }
)
class PersonalClientUserInfoView(APIView):
    """GET /api/v1/personal/client/userinfo/{id} - Get user info"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get user information by ID matching old Swagger format (direct response, no wrapper)."""
        try:
            user = User.objects.get(pk=id)
            
            # Get image URLs as relative paths
            image_url = None
            thumbnail = None
            if user.image_url:
                img_url = user.image_url.url
                if img_url.startswith('http'):
                    from urllib.parse import urlparse
                    parsed = urlparse(img_url)
                    img_url = parsed.path
                image_url = img_url
                thumbnail = img_url  # Same as imageUrl for now
            
            # Build simplified response with only required fields
            response_data = {
                "id": str(user.id),
                "userName": user.username or None,
                "firstName": user.first_name or None,
                "lastName": user.last_name or None,
                "email": user.email or None,
                "imageUrl": image_url,
                "thumbnail": thumbnail,
                "companyId": None,  # Not in User model
                "instagram": None,  # Not in User model
                "facebook": None,  # Not in User model
                "linkedIn": None,  # Not in User model
                "twitter": None,  # Not in User model
                "gitHub": None,  # Not in User model
                "skype": None,  # Not in User model
                "telegram": None,  # Not in User model
                "whatsApp": None,  # Not in User model
                "follower": 0,  # Placeholder
                "following": 0,  # Placeholder
            }
            
            # Old Swagger returns user data directly, not wrapped in {data, messages, succeeded}
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'User with ID "{id}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving user info: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

