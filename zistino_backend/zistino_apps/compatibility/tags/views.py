"""
Views for Tags compatibility layer.
Implements all endpoints matching old Swagger format.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.db.models import Q
from django.core.paginator import Paginator

from zistino_apps.content.models import Tag
from zistino_apps.content.serializers import TagSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from drf_spectacular.utils import OpenApiParameter

from .serializers import (
    TagCreateRequestSerializer,
    TagSearchRequestSerializer,
    TagDetailSerializer,
)


@extend_schema(tags=['Tags'])
class TagsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tags endpoints.
    All endpoints will appear under "Tags" folder in Swagger UI.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Tags'],
        operation_id='tags_create',
        summary='Create a new tag',
        description='Creates a new tag matching old Swagger format.',
        request=TagCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Tag (default)',
                value={
                    "text": "string",
                    "description": "string",
                    "masterId": 0,
                    "type": 0,
                    "locale": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Tag created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new tag matching old Swagger format."""
        try:
            serializer = TagCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Create tag (masterId and type are ignored as they're not in the model)
            tag = Tag.objects.create(
                text=validated_data['text'],
                description=validated_data.get('description', ''),
                locale=validated_data.get('locale', 'fa')
            )
            
            # Return integer ID wrapped in response format
            return create_success_response(data=tag.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating tag: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tags'],
        operation_id='tags_retrieve',
        summary='Retrieve a tag by ID',
        description='Retrieves a tag by ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=TagDetailSerializer,
                description='Tag details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "text": "ne tag",
                                "description": "asdfasdf",
                                "masterId": None,
                                "type": 0,
                                "masterText": None,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Tag not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a tag by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = TagDetailSerializer(instance)
            return create_success_response(data=serializer.data, messages=[])
        except Tag.DoesNotExist:
            return create_error_response(
                error_message=f'Tag with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Tag with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving tag: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tags'],
        operation_id='tags_update',
        summary='Update a tag',
        description='Updates a tag matching old Swagger format.',
        request=TagCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=TagDetailSerializer,
                description='Updated tag details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "text": "ne tag",
                                "description": "asdfasdf",
                                "masterId": None,
                                "type": 0,
                                "masterText": None,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Tag not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a tag matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = TagCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update fields
            instance.text = validated_data.get('text', instance.text)
            instance.description = validated_data.get('description', instance.description)
            instance.locale = validated_data.get('locale', instance.locale)
            instance.save()
            
            response_serializer = TagDetailSerializer(instance)
            return create_success_response(data=response_serializer.data, messages=[])
        except Tag.DoesNotExist:
            return create_error_response(
                error_message=f'Tag with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Tag with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating tag: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tags'],
        operation_id='tags_partial_update',
        summary='Partially update a tag',
        description='Partially updates a tag matching old Swagger format.',
        request=TagCreateRequestSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a tag (calls update method)."""
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=['Tags'],
        operation_id='tags_destroy',
        summary='Delete a tag',
        description='Deletes a tag matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=TagDetailSerializer,
                description='Deleted tag details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "text": "ne tag",
                                "description": "asdfasdf",
                                "masterId": None,
                                "type": 0,
                                "masterText": None,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Tag not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a tag matching old Swagger format."""
        try:
            instance = self.get_object()
            # Serialize before deletion
            serializer = TagDetailSerializer(instance)
            tag_data = serializer.data
            # Delete the tag
            instance.delete()
            # Return the deleted tag data
            return create_success_response(data=tag_data, messages=[])
        except Tag.DoesNotExist:
            return create_error_response(
                error_message=f'Tag with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Tag with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting tag: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tags'],
        operation_id='tags_search',
        summary='Search tags using available filters',
        description='Search tags with pagination, keyword search, and ordering matching old Swagger format.',
        request=TagSearchRequestSerializer,
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
                    "orderBy": ["string"],
                    "type": 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=TagSerializer,
                description='Paginated list of tags',
                examples=[
                    OpenApiExample(
                        'Success Response',
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
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search tags matching old Swagger format."""
        try:
            serializer = TagSearchRequestSerializer(data=request.data)
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
                page_size = 1
            
            # Start with all tags
            queryset = Tag.objects.all()
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '')
            advanced_search = validated_data.get('advancedSearch')
            
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '')
            
            if keyword:
                queryset = queryset.filter(
                    Q(text__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out empty strings and validate fields
                valid_order_fields = []
                valid_fields = ['text', 'description', 'locale', 'created_at', 'updated_at']
                for field in order_by:
                    if field and field.strip():
                        # Remove '-' prefix if present for validation
                        field_name = field.lstrip('-')
                        if field_name in valid_fields:
                            valid_order_fields.append(field)
                
                if valid_order_fields:
                    queryset = queryset.order_by(*valid_order_fields)
                else:
                    queryset = queryset.order_by('text')
            else:
                queryset = queryset.order_by('text')
            
            # Paginate
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            total_count = paginator.count
            
            # Get page
            if page_number > total_pages:
                page_number = total_pages if total_pages > 0 else 1
            
            page = paginator.get_page(page_number)
            tags_data = [TagSerializer(tag).data for tag in page]
            
            return create_success_response(
                data=tags_data,
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
                error_message=f'An error occurred while searching tags: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Tags'],
    operation_id='tags_dapper',
    summary='Get tags in dapper context',
    description='Returns tags in dapper context. If ID is provided, returns specific tag, otherwise returns null.',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.QUERY, required=False, description='Tag ID (optional)')
    ],
    responses={
        200: OpenApiResponse(
            response=TagDetailSerializer,
            description='Tag data or null',
            examples=[
                OpenApiExample(
                    'Success Response (no ID)',
                    value={
                        "data": None,
                        "messages": [],
                        "succeeded": True
                    }
                ),
                OpenApiExample(
                    'Success Response (with ID)',
                    value={
                        "data": {
                            "id": 1,
                            "text": "ne tag",
                            "description": "asdfasdf",
                            "masterId": None,
                            "type": 0,
                            "masterText": None,
                            "locale": "string"
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class TagsDapperView(APIView):
    """GET /api/v1/tags/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get tags in dapper context matching old Swagger format."""
        try:
            tag_id = request.query_params.get('id')
            
            # If ID is provided, return the specific tag
            if tag_id:
                try:
                    tag_id = int(tag_id)
                    tag = Tag.objects.get(id=tag_id)
                    serializer = TagDetailSerializer(tag)
                    return create_success_response(data=serializer.data, messages=[])
                except (ValueError, Tag.DoesNotExist):
                    return create_error_response(
                        error_message=f'Tag with ID "{tag_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Tag with ID "{tag_id}" not found.']}
                    )
            
            # Old Swagger returns null for dapper when no ID
            return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Tags'],
    operation_id='tags_all',
    summary='Get all tags',
    description='Returns all tags matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=TagSerializer,
            description='List of all tags',
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
        )
    }
)
class TagsAllView(APIView):
    """GET /api/v1/tags/all"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all tags matching old Swagger format."""
        try:
            tags = Tag.objects.all().order_by('text')
            serializer = TagSerializer(tags, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Tags'],
    operation_id='tags_client_all',
    summary='Get all tags for client',
    description='Get all tags for client with search functionality matching old Swagger format.',
    request=TagSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Client All Request',
            value={
                "advancedSearch": {
                    "fields": ["string"],
                    "keyword": "string",
                    "groupBy": ["string"]
                },
                "keyword": "string",
                "pageNumber": 0,
                "pageSize": 0,
                "orderBy": ["string"],
                "type": 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=TagSerializer,
            description='Paginated list of tags',
            examples=[
                OpenApiExample(
                    'Success Response',
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
        )
    }
)
class TagsClientAllView(APIView):
    """POST /api/v1/tags/client/all"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Get all tags for client with search functionality matching old Swagger format."""
        try:
            serializer = TagSearchRequestSerializer(data=request.data)
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
                page_size = 1
            
            # Start with all tags
            queryset = Tag.objects.all()
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '')
            advanced_search = validated_data.get('advancedSearch')
            
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '')
            
            if keyword:
                queryset = queryset.filter(
                    Q(text__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out empty strings and validate fields
                valid_order_fields = []
                valid_fields = ['text', 'description', 'locale', 'created_at', 'updated_at']
                for field in order_by:
                    if field and field.strip():
                        # Remove '-' prefix if present for validation
                        field_name = field.lstrip('-')
                        if field_name in valid_fields:
                            valid_order_fields.append(field)
                
                if valid_order_fields:
                    queryset = queryset.order_by(*valid_order_fields)
                else:
                    queryset = queryset.order_by('text')
            else:
                queryset = queryset.order_by('text')
            
            # Paginate
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            total_count = paginator.count
            
            # Get page
            if page_number > total_pages:
                page_number = total_pages if total_pages > 0 else 1
            
            page = paginator.get_page(page_number)
            tags_data = [TagSerializer(tag).data for tag in page]
            
            return create_success_response(
                data=tags_data,
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
