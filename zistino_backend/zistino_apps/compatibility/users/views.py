"""
Views for Users compatibility layer.
Provides all 12 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.db.models import Q
from django.contrib.auth.models import Permission, Group

from zistino_apps.authentication.models import User
from zistino_apps.users.serializers import UserSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.users.views import AdminUserSearchView, ManagerUserByRoleView
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.compatibility.roles.models import Role
from .serializers import (
    UserCompatibilitySerializer,
    UserListResponseSerializer,
    UserDetailResponseSerializer,
    UserSearchRequestSerializer,
    UserSearchSPRequestSerializer,
    UserByRoleRequestSerializer,
    UserByRoleRequestRequestSerializer,
    UserRolesUpdateSerializer,
    UserRoleItemSerializer,
    RoleSerializer,
    PermissionSerializer,
)


@extend_schema(tags=['Users'])
class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Users endpoints.
    Provides list and retrieve operations.
    Uses UserCompatibilitySerializer to match Flutter UserModel format.
    """
    queryset = User.objects.all()
    serializer_class = UserCompatibilitySerializer  # Use compatibility serializer for Flutter
    permission_classes = [IsAuthenticated, IsManager]

    @extend_schema(
        tags=['Users'],
        operation_id='users_list',
        summary='List all users',
        responses={
            'default': {
                'description': 'Error response',
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
    def list(self, request, *args, **kwargs):
        """List all users. Returns response in old Swagger format with wrapper."""
        # Get queryset and serialize
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Wrap response in old Swagger format: { "data": [...], "messages": [], "succeeded": true }
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Users'],
        operation_id='users_retrieve',
        summary='Retrieve a user by ID',
        responses={
            'default': {
                'description': 'Error response',
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
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a user by ID. Returns response in old Swagger format with wrapper."""
        response = super().retrieve(request, *args, **kwargs)
        # Wrap response in old Swagger format
        return create_success_response(
            data=response.data,
            status_code=response.status_code
        )

    @extend_schema(
        tags=['Users'],
        operation_id='users_search',
        summary='Search users using available filters',
        request=UserSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ],
                    "isActive": True,
                    "roleId": "string",
                    "rolesRequests": "string",
                    "companyId": 0,
                    "hasIssue": True,
                    "userName": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Search results with pagination',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 'string',
                                    'userName': 'string',
                                    'firstName': 'string',
                                    'lastName': 'string',
                                    'email': 'string',
                                    'isActive': True,
                                    'createDate': '2025-11-07T19:13:28.296Z',
                                    'middleName': 'string',
                                    'gender': 0,
                                    'title': 'string',
                                    'info': 'string',
                                    'emailConfirmed': True,
                                    'phoneNumberConfirmed': True,
                                    'phoneNumber': 'string',
                                    'imageUrl': 'string',
                                    'thumbnail': 'string',
                                    'companyName': 'string',
                                    'companyNumber': 'string',
                                    'code': 'string',
                                    'codeType': 0,
                                    'companyId': 0,
                                    'jsonExt': 'string',
                                    'vatNumber': 'string',
                                    'representative': 'string',
                                    'sheba': 'string',
                                    'bankname': 'string',
                                    'birthdate': '2025-11-07T19:13:28.296Z',
                                    'codeMeli': 'string',
                                    'representativeBy': 'string',
                                    'representativeDate': '2025-11-07T19:13:28.296Z',
                                    'blueUser': True,
                                    'blueUSerActiveDate': '2025-11-07T19:13:28.296Z',
                                    'issue': 'string',
                                    'rolesRequests': 'string',
                                    'instagram': 'string',
                                    'facebook': 'string',
                                    'linkedIn': 'string',
                                    'twitter': 'string',
                                    'gitHub': 'string',
                                    'skype': 'string',
                                    'telegram': 'string',
                                    'whatsApp': 'string',
                                    'follower': 0,
                                    'following': 0
                                }
                            ],
                            'currentPage': 0,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 0,
                            'hasPreviousPage': True,
                            'hasNextPage': True
                        }
                    )
                ]
            ),
            'default': {
                'description': 'Error response',
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
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search users with pagination and filters. Returns format matching old Swagger."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        
        qs = User.objects.all()
        
        if keyword:
            # Search in username, email, phone, full name
            q = Q(username__icontains=keyword) | Q(email__icontains=keyword) | Q(phone_number__icontains=keyword)
            # If user has first_name/last_name fields
            try:
                q = q | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            except:
                pass
            qs = qs.filter(q)
        
        qs = qs.order_by('-created_at')
        
        # Calculate pagination
        total_count = qs.count()
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        current_page = page_number
        has_previous_page = current_page > 1
        has_next_page = current_page < total_pages
        
        # Get paginated items
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        # Serialize with UserCompatibilitySerializer
        serializer = UserCompatibilitySerializer(items, many=True, context={'request': request})
        
        # Return in old Swagger format with pagination
        # Structure: { "messages": [], "succeeded": true, "data": [...], "currentPage": ..., ... }
        response_data = {
            'messages': [],
            'succeeded': True,
            'data': serializer.data,
            'currentPage': current_page,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous_page,
            'hasNextPage': has_next_page
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Users'],
        operation_id='users_searchsp',
        summary='Search users using stored procedure',
        request=UserSearchSPRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ],
                    "isActive": True,
                    "roleId": "string",
                    "rolesRequests": "string",
                    "companyId": 0,
                    "hasIssue": True,
                    "userName": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Search results with pagination',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 'string',
                                    'userName': 'string',
                                    'firstName': 'string',
                                    'lastName': 'string',
                                    'email': 'string',
                                    'isActive': True,
                                    'createDate': '2025-11-07T19:13:28.296Z',
                                    'middleName': 'string',
                                    'gender': 0,
                                    'title': 'string',
                                    'info': 'string',
                                    'emailConfirmed': True,
                                    'phoneNumberConfirmed': True,
                                    'phoneNumber': 'string',
                                    'imageUrl': 'string',
                                    'thumbnail': 'string',
                                    'companyName': 'string',
                                    'companyNumber': 'string',
                                    'code': 'string',
                                    'codeType': 0,
                                    'companyId': 0,
                                    'jsonExt': 'string',
                                    'vatNumber': 'string',
                                    'representative': 'string',
                                    'sheba': 'string',
                                    'bankname': 'string',
                                    'birthdate': '2025-11-07T19:13:28.296Z',
                                    'codeMeli': 'string',
                                    'representativeBy': 'string',
                                    'representativeDate': '2025-11-07T19:13:28.296Z',
                                    'blueUser': True,
                                    'blueUSerActiveDate': '2025-11-07T19:13:28.296Z',
                                    'issue': 'string',
                                    'rolesRequests': 'string',
                                    'instagram': 'string',
                                    'facebook': 'string',
                                    'linkedIn': 'string',
                                    'twitter': 'string',
                                    'gitHub': 'string',
                                    'skype': 'string',
                                    'telegram': 'string',
                                    'whatsApp': 'string',
                                    'follower': 0,
                                    'following': 0
                                }
                            ],
                            'currentPage': 0,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 0,
                            'hasPreviousPage': True,
                            'hasNextPage': True
                        }
                    )
                ]
            ),
            'default': {
                'description': 'Error response',
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
    @action(detail=False, methods=['post'], url_path='searchsp')
    def searchsp(self, request):
        """Search users using stored procedure (placeholder - uses regular search)."""
        # TODO: Implement stored procedure search if needed
        # For now, use regular search
        return self.search(request)

    @extend_schema(
        tags=['Users'],
        operation_id='users_userbyrole',
        summary='Get users by role',
        request=UserByRoleRequestSerializer,
        examples=[
            OpenApiExample(
                'User by Role Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ],
                    "isActive": True,
                    "roleId": "string",
                    "rolesRequests": "string",
                    "companyId": 0,
                    "hasIssue": True,
                    "userName": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Users filtered by role with pagination',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 1,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        }
                    )
                ]
            ),
            'default': {
                'description': 'Error response',
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
    @action(detail=False, methods=['post'], url_path='userbyrole')
    def userbyrole(self, request):
        """Get users filtered by role. Returns format matching old Swagger with pagination."""
        role = request.data.get('role', '').lower()
        is_active = request.data.get('isActive')
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        
        queryset = User.objects.all()
        
        # Filter by role
        if role == 'driver':
            queryset = queryset.filter(is_driver=True)
        elif role == 'customer':
            queryset = queryset.filter(is_driver=False)
        
        # Filter by active status
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        queryset = queryset.order_by('-created_at')
        
        # Calculate pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        current_page = page_number
        has_previous_page = current_page > 1
        has_next_page = current_page < total_pages
        
        # Get paginated items
        start = (page_number - 1) * page_size
        end = start + page_size
        items = queryset[start:end]
        
        # Serialize with UserCompatibilitySerializer
        serializer = UserCompatibilitySerializer(items, many=True, context={'request': request})
        
        # Return in old Swagger format with pagination (messages: null)
        response_data = {
            'data': serializer.data,
            'currentPage': current_page,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous_page,
            'hasNextPage': has_next_page,
            'messages': None,
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Users'],
        operation_id='users_userbyrolerequest',
        summary='Get users by role request',
        request=UserByRoleRequestRequestSerializer,
        examples=[
            OpenApiExample(
                'User by Role Request Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ],
                    "isActive": True,
                    "roleId": "string",
                    "rolesRequests": "string",
                    "companyId": 0,
                    "hasIssue": True,
                    "userName": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Users with role requests with pagination',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 1,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        }
                    )
                ]
            ),
            'default': {
                'description': 'Error response',
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
    @action(detail=False, methods=['post'], url_path='userbyrolerequest')
    def userbyrolerequest(self, request):
        """Get users by role request. Returns format matching old Swagger with pagination."""
        # TODO: Implement proper role request filtering when role request system is implemented
        # For now, return all users (similar to userbyrole)
        role_request = request.data.get('roleRequest', '').strip()
        status_filter = request.data.get('status', '').strip()
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        
        queryset = User.objects.all()
        
        # TODO: Add filtering by roleRequest and status when role request system is implemented
        # For example:
        # if role_request:
        #     queryset = queryset.filter(role_requests__role_name=role_request)
        # if status_filter:
        #     queryset = queryset.filter(role_requests__status=status_filter)
        
        queryset = queryset.order_by('-created_at')
        
        # Calculate pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        current_page = page_number
        has_previous_page = current_page > 1
        has_next_page = current_page < total_pages
        
        # Get paginated items
        start = (page_number - 1) * page_size
        end = start + page_size
        items = queryset[start:end]
        
        # Serialize with UserCompatibilitySerializer
        serializer = UserCompatibilitySerializer(items, many=True, context={'request': request})
        
        # Return in old Swagger format with pagination (messages: null)
        response_data = {
            'data': serializer.data,
            'currentPage': current_page,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous_page,
            'hasNextPage': has_next_page,
            'messages': None,
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Users'],
        operation_id='users_roles',
        summary='Get user roles',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='User roles with enabled status',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            "data": {
                                "userRoles": [
                                    {
                                        "roleId": "0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea",
                                        "roleName": "akmal",
                                        "enabled": False
                                    },
                                    {
                                        "roleId": "9569158d-ce43-4621-83b0-5e1671094d16",
                                        "roleName": "basic",
                                        "enabled": True
                                    }
                                ]
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            'default': {
                'description': 'Error response',
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
    @action(detail=True, methods=['get'], url_path='roles')
    def roles(self, request, pk=None):
        """Get roles for a specific user. Returns all roles with enabled status matching old Swagger format."""
        try:
            user = self.get_object()
            
            # Get all roles from the compatibility Role model
            all_roles = Role.objects.all().order_by('name')
            
            # Get user's groups (Django Groups are used to represent roles)
            user_groups = set(user.groups.values_list('name', flat=True))
            
            # Build userRoles list with enabled status
            user_roles = []
            for role in all_roles:
                # Check if user has this role (by matching role name to group name)
                enabled = role.name in user_groups
                
                user_roles.append({
                    'roleId': str(role.id),
                    'roleName': role.name,
                    'enabled': enabled
                })
            
            # Return in old Swagger format
            return create_success_response(
                data={
                    'userRoles': user_roles
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Users'],
        operation_id='users_update_roles',
        summary='Assign roles to user',
        request=UserRolesUpdateSerializer,
        examples=[
            OpenApiExample(
                'Assign roles to user',
                value={
                    'userRoles': [
                        {
                            'roleId': 'akmal111',
                            'roleName': 'managerrr',
                            'enabled': True
                        }
                    ]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Roles updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': ['string'],
                            'succeeded': True,
                            'data': 'string',
                            'source': 'string',
                            'exception': 'string',
                            'errorId': 'string',
                            'supportMessage': 'string',
                            'statusCode': 0
                        }
                    )
                ]
            ),
            400: {
                'description': 'Bad Request',
                'content': {
                    'application/json': {
                        'example': {
                            'messages': ['string'],
                            'succeeded': False,
                            'data': None,
                            'source': None,
                            'exception': 'Validation failed',
                            'errorId': None,
                            'supportMessage': None,
                            'statusCode': 400
                        }
                    }
                }
            },
            'default': {
                'description': 'Error response',
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
    @action(detail=True, methods=['post'], url_path='roles')
    def update_roles(self, request, pk=None):
        """Assign roles to a specific user. Matches old Swagger format."""
        user = self.get_object()
        serializer = UserRolesUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, error_list in serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )

        user_roles = serializer.validated_data['userRoles']

        # Get or create groups for the role names (only enabled roles)
        groups = []
        for role_item in user_roles:
            role_name = role_item['roleName']
            enabled = role_item.get('enabled', True)
            
            if enabled:
                # Only add groups that are enabled
                group, created = Group.objects.get_or_create(name=role_name)
                groups.append(group)

        # Assign groups to user (replace existing)
        user.groups.set(groups)

        return create_success_response(
            data='Roles updated successfully'
        )

    @extend_schema(
        tags=['Users'],
        operation_id='users_permissions',
        summary='Get user permissions',
        responses={
            'default': {
                'description': 'Error response',
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
    @action(detail=True, methods=['get'], url_path='permissions')
    def permissions(self, request, pk=None):
        """Get permissions for a specific user. Returns format matching old Swagger."""
        user = self.get_object()

        # Get user permissions (select same fields to avoid UNION column mismatch)
        user_permissions = list(user.user_permissions.all().values_list('codename', flat=True))

        # Get group permissions (select same fields to avoid UNION column mismatch)
        group_permissions = list(Permission.objects.filter(group__user=user).distinct().values_list('codename', flat=True))

        # Combine using set to avoid duplicates, then convert to list
        all_permission_codenames = set(user_permissions + group_permissions)

        # If no explicit permissions found, return default permissions based on user role
        # The old Swagger returns permissions based on user roles (Manager, Admin, etc.)
        if not all_permission_codenames:
            # Define default permissions based on role (matching old Swagger format)
            default_permissions = []
            
            if user.is_superuser:
                # Admin has all permissions
                default_permissions = [
                    'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                    'Permissions.TransactionWallet.Register', 'Permissions.TransactionWallet.Update',
                    'Permissions.TransactionWallet.Remove',
                    'Permissions.Users.View', 'Permissions.Users.Search', 'Permissions.Users.Register',
                    'Permissions.Users.Update', 'Permissions.Users.Remove',
                    'Permissions.Products.View', 'Permissions.Products.Search',
                    'Permissions.Products.Register', 'Permissions.Products.Update',
                    'Permissions.Products.Remove',
                    'Permissions.Brands.View', 'Permissions.Brands.Search',
                    'Permissions.Orders.View', 'Permissions.Orders.Search',
                    'Permissions.Orders.Register', 'Permissions.Orders.Update',
                    'Permissions.Orders.Remove',
                    'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                    'Permissions.SubUser.View', 'Permissions.SubUser.Search',
                    'Permissions.SubUser.Register', 'Permissions.Trip.View',
                    'Permissions.Trip.Search', 'Permissions.Trip.Register',
                    'Permissions.Trip.Update', 'Permissions.Trip.Remove',
                    'Permissions.NotificationMessages.View', 'Permissions.NotificationMessages.Search',
                    'Permissions.NotificationMessages.Register', 'Permissions.NotificationMessages.Update',
                    'Permissions.NotificationMessages.Remove',
                ]
            elif user.is_staff:
                # Manager has most permissions
                default_permissions = [
                    'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                    'Permissions.Products.View', 'Permissions.Products.Search',
                    'Permissions.Products.Update', 'Permissions.Brands.View',
                    'Permissions.Brands.Search', 'Permissions.Orders.View',
                    'Permissions.Orders.Search', 'Permissions.Orders.Update',
                    'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                    'Permissions.Trip.View', 'Permissions.Trip.Search',
                    'Permissions.Trip.Update', 'Permissions.NotificationMessages.View',
                    'Permissions.NotificationMessages.Search',
                ]
            elif hasattr(user, 'is_driver') and user.is_driver:
                # Driver has limited permissions
                default_permissions = [
                    'Permissions.Orders.View', 'Permissions.Orders.Search',
                    'Permissions.Orders.Update', 'Permissions.Trip.View',
                    'Permissions.Trip.Search', 'Permissions.MapZone.View',
                ]
            else:
                # Customer has very limited permissions
                default_permissions = [
                    'Permissions.Orders.View', 'Permissions.Products.View',
                ]
            
            # Check user groups for additional role-based permissions
            user_groups = user.groups.all()
            if user_groups:
                group_names = [g.name.lower() for g in user_groups]
                if 'admin' in group_names:
                    default_permissions = [
                        'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                        'Permissions.TransactionWallet.Register', 'Permissions.TransactionWallet.Update',
                        'Permissions.TransactionWallet.Remove',
                        'Permissions.Users.View', 'Permissions.Users.Search',
                        'Permissions.Users.Register', 'Permissions.Users.Update',
                        'Permissions.Users.Remove',
                        'Permissions.Products.View', 'Permissions.Products.Search',
                        'Permissions.Products.Register', 'Permissions.Products.Update',
                        'Permissions.Products.Remove',
                        'Permissions.Brands.View', 'Permissions.Brands.Search',
                        'Permissions.Orders.View', 'Permissions.Orders.Search',
                        'Permissions.Orders.Register', 'Permissions.Orders.Update',
                        'Permissions.Orders.Remove',
                        'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                        'Permissions.SubUser.View', 'Permissions.SubUser.Search',
                        'Permissions.SubUser.Register', 'Permissions.Trip.View',
                        'Permissions.Trip.Search', 'Permissions.Trip.Register',
                        'Permissions.Trip.Update', 'Permissions.Trip.Remove',
                        'Permissions.NotificationMessages.View', 'Permissions.NotificationMessages.Search',
                        'Permissions.NotificationMessages.Register', 'Permissions.NotificationMessages.Update',
                        'Permissions.NotificationMessages.Remove',
                    ]
                elif 'manager' in group_names:
                    default_permissions = [
                        'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                        'Permissions.Products.View', 'Permissions.Products.Search',
                        'Permissions.Products.Update', 'Permissions.Brands.View',
                        'Permissions.Brands.Search', 'Permissions.Orders.View',
                        'Permissions.Orders.Search', 'Permissions.Orders.Update',
                        'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                        'Permissions.Trip.View', 'Permissions.Trip.Search',
                        'Permissions.Trip.Update', 'Permissions.NotificationMessages.View',
                        'Permissions.NotificationMessages.Search',
                    ]
                elif 'driver' in group_names:
                    default_permissions = [
                        'Permissions.Orders.View', 'Permissions.Orders.Search',
                        'Permissions.Orders.Update', 'Permissions.Trip.View',
                        'Permissions.Trip.Search', 'Permissions.MapZone.View',
                    ]
            
            # Use default permissions (already in old Swagger format)
            all_permission_codenames = set(default_permissions)

        # Format permissions to match old Swagger format: { "permission": "...", "description": null }
        # Old Swagger format: "Permissions.{Resource}.{Action}"
        # Example: "Permissions.TransactionWallet.View"
        def format_permission_name(codename):
            """Convert Django permission codename to old Swagger format."""
            # If already in old format, return as is
            if codename.startswith("Permissions."):
                return codename
            
            # Try to parse Django format and convert
            # Common patterns: "view_transactionwallet", "transactionwallet.view", "view_transaction_wallet"
            parts = codename.split('_')
            if len(parts) >= 2:
                # Pattern: "view_transactionwallet" -> "Permissions.TransactionWallet.View"
                action = parts[0].capitalize()
                resource_parts = parts[1:]
                # Handle camelCase conversion: "transaction_wallet" -> "TransactionWallet"
                resource = ''.join(word.capitalize() for word in resource_parts)
                return f"Permissions.{resource}.{action}"
            elif '.' in codename:
                # Pattern: "transactionwallet.view" -> "Permissions.TransactionWallet.View"
                resource, action = codename.split('.', 1)
                resource = ''.join(word.capitalize() for word in resource.split('_'))
                action = action.capitalize()
                return f"Permissions.{resource}.{action}"
            else:
                # Fallback: just prefix with "Permissions."
                return f"Permissions.{codename}"

        permissions_data = []
        for codename in sorted(all_permission_codenames):
            # If codename is already in old Swagger format, use it directly
            # Otherwise, format it
            if codename.startswith("Permissions."):
                permission_name = codename
            else:
                permission_name = format_permission_name(codename)
            
            permissions_data.append({
                'permission': permission_name,
                'description': None
            })

        # Debug: Log if no permissions found
        if not permissions_data:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No permissions found for user {user.id} ({user.email}). "
                         f"User is_superuser: {user.is_superuser}, is_staff: {user.is_staff}, "
                         f"groups: {list(user.groups.values_list('name', flat=True))}")

        return create_success_response(data=permissions_data)


# Direct views for list and retrieve (to avoid router API root view)
@extend_schema(
    tags=['Users'],
    operation_id='users_list_direct',
    summary='List all users',
    responses={
        200: OpenApiResponse(
            response=UserListResponseSerializer,
            description='List of users',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 'string',
                                'userName': 'string',
                                'firstName': 'string',
                                'lastName': 'string',
                                'email': 'string',
                                'isActive': True,
                                'createDate': '2025-11-07T18:07:58.653Z',
                                'middleName': 'string',
                                'gender': 0,
                                'title': 'string',
                                'info': 'string',
                                'emailConfirmed': True,
                                'phoneNumberConfirmed': True,
                                'phoneNumber': 'string',
                                'imageUrl': 'string',
                                'thumbnail': 'string',
                                'companyName': 'string',
                                'companyNumber': 'string',
                                'code': 'string',
                                'codeType': 0,
                                'companyId': 0,
                                'jsonExt': 'string',
                                'vatNumber': 'string',
                                'representative': 'string',
                                'sheba': 'string',
                                'bankname': 'string',
                                'birthdate': '2025-11-07T18:07:58.653Z',
                                'codeMeli': 'string',
                                'representativeBy': 'string',
                                'representativeDate': '2025-11-07T18:07:58.653Z',
                                'blueUser': True,
                                'blueUSerActiveDate': '2025-11-07T18:07:58.653Z',
                                'issue': 'string',
                                'rolesRequests': 'string',
                                'instagram': 'string',
                                'facebook': 'string',
                                'linkedIn': 'string',
                                'twitter': 'string',
                                'gitHub': 'string',
                                'skype': 'string',
                                'telegram': 'string',
                                'whatsApp': 'string',
                                'follower': 0,
                                'following': 0
                            }
                        ]
                    }
                )
            ]
        ),
        'default': {
            'description': 'Error response',
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
        },
        401: {
            'description': 'Unauthorized',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['Authentication credentials were not provided.'],
                        'succeeded': False,
                        'data': None,
                        'source': None,
                        'exception': 'Authentication credentials were not provided.',
                        'errorId': None,
                        'supportMessage': None,
                        'statusCode': 401
                    }
                }
            }
        },
        403: {
            'description': 'Forbidden',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['You do not have permission to perform this action.'],
                        'succeeded': False,
                        'data': None,
                        'source': None,
                        'exception': 'You do not have permission to perform this action.',
                        'errorId': None,
                        'supportMessage': None,
                        'statusCode': 403
                    }
                }
            }
        }
    }
)
class UsersListView(APIView):
    """GET /api/v1/users - List all users (direct view to avoid router API root)."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        """List all users in old Swagger format."""
        queryset = User.objects.all()
        serializer = UserCompatibilitySerializer(queryset, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Users'],
    operation_id='users_retrieve_direct',
    summary='Retrieve a user by ID',
    responses={
        200: OpenApiResponse(
            response=UserDetailResponseSerializer,
            description='User details',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': {
                            'id': 'string',
                            'userName': 'string',
                            'firstName': 'string',
                            'lastName': 'string',
                            'email': 'string',
                            'isActive': True,
                            'createDate': '2025-11-07T18:07:58.653Z',
                            'middleName': 'string',
                            'gender': 0,
                            'title': 'string',
                            'info': 'string',
                            'emailConfirmed': True,
                            'phoneNumberConfirmed': True,
                            'phoneNumber': 'string',
                            'imageUrl': 'string',
                            'thumbnail': 'string',
                            'companyName': 'string',
                            'companyNumber': 'string',
                            'code': 'string',
                            'codeType': 0,
                            'companyId': 0,
                            'jsonExt': 'string',
                            'vatNumber': 'string',
                            'representative': 'string',
                            'sheba': 'string',
                            'bankname': 'string',
                            'birthdate': '2025-11-07T18:07:58.653Z',
                            'codeMeli': 'string',
                            'representativeBy': 'string',
                            'representativeDate': '2025-11-07T18:07:58.653Z',
                            'blueUser': True,
                            'blueUSerActiveDate': '2025-11-07T18:07:58.653Z',
                            'issue': 'string',
                            'rolesRequests': 'string',
                            'instagram': 'string',
                            'facebook': 'string',
                            'linkedIn': 'string',
                            'twitter': 'string',
                            'gitHub': 'string',
                            'skype': 'string',
                            'telegram': 'string',
                            'whatsApp': 'string',
                            'follower': 0,
                            'following': 0
                        }
                    }
                )
            ]
        ),
        'default': {
            'description': 'Error response',
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
        },
        404: {
            'description': 'User not found',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['User not found'],
                        'succeeded': False,
                        'data': None,
                        'source': None,
                        'exception': 'User not found',
                        'errorId': None,
                        'supportMessage': None,
                        'statusCode': 404
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['Authentication credentials were not provided.'],
                        'succeeded': False,
                        'data': None,
                        'source': None,
                        'exception': 'Authentication credentials were not provided.',
                        'errorId': None,
                        'supportMessage': None,
                        'statusCode': 401
                    }
                }
            }
        },
        403: {
            'description': 'Forbidden',
            'content': {
                'application/json': {
                    'example': {
                        'messages': ['You do not have permission to perform this action.'],
                        'succeeded': False,
                        'data': None,
                        'source': None,
                        'exception': 'You do not have permission to perform this action.',
                        'errorId': None,
                        'supportMessage': None,
                        'statusCode': 403
                    }
                }
            }
        }
    }
)
class UsersRetrieveView(APIView):
    """GET /api/v1/users/{id} - Retrieve a user by ID (direct view)."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request, pk):
        """Retrieve a user by ID in old Swagger format."""
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return create_error_response(
                error_message='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = UserCompatibilitySerializer(user, context={'request': request})
        return create_success_response(data=serializer.data)


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Users'],
    responses={
        'default': {
            'description': 'Error response',
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
class UsersUserSearchView(APIView):
    """POST /api/v1/users/usersearch"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """User search endpoint (alternative to /search)."""
        # Reuse search logic
        viewset = UsersViewSet()
        viewset.request = request
        return viewset.search(request)


@extend_schema(
    tags=['Users'],
    operation_id='users_client_searchsp',
    summary='Search users (client) using stored procedure',
    request=UserSearchSPRequestSerializer,
    examples=[
        OpenApiExample(
            'Client Search Request (default)',
            value={
                "advancedSearch": {
                    "fields": [
                        "string"
                    ],
                    "keyword": "string",
                    "groupBy": [
                        "string"
                    ]
                },
                "keyword": "string",
                "pageNumber": 0,
                "pageSize": 0,
                "orderBy": [
                    "string"
                ],
                "isActive": True,
                "roleId": "string",
                "rolesRequests": "string",
                "companyId": 0,
                "hasIssue": True,
                "userName": "string",
                "email": "string",
                "city": "string",
                "country": "string",
                "phoneNumber": "string"
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Client search results with nested pagination',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        "data": {
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 1,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        ),
        'default': {
            'description': 'Error response',
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
class UsersClientSearchSPView(APIView):
    """POST /api/v1/users/client/searchsp"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Client search users using stored procedure matching old Swagger format."""
        # Get search parameters
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        
        # Build query
        qs = User.objects.all()
        
        if keyword:
            # Search in username, email, phone, full name
            q = Q(username__icontains=keyword) | Q(email__icontains=keyword) | Q(phone_number__icontains=keyword)
            try:
                q = q | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            except:
                pass
            qs = qs.filter(q)
        
        # Apply filters
        if request.data.get('isActive') is not None:
            qs = qs.filter(is_active=request.data.get('isActive'))
        if request.data.get('userName'):
            qs = qs.filter(username__icontains=request.data.get('userName'))
        if request.data.get('email'):
            qs = qs.filter(email__icontains=request.data.get('email'))
        if request.data.get('phoneNumber'):
            qs = qs.filter(phone_number__icontains=request.data.get('phoneNumber'))
        
        qs = qs.order_by('-created_at')
        
        # Calculate pagination
        total_count = qs.count()
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        current_page = page_number
        has_previous_page = current_page > 1
        has_next_page = current_page < total_pages
        
        # Get paginated items
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        # Serialize with UserCompatibilitySerializer
        serializer = UserCompatibilitySerializer(items, many=True, context={'request': request})
        
        # Return in nested format matching old Swagger
        # Structure: { "data": { "data": [...], "currentPage": ..., ... }, "messages": [], "succeeded": true }
        nested_data = {
            'data': serializer.data,
            'currentPage': current_page,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous_page,
            'hasNextPage': has_next_page,
            'messages': None,
            'succeeded': True
        }
        
        response_data = {
            'data': nested_data,
            'messages': [],
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Users'],
    responses={
        'default': {
            'description': 'Error response',
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
class UsersClientPermissionsView(APIView):
    """GET /api/v1/users/client/permissions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get permissions for the currently logged-in user. Returns format matching old Swagger."""
        user = request.user

        # Get user permissions (select same fields to avoid UNION column mismatch)
        user_permissions = list(user.user_permissions.all().values_list('codename', flat=True))

        # Get group permissions (select same fields to avoid UNION column mismatch)
        group_permissions = list(Permission.objects.filter(group__user=user).distinct().values_list('codename', flat=True))

        # Combine using set to avoid duplicates, then convert to list
        all_permission_codenames = set(user_permissions + group_permissions)

        # If no explicit permissions found, return default permissions based on user role
        if not all_permission_codenames:
            # Define default permissions based on role (matching old Swagger format)
            default_permissions = []
            
            if user.is_superuser:
                # Admin has all permissions
                default_permissions = [
                    'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                    'Permissions.TransactionWallet.Register', 'Permissions.TransactionWallet.Update',
                    'Permissions.TransactionWallet.Remove',
                    'Permissions.Users.View', 'Permissions.Users.Search', 'Permissions.Users.Register',
                    'Permissions.Users.Update', 'Permissions.Users.Remove',
                    'Permissions.Products.View', 'Permissions.Products.Search',
                    'Permissions.Products.Register', 'Permissions.Products.Update',
                    'Permissions.Products.Remove',
                    'Permissions.Brands.View', 'Permissions.Brands.Search',
                    'Permissions.Orders.View', 'Permissions.Orders.Search',
                    'Permissions.Orders.Register', 'Permissions.Orders.Update',
                    'Permissions.Orders.Remove',
                    'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                    'Permissions.SubUser.View', 'Permissions.SubUser.Search',
                    'Permissions.SubUser.Register', 'Permissions.Trip.View',
                    'Permissions.Trip.Search', 'Permissions.Trip.Register',
                    'Permissions.Trip.Update', 'Permissions.Trip.Remove',
                    'Permissions.NotificationMessages.View', 'Permissions.NotificationMessages.Search',
                    'Permissions.NotificationMessages.Register', 'Permissions.NotificationMessages.Update',
                    'Permissions.NotificationMessages.Remove',
                ]
            elif user.is_staff:
                # Manager has most permissions
                default_permissions = [
                    'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                    'Permissions.Products.View', 'Permissions.Products.Search',
                    'Permissions.Products.Update', 'Permissions.Brands.View',
                    'Permissions.Brands.Search', 'Permissions.Orders.View',
                    'Permissions.Orders.Search', 'Permissions.Orders.Update',
                    'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                    'Permissions.Trip.View', 'Permissions.Trip.Search',
                    'Permissions.Trip.Update', 'Permissions.NotificationMessages.View',
                    'Permissions.NotificationMessages.Search',
                ]
            elif hasattr(user, 'is_driver') and user.is_driver:
                # Driver has limited permissions
                default_permissions = [
                    'Permissions.Orders.View', 'Permissions.Orders.Search',
                    'Permissions.Orders.Update', 'Permissions.Trip.View',
                    'Permissions.Trip.Search', 'Permissions.MapZone.View',
                ]
            else:
                # Customer has very limited permissions
                default_permissions = [
                    'Permissions.Orders.View', 'Permissions.Products.View',
                ]
            
            # Check user groups for additional role-based permissions
            user_groups = user.groups.all()
            if user_groups:
                group_names = [g.name.lower() for g in user_groups]
                if 'admin' in group_names:
                    default_permissions = [
                        'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                        'Permissions.TransactionWallet.Register', 'Permissions.TransactionWallet.Update',
                        'Permissions.TransactionWallet.Remove',
                        'Permissions.Users.View', 'Permissions.Users.Search',
                        'Permissions.Users.Register', 'Permissions.Users.Update',
                        'Permissions.Users.Remove',
                        'Permissions.Products.View', 'Permissions.Products.Search',
                        'Permissions.Products.Register', 'Permissions.Products.Update',
                        'Permissions.Products.Remove',
                        'Permissions.Brands.View', 'Permissions.Brands.Search',
                        'Permissions.Orders.View', 'Permissions.Orders.Search',
                        'Permissions.Orders.Register', 'Permissions.Orders.Update',
                        'Permissions.Orders.Remove',
                        'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                        'Permissions.SubUser.View', 'Permissions.SubUser.Search',
                        'Permissions.SubUser.Register', 'Permissions.Trip.View',
                        'Permissions.Trip.Search', 'Permissions.Trip.Register',
                        'Permissions.Trip.Update', 'Permissions.Trip.Remove',
                        'Permissions.NotificationMessages.View', 'Permissions.NotificationMessages.Search',
                        'Permissions.NotificationMessages.Register', 'Permissions.NotificationMessages.Update',
                        'Permissions.NotificationMessages.Remove',
                    ]
                elif 'manager' in group_names:
                    default_permissions = [
                        'Permissions.TransactionWallet.View', 'Permissions.TransactionWallet.Search',
                        'Permissions.Products.View', 'Permissions.Products.Search',
                        'Permissions.Products.Update', 'Permissions.Brands.View',
                        'Permissions.Brands.Search', 'Permissions.Orders.View',
                        'Permissions.Orders.Search', 'Permissions.Orders.Update',
                        'Permissions.MapZone.View', 'Permissions.MapZone.Search',
                        'Permissions.Trip.View', 'Permissions.Trip.Search',
                        'Permissions.Trip.Update', 'Permissions.NotificationMessages.View',
                        'Permissions.NotificationMessages.Search',
                    ]
                elif 'driver' in group_names:
                    default_permissions = [
                        'Permissions.Orders.View', 'Permissions.Orders.Search',
                        'Permissions.Orders.Update', 'Permissions.Trip.View',
                        'Permissions.Trip.Search', 'Permissions.MapZone.View',
                    ]
            
            # Use default permissions (already in old Swagger format)
            all_permission_codenames = set(default_permissions)

        # Format permissions to match old Swagger format: { "permission": "...", "description": null }
        def format_permission_name(codename):
            """Convert Django permission codename to old Swagger format."""
            # If already in old format, return as is
            if codename.startswith("Permissions."):
                return codename
            
            # Try to parse Django format and convert
            parts = codename.split('_')
            if len(parts) >= 2:
                action = parts[0].capitalize()
                resource_parts = parts[1:]
                resource = ''.join(word.capitalize() for word in resource_parts)
                return f"Permissions.{resource}.{action}"
            elif '.' in codename:
                resource, action = codename.split('.', 1)
                resource = ''.join(word.capitalize() for word in resource.split('_'))
                action = action.capitalize()
                return f"Permissions.{resource}.{action}"
            else:
                return f"Permissions.{codename}"

        permissions_data = []
        for codename in sorted(all_permission_codenames):
            if codename.startswith("Permissions."):
                permission_name = codename
            else:
                permission_name = format_permission_name(codename)
            
            permissions_data.append({
                'permission': permission_name,
                'description': None
            })

        return create_success_response(data=permissions_data)

