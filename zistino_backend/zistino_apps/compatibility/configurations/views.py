"""
Compatibility views for Configurations endpoints.
All endpoints will appear under "Configurations" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Configurations
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from zistino_apps.configurations.models import Configuration
from zistino_apps.configurations.serializers import ConfigurationSerializer, ConfigRequestSerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    ConfigurationSearchRequestSerializer,
    ConfigurationCreateRequestSerializer
)


@extend_schema(tags=['Configurations'])
class ConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing configurations.
    All endpoints will appear under "Configurations" folder in Swagger UI.
    """
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all configurations."""
        return Configuration.objects.all()

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_create',
        summary='Create a new configuration',
        description='Creates a new configuration matching old Swagger format.',
        request=ConfigurationCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create configuration',
                value={
                    'name': 'string',
                    'type': 0,
                    'value': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Configuration created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 9,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create configuration matching old Swagger format. Returns configuration ID."""
        try:
            # Validate input using old Swagger format serializer
            input_serializer = ConfigurationCreateRequestSerializer(data=request.data)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = input_serializer.validated_data
            
            # Create configuration
            # Convert value string to JSON (or keep as string if it's already JSON)
            value_str = validated_data.get('value', '')
            try:
                import json
                # Try to parse as JSON, if fails, store as string
                value_json = json.loads(value_str) if value_str else {}
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, store as string in a dict
                value_json = {'value': value_str}
            
            try:
                configuration = Configuration.objects.create(
                    name=validated_data.get('name'),
                    type=validated_data.get('type', 0),
                    value=value_json,
                    is_active=True
                )
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    if 'UNIQUE constraint' in error_detail or 'unique constraint' in error_detail.lower() or 'name' in error_detail.lower():
                        return create_error_response(
                            error_message=f'A configuration with name "{validated_data.get("name")}" already exists.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'name': [f'A configuration with name "{validated_data.get("name")}" already exists.']}
                        )
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'configuration': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while creating the configuration: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return just the configuration ID wrapped in standard response
            return create_success_response(data=configuration.id)  # 200 OK to match old Swagger
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_search',
        summary='Search Configurations using available Filters',
        description='Search Configurations using available Filters matching old Swagger format.',
        request=ConfigurationSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search configurations',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'string',
                        'groupBy': ['string']
                    },
                    'keyword': 'string',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string']
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Paginated search results',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [],
                            'currentPage': 1,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 1,
                            'hasPreviousPage': False,
                            'hasNextPage': False,
                            'messages': None,
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search configurations with pagination (admin) matching old Swagger format."""
        try:
            # Validate input
            serializer = ConfigurationSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters (can be 0)
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Get keyword from request or advancedSearch
            keyword = validated_data.get('keyword') or ''
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword') or keyword
            
            # Build query
            qs = Configuration.objects.all()
            
            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(name__icontains=keyword.strip())
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by and any(order_by):  # If orderBy has non-empty values
                # Validate fields exist in Configuration model
                valid_fields = ['id', 'name', 'type', 'is_active', 'created_at', 'updated_at']
                order_fields = []
                invalid_fields = []
                
                for field in order_by:
                    if field and field.strip():
                        # Remove leading minus for validation
                        field_name = field.strip().lstrip('-')
                        # Map old Swagger field names to Django field names
                        field_mapping = {
                            'createdAt': 'created_at',
                            'updatedAt': 'updated_at',
                            'isActive': 'is_active',
                        }
                        django_field = field_mapping.get(field_name, field_name)
                        if django_field in valid_fields:
                            # Add minus back if it was there
                            if field.strip().startswith('-'):
                                order_fields.append(f'-{django_field}')
                            else:
                                order_fields.append(django_field)
                        else:
                            invalid_fields.append(field.strip())
                
                if invalid_fields:
                    return create_error_response(
                        error_message=f'Invalid orderBy fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'orderBy': [f'Invalid fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}']}
                    )
                
                if order_fields:
                    try:
                        qs = qs.order_by(*order_fields)
                    except Exception:
                        # If ordering fails, use default
                        qs = qs.order_by('name')
                else:
                    qs = qs.order_by('name')
            else:
                # Default ordering
                qs = qs.order_by('name')
            
            # Get total count
            total_count = qs.count()
            
            # Calculate pagination
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
                # Handle pageNumber 0 - treat as page 1
                effective_page = page_number if page_number > 0 else 1
                start = (effective_page - 1) * page_size
                end = start + page_size
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                start = 0
                end = None
                has_previous = False
                has_next = False
            
            # Get paginated results
            if end is not None:
                items = qs[start:end]
            else:
                items = qs[start:]
            
            # Serialize results
            item_serializer = ConfigurationSerializer(items, many=True, context={'request': request})
            items_data = item_serializer.data
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 1 if empty, as per old Swagger example)
            response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 1)
            
            response_data = {
                'data': items_data,
                'currentPage': effective_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': response_page_size,
                'hasPreviousPage': has_previous,
                'hasNextPage': has_next,
                'messages': None,  # Old Swagger shows null, not empty array
                'succeeded': True
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_retrieve',
        summary='Retrieve a configuration by ID',
        description='Retrieves a configuration by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Configuration ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Configuration details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'delivery_time',
                                'type': 1,
                                'value': {
                                    'start': '09:00',
                                    'end': '18:00',
                                    'split': '30'
                                }
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Configuration not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a configuration by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = ConfigurationSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data)
        except Configuration.DoesNotExist:
            return create_error_response(
                error_message=f'Configuration with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Configuration with ID "{kwargs.get("pk")}" not found.']}
            )

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_update',
        summary='Update a configuration by ID',
        description='Updates an existing configuration by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Configuration ID'
            )
        ],
        request=ConfigurationCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update configuration',
                value={
                    'name': 'delivery_time',
                    'type': 1,
                    'value': '{"start": "09:00", "end": "18:00", "split": "30"}'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Configuration updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'delivery_time',
                                'type': 1,
                                'value': {
                                    'start': '09:00',
                                    'end': '18:00',
                                    'split': '30'
                                }
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Configuration not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a configuration by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input using old Swagger format serializer
            input_serializer = ConfigurationCreateRequestSerializer(data=request.data)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = input_serializer.validated_data
            
            # Update configuration
            # Convert value string to JSON (or keep as string if it's already JSON)
            value_str = validated_data.get('value', '')
            try:
                import json
                # Try to parse as JSON, if fails, store as string
                value_json = json.loads(value_str) if value_str else {}
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, store as string in a dict
                value_json = {'value': value_str}
            
            try:
                instance.name = validated_data.get('name', instance.name)
                instance.type = validated_data.get('type', instance.type)
                instance.value = value_json
                instance.save()
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    if 'UNIQUE constraint' in error_detail or 'unique constraint' in error_detail.lower() or 'name' in error_detail.lower():
                        return create_error_response(
                            error_message=f'A configuration with name "{validated_data.get("name")}" already exists.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'name': [f'A configuration with name "{validated_data.get("name")}" already exists.']}
                        )
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'configuration': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while updating the configuration: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return updated configuration in old Swagger format
            serializer = ConfigurationSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data)
        
        except Configuration.DoesNotExist:
            return create_error_response(
                error_message=f'Configuration with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Configuration with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_destroy',
        summary='Delete a configuration by ID',
        description='Deletes a configuration by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Configuration ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Configuration deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Configuration not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a configuration by ID matching old Swagger format. Returns configuration ID."""
        try:
            instance = self.get_object()
            config_id = instance.id
            instance.delete()  # Hard delete
            return create_success_response(data=config_id)
        except Configuration.DoesNotExist:
            return create_error_response(
                error_message=f'Configuration with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Configuration with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_dapper',
        summary='Get configuration (dapper context)',
        description='Get configuration in dapper context matching old Swagger format. Returns null if no id provided.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Configuration ID (optional)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Configuration data or null',
                examples=[
                    OpenApiExample(
                        'Success response (no id)',
                        value={
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get configuration in dapper context matching old Swagger format. Returns null if no id provided."""
        config_id = request.query_params.get('id')
        
        if config_id:
            try:
                config = Configuration.objects.get(id=config_id, is_active=True)
                serializer = ConfigurationSerializer(config, context={'request': request})
                return create_success_response(data=serializer.data)
            except Configuration.DoesNotExist:
                return create_success_response(data=None)
        
        # If no id provided, return null as per old Swagger
        return create_success_response(data=None)

    @extend_schema(
        tags=['Configurations'],
        operation_id='configurations_client_search',
        summary='Search configurations for client',
        description='Search configurations for client-side use matching old Swagger format.',
        request=ConfigRequestSerializer,
        examples=[
            OpenApiExample(
                'Search by name',
                description='Search configuration by name',
                value={
                    "name": "string",
                    "type": 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Configuration search result',
                examples=[
                    OpenApiExample(
                        'Success response (not found)',
                        value={
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='client/search', permission_classes=[AllowAny])
    def client_search(self, request):
        """Search configurations for client matching old Swagger format. Returns null if not found."""
        try:
            serializer = ConfigRequestSerializer(data=request.data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            data = serializer.validated_data

            queryset = Configuration.objects.filter(is_active=True)

            # Filter by name if provided
            if data.get('name') and data.get('name').strip():
                queryset = queryset.filter(name__icontains=data['name'].strip())

            # Filter by type if provided and not 0
            if data.get('type', 0) > 0:
                queryset = queryset.filter(type=data['type'])

            configs = queryset.order_by('name')
            
            # If no results found, return null as per old Swagger
            if not configs.exists():
                return create_success_response(data=None)
            
            # Return first result (old Swagger returns single config or null)
            config_serializer = ConfigurationSerializer(configs.first(), context={'request': request})
            return create_success_response(data=config_serializer.data)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

