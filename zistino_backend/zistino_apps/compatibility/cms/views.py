"""
Compatibility views for CMS endpoints.
All endpoints will appear under "Cms" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Cms
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from zistino_apps.products.models import ProductSection
from zistino_apps.products.serializers import ProductSectionSerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    CMSCreateRequestSerializer,
    CMSSearchRequestSerializer,
    CMSCompatibilitySerializer
)


@extend_schema(tags=['Cms'])
class CMSViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing CMS (ProductSection) content.
    All endpoints will appear under "Cms" folder in Swagger UI.
    """
    queryset = ProductSection.objects.filter(is_active=True)
    serializer_class = ProductSectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return all sections (including inactive) for admin, active only for others."""
        if self.action in ['list', 'retrieve']:
            return ProductSection.objects.filter(is_active=True)
        return ProductSection.objects.all()

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Cms'],
        operation_id='cms_create',
        summary='Creates a new CMS item',
        description='Creates a new CMS item matching old Swagger format.',
        request=CMSCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create CMS',
                value={
                    'version': 0,
                    'name': 'string',
                    'content': 'string',
                    'groupName': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='CMS created successfully',
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
        """Create a new CMS item matching old Swagger format. Returns CMS ID."""
        # Validate input using old Swagger format serializer
        input_serializer = CMSCreateRequestSerializer(data=request.data)
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
        
        # Map old Swagger fields to Django model fields
        cms_data = {
            'name': validated_data.get('name'),
            'description': validated_data.get('content') or '',
            'group_name': validated_data.get('groupName') or '',
            'version': validated_data.get('version', 0),
            'locale': validated_data.get('locale') or 'en',
            'page': 'home',  # Default page
        }
        
        # Create CMS using Django model
        cms = ProductSection.objects.create(**cms_data)
        
        # Return just the CMS ID wrapped in standard response (200 OK to match old Swagger)
        return create_success_response(data=cms.id)

    @extend_schema(
        tags=['Cms'],
        operation_id='cms_search',
        summary='Search Cms using available Filters',
        description='Search Cms using available Filters matching old Swagger format.',
        request=CMSSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search CMS',
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
            ),
            400: {'description': 'Validation error'}
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search CMS with pagination matching old Swagger format."""
        # Validate input
        serializer = CMSSearchRequestSerializer(data=request.data)
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
        qs = ProductSection.objects.all()
        
        # Apply keyword search
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(name__icontains=keyword.strip()) |
                Q(description__icontains=keyword.strip()) |
                Q(page__icontains=keyword.strip()) |
                Q(group_name__icontains=keyword.strip())
            )
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Parse orderBy fields (e.g., "name", "-name" for descending)
            order_fields = []
            for field in order_by:
                if field and field.strip():
                    order_fields.append(field.strip())
            if order_fields:
                qs = qs.order_by(*order_fields)
        else:
            # Default ordering
            qs = qs.order_by('-created_at')
        
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
        
        # Serialize results (empty array for now, as old Swagger shows empty data)
        item_serializer = self.get_serializer(items, many=True)
        items_data = item_serializer.data
        
        # Build response matching old Swagger format
        # If pageSize is 0, show actual number of items returned (or 1 if empty)
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

    @extend_schema(
        tags=['Cms'],
        operation_id='cms_dapper',
        summary='Get CMS (dapper context)',
        description='Get CMS in dapper context. If id query parameter is provided, returns single CMS.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='CMS ID. If provided, returns single CMS.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='CMS data',
                examples=[
                    OpenApiExample(
                        'Success response (single CMS)',
                        value={
                            'data': {
                                'id': 1,
                                'version': 1,
                                'name': 'cms',
                                'content': 'c',
                                'groupName': 'cm',
                                'locale': 'fa'
                            },
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
        """Get CMS in dapper context matching old Swagger format."""
        cms_id = request.query_params.get('id')
        
        if cms_id:
            # Return single CMS by ID
            try:
                cms = ProductSection.objects.get(id=int(cms_id), is_active=True)
                serializer = CMSCompatibilitySerializer(cms)
                return create_success_response(data=serializer.data)
            except (ProductSection.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'CMS with ID "{cms_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all CMS (empty array for now, as old Swagger shows)
            return create_success_response(data=[])

    @extend_schema(
        tags=['Cms'],
        operation_id='cms_retrieve',
        summary='Retrieves a CMS item by its ID',
        description='Retrieves a CMS item by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='CMS ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='CMS details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'version': 1,
                                'name': 'cms',
                                'content': 'c',
                                'groupName': 'cm',
                                'locale': 'fa'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'CMS not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a CMS item by ID matching old Swagger format."""
        instance = self.get_object()
        serializer = CMSCompatibilitySerializer(instance)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Cms'],
        operation_id='cms_update',
        summary='Updates an existing CMS item by its ID',
        description='Updates an existing CMS item by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='CMS ID'
            )
        ],
        request=CMSCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update CMS',
                value={
                    'version': 1,
                    'name': 'cms',
                    'content': 'c',
                    'groupName': 'cm',
                    'locale': 'fa'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='CMS updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'version': 1,
                                'name': 'cms',
                                'content': 'c',
                                'groupName': 'cm',
                                'locale': 'fa'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'CMS not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a CMS item by ID matching old Swagger format."""
        instance = self.get_object()
        
        # Validate input using old Swagger format serializer
        input_serializer = CMSCreateRequestSerializer(data=request.data)
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
        
        # Update CMS fields
        if 'name' in validated_data:
            instance.name = validated_data.get('name')
        if 'content' in validated_data:
            instance.description = validated_data.get('content') or ''
        if 'groupName' in validated_data:
            instance.group_name = validated_data.get('groupName') or ''
        if 'version' in validated_data:
            instance.version = validated_data.get('version', 0)
        if 'locale' in validated_data:
            instance.locale = validated_data.get('locale') or 'en'
        
        instance.save()
        
        # Return updated CMS in compatibility format
        serializer = CMSCompatibilitySerializer(instance)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Cms'],
        operation_id='cms_destroy',
        summary='Deletes a CMS item by its ID',
        description='Deletes a CMS item by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='CMS ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='CMS deleted successfully',
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
            404: {'description': 'CMS not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a CMS item by ID matching old Swagger format."""
        instance = self.get_object()
        # Soft delete by setting is_active to False
        instance.is_active = False
        instance.save()
        return create_success_response(data=None)


    @extend_schema(
        tags=['Cms'],
        operation_id='cms_getmycms_post',
        summary='Get my CMS (POST)',
        description='Get CMS items for the authenticated user or by user ID.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'userId': {'type': 'string', 'format': 'uuid', 'description': 'User ID (optional)'},
                }
            }
        },
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='CMS items for user',
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
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='getmycms')
    def getmycms(self, request):
        """Get CMS items for user (POST version) matching old Swagger format. Returns null."""
        # Old Swagger returns null for this endpoint
        return create_success_response(data=None)


# ============================================================================
# SEPARATE APIView CLASSES FOR CUSTOM ENDPOINTS WITH PATH PARAMETERS
# ============================================================================

@extend_schema(
    tags=['Cms'],
    operation_id='cms_getmycms',
    summary='Get my CMS',
    description='Get CMS items for the authenticated user matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='CMS items for user',
            examples=[
                OpenApiExample(
                    'Success response',
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
class CMSGetMyCMSView(APIView):
    """GET /api/v1/cms/getmycms/ - Get CMS for authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get CMS items for authenticated user matching old Swagger format."""
        # Note: ProductSection doesn't have a user field
        # Return all active CMS items for now
        sections = ProductSection.objects.filter(is_active=True).order_by('-created_at')
        serializer = CMSCompatibilitySerializer(sections, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Cms'],
    operation_id='cms_getmycms_by_userid',
    summary='Get my CMS by user ID',
    description='Get CMS items for a specific user ID. Accepts UUID as string.',
    parameters=[
        OpenApiParameter(
            name='userid',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='User ID (UUID as string). Example: "14d27650-df76-4c0c-981d-9aa46c1eb3f5"'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='CMS items for user',
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
        )
    }
)
class CMSGetMyCMSByUserIdView(APIView):
    """GET /api/v1/cms/getmycms/{userid} - Get CMS by user ID"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, userid):
        """Get CMS by user ID matching old Swagger format. Accepts UUID as string. Returns null."""
        # Validate UUID format
        try:
            from uuid import UUID
            uuid_obj = UUID(userid)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid user ID format: "{userid}". Expected UUID format.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userid': [f'Value must be a Guid.']}
            )
        
        # Old Swagger returns null for this endpoint
        return create_success_response(data=None)


@extend_schema(
    tags=['Cms'],
    operation_id='cms_client_by_name',
    summary='Get CMS by name for client',
    description='Retrieves client-related CMS items by a given name.',
    responses={200: ProductSectionSerializer}
)
class CMSClientByNameView(APIView):
    """GET /api/v1/cms/client/by-name/{name} - Get CMS by name for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, name):
        """Get CMS by name for client matching old Swagger format."""
        sections = ProductSection.objects.filter(
            name__icontains=name,
            is_active=True
        ).order_by('-created_at')
        serializer = CMSCompatibilitySerializer(sections, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Cms'],
    operation_id='cms_client_by_group_name',
    summary='Get CMS by group name for client',
    description='Retrieves client-related CMS items by a given group name.',
    responses={200: ProductSectionSerializer}
)
class CMSClientByGroupNameView(APIView):
    """GET /api/v1/cms/client/by-group-name/{groupName} - Get CMS by group name for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, groupName):
        """Get CMS by group name for client matching old Swagger format."""
        sections = ProductSection.objects.filter(
            group_name=groupName,
            is_active=True
        ).order_by('-created_at')
        serializer = CMSCompatibilitySerializer(sections, many=True)
        return create_success_response(data=serializer.data)

