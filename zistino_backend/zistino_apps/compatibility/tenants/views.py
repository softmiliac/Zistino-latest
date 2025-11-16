"""
Views for Tenants compatibility layer.
Implements all endpoints matching old Swagger format.
"""
import uuid
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from .models import Tenant
from .serializers import (
    TenantSerializer,
    TenantCreateRequestSerializer,
    TenantUpgradeRequestSerializer,
)


@extend_schema(tags=['Tenants'])
class TenantsViewSet(viewsets.ViewSet):
    """
    ViewSet for Tenants endpoints.
    All endpoints will appear under "Tenants" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated, IsManager]
    lookup_field = 'key'  # Use 'key' as lookup field instead of 'id'
    lookup_url_kwarg = 'key'  # URL parameter name is 'key'

    @extend_schema(
        tags=['Tenants'],
        operation_id='tenants_list',
        summary='Get all tenants',
        description='Returns all tenants matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=TenantSerializer,
                description='List of all tenants',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [
                                {
                                    "id": "69bb0000-444d-28d2-fca0-08d9c611f02d",
                                    "name": "Root",
                                    "key": "root",
                                    "adminEmail": "admin@root.com",
                                    "connectionString": "Data Source=.;Initial Catalog=RecycleDB;Integrated Security=True;MultipleActiveResultSets=True",
                                    "isActive": True,
                                    "validUpto": "2051-12-23T12:44:19.5932841"
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
    def list(self, request):
        """Get all tenants matching old Swagger format."""
        try:
            tenants = Tenant.objects.all().order_by('name')
            serializer = TenantSerializer(tenants, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tenants'],
        operation_id='tenants_retrieve',
        summary='Get tenant by key',
        description='Retrieves a tenant by key matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='key',
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description='Tenant key (string identifier)',
                examples=[
                    OpenApiExample('Example Key', value='root'),
                    OpenApiExample('Example Key 2', value='akm2'),
                ]
            )
        ],
        responses={
            200: OpenApiResponse(
                response=TenantSerializer,
                description='Tenant details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": "69bb0000-444d-28d2-fca0-08d9c611f02d",
                                "name": "Root",
                                "key": "root",
                                "adminEmail": "admin@root.com",
                                "connectionString": "Data Source=.;Initial Catalog=RecycleDB;Integrated Security=True;MultipleActiveResultSets=True",
                                "isActive": True,
                                "validUpto": "2051-12-23T12:44:19.5932841"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Tenant not found'}
        }
    )
    def retrieve(self, request, key=None):
        """Get tenant by key matching old Swagger format."""
        try:
            # key is passed from URL when lookup_url_kwarg='key'
            if not key:
                return create_error_response(
                    error_message='Tenant key is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'key': ['Tenant key is required.']}
                )
            
            try:
                tenant = Tenant.objects.get(key=key)
            except Tenant.DoesNotExist:
                return create_error_response(
                    error_message=f'Tenant with key "{key}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'key': [f'Tenant with key "{key}" not found.']}
                )
            
            serializer = TenantSerializer(tenant)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tenants'],
        operation_id='tenants_create',
        summary='Create a new tenant',
        description='Creates a new tenant matching old Swagger format.',
        request=TenantCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Tenant (default)',
                value={
                    "name": "string",
                    "key": "string",
                    "adminEmail": "string",
                    "connectionString": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Tenant created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "messages": [
                                "string"
                            ],
                            "succeeded": True,
                            "data": "string"
                        }
                    )
                ]
            ),
            400: {
                'description': 'Validation error',
                'content': {
                    'application/json': {
                        'example': {
                            "messages": ["string"],
                            "succeeded": False,
                            "data": "string",
                            "source": "string",
                            "exception": "string",
                            "errorId": "string",
                            "supportMessage": "string",
                            "statusCode": 400
                        }
                    }
                }
            }
        }
    )
    def create(self, request):
        """Create a new tenant matching old Swagger format."""
        try:
            serializer = TenantCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Check if tenant with same key already exists
            if Tenant.objects.filter(key=validated_data['key']).exists():
                return create_error_response(
                    error_message=f'Tenant with key "{validated_data["key"]}" already exists.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'key': [f'Tenant with key "{validated_data["key"]}" already exists.']}
                )
            
            # Create tenant (ID will be auto-generated UUID)
            tenant = Tenant.objects.create(
                name=validated_data['name'],
                key=validated_data['key'],
                admin_email=validated_data.get('adminEmail') or None,
                connection_string=validated_data.get('connectionString') or None
            )
            
            # Return tenant key as data with success message
            return create_success_response(
                data=tenant.key,
                messages=[f'Tenant {tenant.name} created successfully. [en-US]']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating tenant: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Tenants'],
    operation_id='tenants_upgrade',
    summary='Upgrade subscription of tenant',
    description='Upgrades subscription of tenant by extending expiry date matching old Swagger format.',
    request=TenantUpgradeRequestSerializer,
    examples=[
        OpenApiExample(
            'Upgrade Tenant Request',
            value={
                "tenant": "string",
                "extendedExpiryDate": "2025-11-10T11:45:36.954Z"
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Tenant upgraded successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "messages": [
                            "string"
                        ],
                        "succeeded": True
                    }
                )
            ]
        ),
        400: {
            'description': 'Validation error',
            'content': {
                'application/json': {
                    'example': {
                        "messages": ["string"],
                        "succeeded": False,
                        "data": "string",
                        "source": "string",
                        "exception": "string",
                        "errorId": "string",
                        "supportMessage": "string",
                        "statusCode": 400
                    }
                }
            }
        },
        404: {
            'description': 'Tenant not found',
            'content': {
                'application/json': {
                    'example': {
                        "messages": ["string"],
                        "succeeded": False,
                        "data": "string",
                        "source": "string",
                        "exception": "string",
                        "errorId": "string",
                        "supportMessage": "string",
                        "statusCode": 404
                    }
                }
            }
        }
    }
)
class TenantsUpgradeView(APIView):
    """POST /api/v1/tenants/upgrade - Upgrade Subscription of Tenant"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Upgrade subscription of tenant matching old Swagger format."""
        try:
            serializer = TenantUpgradeRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            tenant_key = validated_data['tenant']
            extended_expiry_date = validated_data['extendedExpiryDate']
            
            # Find tenant by key
            try:
                tenant = Tenant.objects.get(key=tenant_key)
            except Tenant.DoesNotExist:
                return create_error_response(
                    error_message=f'Tenant with key "{tenant_key}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'tenant': [f'Tenant with key "{tenant_key}" not found.']}
                )
            
            # Update extended expiry date
            tenant.extended_expiry_date = extended_expiry_date
            tenant.save()
            
            return create_success_response(
                data=None,
                messages=[f'Tenant {tenant.name} subscription upgraded successfully. [en-US]']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while upgrading tenant: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Tenants'],
    operation_id='tenants_deactivate',
    summary='Deactivate tenant',
    description='Deactivates a tenant by ID matching old Swagger format.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, required=True, description='Tenant ID (UUID)')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Tenant deactivated successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "messages": [
                            "string"
                        ],
                        "succeeded": True
                    }
                )
            ]
        ),
        404: {
            'description': 'Tenant not found',
            'content': {
                'application/json': {
                    'example': {
                        "messages": ["string"],
                        "succeeded": False,
                        "data": "string",
                        "source": "string",
                        "exception": "string",
                        "errorId": "string",
                        "supportMessage": "string",
                        "statusCode": 404
                    }
                }
            }
        }
    }
)
class TenantsDeactivateView(APIView):
    """GET /api/v1/tenants/{id}/deactivate - Deactivate Tenant"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, id):
        """Deactivate tenant matching old Swagger format."""
        try:
            # Try to get by UUID
            try:
                tenant_id = uuid.UUID(str(id))
                tenant = Tenant.objects.get(id=tenant_id)
            except (ValueError, TypeError) as e:
                return create_error_response(
                    error_message=f'Invalid tenant ID format: "{id}". Expected UUID.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'id': [f'Invalid tenant ID format: "{id}". Expected UUID.']}
                )
            except Tenant.DoesNotExist:
                return create_error_response(
                    error_message=f'Tenant with ID "{id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Tenant with ID "{id}" not found.']}
                )
            
            # Deactivate tenant
            tenant.is_active = False
            tenant.save()
            
            return create_success_response(
                data=None,
                messages=[f'Tenant {tenant.name} deactivated successfully. [en-US]']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deactivating tenant: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Tenants'],
    operation_id='tenants_activate',
    summary='Activate tenant',
    description='Activates a tenant by ID matching old Swagger format.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, required=True, description='Tenant ID (UUID)')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Tenant activated successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "messages": [
                            "string"
                        ],
                        "succeeded": True
                    }
                )
            ]
        ),
        404: {
            'description': 'Tenant not found',
            'content': {
                'application/json': {
                    'example': {
                        "messages": ["string"],
                        "succeeded": False,
                        "data": "string",
                        "source": "string",
                        "exception": "string",
                        "errorId": "string",
                        "supportMessage": "string",
                        "statusCode": 404
                    }
                }
            }
        }
    }
)
class TenantsActivateView(APIView):
    """GET /api/v1/tenants/{id}/activate - Activate Tenant"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, id):
        """Activate tenant matching old Swagger format."""
        try:
            # Try to get by UUID
            try:
                tenant_id = uuid.UUID(str(id))
                tenant = Tenant.objects.get(id=tenant_id)
            except (ValueError, TypeError) as e:
                return create_error_response(
                    error_message=f'Invalid tenant ID format: "{id}". Expected UUID.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'id': [f'Invalid tenant ID format: "{id}". Expected UUID.']}
                )
            except Tenant.DoesNotExist:
                return create_error_response(
                    error_message=f'Tenant with ID "{id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Tenant with ID "{id}" not found.']}
                )
            
            # Activate tenant
            tenant.is_active = True
            tenant.save()
            
            return create_success_response(
                data=None,
                messages=[f'Tenant {tenant.name} activated successfully. [en-US]']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while activating tenant: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
