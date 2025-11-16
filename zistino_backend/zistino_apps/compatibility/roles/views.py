"""
Views for Roles compatibility layer.
Implements all endpoints matching old Swagger format.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from .models import Role
from .serializers import (
    RoleCreateUpdateRequestSerializer,
    RoleListSerializer,
    RoleSearchRequestSerializer,
    RoleListRequestSerializer,
    RolePermissionsRequestSerializer,
)


@extend_schema(tags=['Roles'])
class RolesViewSet(viewsets.ViewSet):
    """
    ViewSet for Roles endpoints.
    All endpoints will appear under "Roles" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated, IsManager]

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_create',
        summary='Create or update a role',
        description='Creates a new role or updates existing one if ID is provided.',
        request=RoleCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create/Update Role (default)',
                value={
                    "id": "string",
                    "name": "string",
                    "description": "string"
                }
            ),
            OpenApiExample(
                'Create/Update Role (actual)',
                value={
                    "id": "0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea",
                    "name": "akmal",
                    "description": "asd"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=RoleCreateUpdateRequestSerializer,
                description='Role created or updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": "0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea",
                            "messages": [
                                "Role akmal Updated. [en-US]"
                            ],
                            "succeeded": True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            500: {'description': 'Server error'}
        }
    )
    def create(self, request):
        """Create or update a role matching old Swagger format."""
        try:
            serializer = RoleCreateUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            role_id = validated_data.get('id')
            name = validated_data.get('name')
            description = validated_data.get('description', '')
            
            # If ID is provided, try to update existing role
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                    role.name = name
                    role.description = description
                    role.save()
                    action_message = f'Role {name} Updated. [en-US]'
                except Role.DoesNotExist:
                    # If role doesn't exist, create new one with provided ID
                    role = Role.objects.create(
                        id=role_id,
                        name=name,
                        description=description,
                        tenant='root'
                    )
                    action_message = f'Role {name} Created. [en-US]'
            else:
                # Create new role without ID (will auto-generate UUID)
                role = Role.objects.create(
                    name=name,
                    description=description,
                    tenant='root'
                )
                action_message = f'Role {name} Created. [en-US]'
            
            return create_success_response(
                data=str(role.id),
                messages=[action_message]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating/updating role: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_retrieve',
        summary='Retrieve a role by ID',
    )
    def retrieve(self, request, pk=None):
        """Retrieve a role by ID."""
        try:
            role = Role.objects.get(id=pk)
            serializer = RoleListSerializer(role)
            return create_success_response(data=serializer.data, messages=[])
        except Role.DoesNotExist:
            return create_error_response(
                error_message=f'Role with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Role with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_destroy',
        summary='Delete a role',
    )
    def destroy(self, request, pk=None):
        """Delete a role."""
        try:
            role = Role.objects.get(id=pk)
            role.delete()
            return create_success_response(data=str(pk), messages=[])
        except Role.DoesNotExist:
            return create_error_response(
                error_message=f'Role with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Role with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_search',
        summary='Search roles using available filters',
        description='Search roles with pagination, keyword search, and ordering matching old Swagger format.',
        request=RoleSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request',
                value={
                    "advancedSearch": {
                        "fields": ["string"],
                        "keyword": "string",
                        "groupBy": ["string"]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": ["string"]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=RoleListSerializer,
                description='Paginated list of roles',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 100,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search roles matching old Swagger format."""
        try:
            serializer = RoleSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Handle pagination defaults (0 means use defaults)
            if page_number == 0:
                page_number = 1
            if page_size == 0:
                page_size = 100
            
            # Start with all roles
            queryset = Role.objects.all()
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '')
            advanced_search = validated_data.get('advancedSearch')
            
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '')
            
            if keyword:
                queryset = queryset.filter(
                    Q(name__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out empty strings and validate fields
                valid_order_fields = []
                valid_fields = ['name', 'description', 'tenant', 'created_at', 'updated_at']
                for field in order_by:
                    if field and field.strip():
                        # Remove '-' prefix if present for validation
                        field_name = field.lstrip('-')
                        if field_name in valid_fields:
                            valid_order_fields.append(field)
                
                if valid_order_fields:
                    queryset = queryset.order_by(*valid_order_fields)
                else:
                    queryset = queryset.order_by('name')
            else:
                queryset = queryset.order_by('name')
            
            # Paginate
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            total_count = paginator.count
            
            # Get page
            if page_number > total_pages:
                page_number = total_pages if total_pages > 0 else 1
            
            page = paginator.get_page(page_number)
            roles_data = [RoleListSerializer(role).data for role in page]
            
            return create_success_response(
                data=roles_data,
                pagination={
                    'currentPage': page_number,
                    'totalPages': total_pages,
                    'totalCount': total_count,
                    'pageSize': page_size,
                    'hasPreviousPage': page.has_previous(),
                    'hasNextPage': page.has_next()
                }
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching roles: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_rolelist',
        summary='Get list of roles',
        description='Get list of roles with pagination, keyword search, and ordering matching old Swagger format.',
        request=RoleListRequestSerializer,
        examples=[
            OpenApiExample(
                'Role List Request',
                value={
                    "advancedSearch": {
                        "fields": ["string"],
                        "keyword": "string",
                        "groupBy": ["string"]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": ["string"]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=RoleListSerializer,
                description='Paginated list of roles',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 100,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='rolelist')
    def rolelist(self, request):
        """Get list of roles matching old Swagger format."""
        try:
            serializer = RoleListRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Handle pagination defaults (0 means use defaults)
            if page_number == 0:
                page_number = 1
            if page_size == 0:
                page_size = 100
            
            # Start with all roles
            queryset = Role.objects.all()
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '')
            advanced_search = validated_data.get('advancedSearch')
            
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '')
            
            if keyword:
                queryset = queryset.filter(
                    Q(name__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out empty strings and validate fields
                valid_order_fields = []
                valid_fields = ['name', 'description', 'tenant', 'created_at', 'updated_at']
                for field in order_by:
                    if field and field.strip():
                        # Remove '-' prefix if present for validation
                        field_name = field.lstrip('-')
                        if field_name in valid_fields:
                            valid_order_fields.append(field)
                
                if valid_order_fields:
                    queryset = queryset.order_by(*valid_order_fields)
                else:
                    queryset = queryset.order_by('name')
            else:
                queryset = queryset.order_by('name')
            
            # Paginate
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            total_count = paginator.count
            
            # Get page
            if page_number > total_pages:
                page_number = total_pages if total_pages > 0 else 1
            
            page = paginator.get_page(page_number)
            roles_data = [RoleListSerializer(role).data for role in page]
            
            return create_success_response(
                data=roles_data,
                pagination={
                    'currentPage': page_number,
                    'totalPages': total_pages,
                    'totalCount': total_count,
                    'pageSize': page_size,
                    'hasPreviousPage': page.has_previous(),
                    'hasNextPage': page.has_next()
                }
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting role list: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_permissions',
        summary='Get permissions for a role',
        description='Returns permissions assigned to a specific role.',
        responses={
            200: OpenApiResponse(
                response=list,
                description='List of permissions for the role',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [],
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Role not found'}
        }
    )
    @action(detail=True, methods=['get'], url_path='permissions')
    def permissions(self, request, pk=None):
        """Get permissions for a role matching old Swagger format."""
        try:
            role = Role.objects.get(id=pk)
            # TODO: Implement actual permission retrieval from RolePermission model
            # For now, return empty array matching old Swagger format
            return create_success_response(
                data=[],
                messages=[]
            )
        except Role.DoesNotExist:
            return create_error_response(
                error_message=f'Role with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Role with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Roles'],
        operation_id='roles_update_permissions',
        summary='Update permissions for a role',
        description='Updates permissions assigned to a specific role.',
        request=RolePermissionsRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=list,
                description='Updated permissions for the role',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [],
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Role not found'}
        }
    )
    @action(detail=True, methods=['put'], url_path='permissions')
    def update_permissions(self, request, pk=None):
        """Update permissions for a role matching old Swagger format."""
        try:
            role = Role.objects.get(id=pk)
            serializer = RolePermissionsRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # TODO: Implement actual permission update logic
            # For now, return success response matching old Swagger format
            return create_success_response(
                data=[],
                messages=[]
            )
        except Role.DoesNotExist:
            return create_error_response(
                error_message=f'Role with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Role with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Roles'],
    operation_id='roles_count',
    summary='Get total count of roles',
    description='Returns the total count of roles as a plain number (not wrapped).',
    responses={
        200: OpenApiResponse(
            response=int,
            description='Total count of roles',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value=22
                )
            ]
        )
    }
)
class RolesCountView(APIView):
    """GET /api/v1/roles/count"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get total count of roles (returns plain number, not wrapped)."""
        try:
            count = Role.objects.count()
            # Old Swagger returns just the number, not wrapped
            return Response(count, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Roles'],
    operation_id='roles_all',
    summary='Get all roles',
    description='Returns paginated list of all roles matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=RoleListSerializer,
            description='List of roles',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "id": "0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea",
                                "name": "انباردار",
                                "description": "توضحیح",
                                "tenant": "root"
                            },
                            {
                                "id": "143ea6f0-366b-476b-9790-b8572b858fe6",
                                "name": "marketers",
                                "description": "marketers",
                                "tenant": "root"
                            }
                        ],
                        "currentPage": 1,
                        "totalPages": 1,
                        "totalCount": 22,
                        "pageSize": 100,
                        "hasPreviousPage": False,
                        "hasNextPage": False,
                        "messages": None,
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RolesAllView(APIView):
    """GET /api/v1/roles/all"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get all roles with pagination matching old Swagger format."""
        try:
            # Get pagination parameters
            page_number = int(request.query_params.get('pageNumber', 1))
            page_size = int(request.query_params.get('pageSize', 100))
            
            # Ensure valid pagination
            if page_number < 1:
                page_number = 1
            if page_size < 1:
                page_size = 100
            
            # Get all roles
            roles = Role.objects.all().order_by('name')
            
            # Paginate
            paginator = Paginator(roles, page_size)
            total_pages = paginator.num_pages
            total_count = paginator.count
            
            # Get page
            if page_number > total_pages:
                page_number = total_pages if total_pages > 0 else 1
            
            page = paginator.get_page(page_number)
            roles_data = [RoleListSerializer(role).data for role in page]
            
            return create_success_response(
                data=roles_data,
                pagination={
                    'currentPage': page_number,
                    'totalPages': total_pages,
                    'totalCount': total_count,
                    'pageSize': page_size,
                    'hasPreviousPage': page.has_previous(),
                    'hasNextPage': page.has_next()
                }
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Permission mappings from assign_default_permissions command
# Format: "Permissions.{Resource}.{Action}"
ALL_PERMISSIONS = [
    # TransactionWallet permissions
    'Permissions.TransactionWallet.View',
    'Permissions.TransactionWallet.Search',
    'Permissions.TransactionWallet.Register',
    'Permissions.TransactionWallet.Update',
    'Permissions.TransactionWallet.Remove',
    
    # Users permissions
    'Permissions.Users.View',
    'Permissions.Users.Search',
    'Permissions.Users.Register',
    'Permissions.Users.Update',
    'Permissions.Users.Remove',
    
    # Products permissions
    'Permissions.Products.View',
    'Permissions.Products.Search',
    'Permissions.Products.Register',
    'Permissions.Products.Update',
    'Permissions.Products.Remove',
    
    # Brands permissions
    'Permissions.Brands.View',
    'Permissions.Brands.Search',
    'Permissions.Brands.Register',
    'Permissions.Brands.Update',
    'Permissions.Brands.Remove',
    
    # Orders permissions
    'Permissions.Orders.View',
    'Permissions.Orders.Search',
    'Permissions.Orders.Register',
    'Permissions.Orders.Update',
    'Permissions.Orders.Remove',
    
    # MapZone permissions
    'Permissions.MapZone.View',
    'Permissions.MapZone.Search',
    'Permissions.MapZone.Register',
    'Permissions.MapZone.Update',
    'Permissions.MapZone.Remove',
    
    # SubUser permissions
    'Permissions.SubUser.View',
    'Permissions.SubUser.Search',
    'Permissions.SubUser.Register',
    'Permissions.SubUser.Update',
    'Permissions.SubUser.Remove',
    
    # Trip permissions
    'Permissions.Trip.View',
    'Permissions.Trip.Search',
    'Permissions.Trip.Register',
    'Permissions.Trip.Update',
    'Permissions.Trip.Remove',
    
    # NotificationMessages permissions
    'Permissions.NotificationMessages.View',
    'Permissions.NotificationMessages.Search',
    'Permissions.NotificationMessages.Register',
    'Permissions.NotificationMessages.Update',
    'Permissions.NotificationMessages.Remove',
]


@extend_schema(
    tags=['Roles'],
    operation_id='roles_permissionslist',
    summary='Get list of all available permissions',
    description='Returns all available permissions in the system matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=list,
            description='List of all available permissions',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "permission": "Permissions.Products.View",
                                "description": None
                            },
                            {
                                "permission": "Permissions.Products.Search",
                                "description": None
                            },
                            {
                                "permission": "Permissions.Products.Register",
                                "description": None
                            },
                            {
                                "permission": "Permissions.Products.Update",
                                "description": None
                            }
                        ],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RolesPermissionsListView(APIView):
    """GET /api/v1/roles/permissionslist"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get list of all available permissions matching old Swagger format."""
        try:
            # Return all permissions in the format: {permission: "string", description: null}
            permissions_data = [
                {
                    "permission": perm,
                    "description": None
                }
                for perm in sorted(ALL_PERMISSIONS)
            ]
            
            return create_success_response(
                data=permissions_data,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
