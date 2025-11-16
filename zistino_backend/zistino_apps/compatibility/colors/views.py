"""
Compatibility views for Colors endpoints.
All endpoints will appear under "Colors" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Colors
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from zistino_apps.products.models import Color
from zistino_apps.products.serializers import ColorSerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import ColorCreateRequestSerializer, ColorSearchRequestSerializer


@extend_schema(tags=['Colors'])
class ColorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing colors.
    All endpoints will appear under "Colors" folder in Swagger UI.
    """
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_create',
        summary='Creates a new color',
        description='Creates a new color matching old Swagger format.',
        request=ColorCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create color',
                value={
                    'name': 'string',
                    'code': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Color created successfully',
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
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new color matching old Swagger format. Returns color ID."""
        # Validate input using old Swagger format serializer
        input_serializer = ColorCreateRequestSerializer(data=request.data)
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
        
        # Create color using Django model
        color = Color.objects.create(
            name=validated_data.get('name'),
            code=validated_data.get('code') or '',
            locale=validated_data.get('locale') or 'en'
        )
        
        # Return just the color ID wrapped in standard response
        return create_success_response(data=color.id)  # 200 OK to match old Swagger

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_search',
        summary='Search Colors using available Filters',
        description='Search Colors using available Filters matching old Swagger format.',
        request=ColorSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search colors',
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
                            'pageSize': 10,
                            'hasPreviousPage': False,
                            'hasNextPage': False,
                            'messages': None,
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search colors with pagination matching old Swagger format."""
        try:
            # Handle empty request body - allow it and use defaults
            if not request.data:
                request_data = {}
            else:
                request_data = request.data
            
            # Validate input
            serializer = ColorSearchRequestSerializer(data=request_data)
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
            qs = Color.objects.all()
            
            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(name__icontains=keyword.strip()) |
                    Q(code__icontains=keyword.strip())
                )
            
            # Apply ordering with field validation
            order_by = validated_data.get('orderBy', [])
            if order_by and any(order_by):  # If orderBy has non-empty values
                # Parse orderBy fields (e.g., "name", "-name" for descending)
                # Validate fields exist in Color model
                valid_fields = ['id', 'name', 'code', 'locale']  # Color model fields
                order_fields = []
                invalid_fields = []
                
                for field in order_by:
                    if field and field.strip():
                        # Remove leading minus for validation
                        field_name = field.strip().lstrip('-')
                        if field_name in valid_fields:
                            order_fields.append(field.strip())
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
                    except Exception as e:
                        return create_error_response(
                            error_message=f'Error applying ordering: {str(e)}',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'orderBy': [f'Error applying ordering: {str(e)}']}
                        )
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
            item_serializer = self.get_serializer(items, many=True)
            items_data = item_serializer.data
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 10 if empty, as per old Swagger example)
            response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 10)
            
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
            
            # Check if it's a Django FieldError
            from django.core.exceptions import FieldError
            if isinstance(e, FieldError):
                return create_error_response(
                    error_message=f'Invalid field in query: {error_detail}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'orderBy': [f'Invalid field: {error_detail}. Valid fields are: id, name, code, locale']}
                )
            
            # Check if it's a JSON parsing error
            if 'JSON' in error_type or 'json' in error_detail.lower() or 'parse' in error_detail.lower():
                return create_error_response(
                    error_message='Invalid JSON in request body',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'request': ['Invalid JSON format. Please check your request body.']}
                )
            
            # Check if it's a ValueError (e.g., invalid integer conversion)
            if isinstance(e, ValueError):
                return create_error_response(
                    error_message=f'Invalid value: {error_detail}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'value': [error_detail]}
                )
            
            # For other exceptions, return generic error (but don't expose internal details in production)
            import sys
            if hasattr(sys, '_getframe'):
                # In development, show more details
                return create_error_response(
                    error_message=f'An error occurred while processing the request: {error_detail}',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    errors={'error': [f'{error_type}: {error_detail}']}
                )
            else:
                # In production, show generic message
                return create_error_response(
                    error_message='An error occurred while processing the request. Please check your input and try again.',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    errors={'error': ['Internal server error']}
                )

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_dapper',
        summary='Get colors (dapper context)',
        description='Get colors in dapper context. If id query parameter is provided, returns single color.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Color ID. If provided, returns single color.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Color(s) data',
                examples=[
                    OpenApiExample(
                        'Success response (single color)',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'red',
                                'code': 'string',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    ),
                    OpenApiExample(
                        'Success response (all colors)',
                        value={
                            'data': [],
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
        """Get colors in dapper context matching old Swagger format."""
        color_id = request.query_params.get('id')
        
        if color_id:
            # Return single color by ID
            try:
                color = Color.objects.get(id=int(color_id))
                serializer = self.get_serializer(color)
                return create_success_response(data=serializer.data)
            except (Color.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Color with ID "{color_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all colors
            colors = Color.objects.all().order_by('name')
            serializer = self.get_serializer(colors, many=True)
            return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_all',
        summary='Retrieves all colors',
        description='Retrieves all colors matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all colors',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'name': 'red',
                                    'code': 'string',
                                    'locale': 'string'
                                }
                            ],
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        """Get all colors matching old Swagger format."""
        colors = Color.objects.all().order_by('name')
        serializer = self.get_serializer(colors, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_retrieve',
        summary='Retrieves a color by its ID',
        description='Retrieves a color by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Color ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Color details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'red',
                                'code': 'string',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Color not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a color by ID matching old Swagger format."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_update',
        summary='Updates an existing color by its ID',
        description='Updates an existing color by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Color ID'
            )
        ],
        request=ColorCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update color',
                value={
                    'name': 'red',
                    'code': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Color updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'red',
                                'code': 'string',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Color not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a color by ID matching old Swagger format."""
        instance = self.get_object()
        
        # Validate input using old Swagger format serializer
        input_serializer = ColorCreateRequestSerializer(data=request.data)
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
        
        # Update color fields
        if 'name' in validated_data:
            instance.name = validated_data.get('name')
        if 'code' in validated_data:
            instance.code = validated_data.get('code') or ''
        if 'locale' in validated_data:
            instance.locale = validated_data.get('locale') or 'en'
        
        instance.save()
        
        # Return updated color
        serializer = self.get_serializer(instance)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Colors'],
        operation_id='colors_destroy',
        summary='Deletes a color by its ID',
        description='Deletes a color by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Color ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Color deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Color not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a color by ID matching old Swagger format."""
        instance = self.get_object()
        instance.delete()  # Hard delete
        return create_success_response(data=None)

