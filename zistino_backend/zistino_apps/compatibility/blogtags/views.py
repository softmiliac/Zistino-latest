"""
Compatibility views for BlogTags endpoints.
All endpoints will appear under "BlogTags" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogTags
"""
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.content.models import BlogTag
from zistino_apps.content.serializers import BlogTagSerializer
from django.db.models import Q
from .serializers import (
    BlogTagCreateRequestSerializer,
    BlogTagCompatibilitySerializer,
    BlogTagSearchRequestSerializer
)


# ============================================================================
# STANDARD REST ENDPOINTS
# ============================================================================

class BlogTagsListView(APIView):
    """GET/POST /api/v1/blogtags - List/Create blog tags"""
    permission_classes = [AllowAny]  # GET is public, POST needs auth (can be changed)
    
    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_list',
        summary='List all blog tags',
        description='Get list of all blog tags matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of blog tags',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'title': 'string',
                                    'slug': 'string',
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
    def get(self, request):
        """Get list of blog tags matching old Swagger format."""
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagCompatibilitySerializer(tags, many=True)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_create',
        summary='Creates a new blog tag',
        description='Creates a new blog tag matching old Swagger format.',
        request=BlogTagCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create blog tag',
                value={
                    'title': 'string',
                    'slug': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog tag created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 2,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    def post(self, request):
        """Create blog tag matching old Swagger format. Returns tag ID."""
        # Validate input using old Swagger format serializer
        input_serializer = BlogTagCreateRequestSerializer(data=request.data)
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
        tag_data = {
            'name': validated_data.get('title'),
            'slug': validated_data.get('slug') or '',
            'locale': validated_data.get('locale') or 'en',
        }
        
        # Create tag using Django model serializer
        tag_serializer = BlogTagSerializer(data=tag_data, context={'request': request})
        if not tag_serializer.is_valid():
            errors = {}
            for field, error_list in tag_serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        tag = tag_serializer.save()
        
        # Return just the tag ID wrapped in standard response
        return create_success_response(data=tag.id)  # 200 OK to match old Swagger


class BlogTagsDetailView(APIView):
    """GET/PUT/DELETE /api/v1/blogtags/{id} - Retrieve/Update/Delete blog tag"""
    permission_classes = [AllowAny]  # GET is public, PUT/DELETE need auth (can be changed)
    
    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_retrieve',
        summary='Retrieves a blog tag by its ID',
        description='Retrieves a blog tag by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog tag ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog tag details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'title': 'string',
                                'slug': 'string',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Blog tag not found'}
        }
    )
    def get(self, request, id):
        """Get blog tag by ID matching old Swagger format."""
        try:
            tag = BlogTag.objects.get(id=id)
            serializer = BlogTagCompatibilitySerializer(tag)
            return create_success_response(data=serializer.data)
        except BlogTag.DoesNotExist:
            return create_error_response(
                error_message=f'Blog tag with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_update',
        summary='Updates an existing blog tag by its ID',
        description='Updates an existing blog tag by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog tag ID'
            )
        ],
        request=BlogTagCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update blog tag',
                value={
                    'title': 'string',
                    'slug': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog tag updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'title': 'string',
                                'slug': 'string',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Blog tag not found'}
        }
    )
    def put(self, request, id):
        """Update blog tag matching old Swagger format."""
        try:
            tag = BlogTag.objects.get(id=id)
        except BlogTag.DoesNotExist:
            return create_error_response(
                error_message=f'Blog tag with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = BlogTagCreateRequestSerializer(data=request.data)
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
        
        # Update tag fields
        if 'title' in validated_data:
            tag.name = validated_data.get('title')
        if 'slug' in validated_data:
            tag.slug = validated_data.get('slug') or ''
        if 'locale' in validated_data:
            tag.locale = validated_data.get('locale') or 'en'
        
        tag.save()
        
        # Return updated tag
        serializer = BlogTagCompatibilitySerializer(tag)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_delete',
        summary='Deletes a blog tag by its ID',
        description='Deletes a blog tag by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog tag ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog tag deleted successfully',
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
            404: {'description': 'Blog tag not found'}
        }
    )
    def delete(self, request, id):
        """Delete blog tag matching old Swagger format."""
        try:
            tag = BlogTag.objects.get(id=id)
            tag.delete()  # Hard delete since BlogTag doesn't have is_active
            return create_success_response(data=None)
        except BlogTag.DoesNotExist:
            return create_error_response(
                error_message=f'Blog tag with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# SPECIAL ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['BlogTags'],
    operation_id='blogtags_dapper',
    summary='Get blog tags (dapper context)',
    description='Get blog tags in dapper context. If id query parameter is provided, returns single tag.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Blog tag ID. If provided, returns single tag.'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Blog tag(s) data',
            examples=[
                OpenApiExample(
                    'Success response (single tag)',
                    value={
                        'data': {
                            'id': 1,
                            'title': 'string',
                            'slug': 'string',
                            'locale': 'string'
                        },
                        'messages': [],
                        'succeeded': True
                    }
                ),
                OpenApiExample(
                    'Success response (all tags)',
                    value={
                        'data': [
                            {
                                'id': 1,
                                'title': 'string',
                                'slug': 'string',
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
class BlogTagsDapperView(APIView):
    """GET /api/v1/blogtags/dapper - Get blog tags (dapper context)"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get blog tags in dapper context matching old Swagger format."""
        tag_id = request.query_params.get('id')
        
        if tag_id:
            # Return single tag by ID
            try:
                tag = BlogTag.objects.get(id=int(tag_id))
                serializer = BlogTagCompatibilitySerializer(tag)
                return create_success_response(data=serializer.data)
            except (BlogTag.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Blog tag with ID "{tag_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all tags
            tags = BlogTag.objects.all().order_by('name')
            serializer = BlogTagCompatibilitySerializer(tags, many=True)
            return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogTags'],
    operation_id='blogtags_search',
    summary='Search blog tags using available Filters',
    description='Search blog tags using available Filters matching old Swagger format.',
    request=BlogTagSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Search blog tags',
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
class BlogTagsSearchView(APIView):
    """POST /api/v1/blogtags/search - Search blog tags"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search blog tags matching old Swagger format."""
        # Validate input
        serializer = BlogTagSearchRequestSerializer(data=request.data)
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
        
        # Get pagination parameters
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        # Get keyword from request or advancedSearch
        keyword = validated_data.get('keyword') or ''
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and advanced_search.get('keyword'):
            keyword = advanced_search.get('keyword') or keyword
        
        # Build query
        qs = BlogTag.objects.all()
        
        # Apply keyword search
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(name__icontains=keyword.strip()) |
                Q(description__icontains=keyword.strip()) |
                Q(slug__icontains=keyword.strip())
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
            qs = qs.order_by('name')
        
        # Get total count
        total_count = qs.count()
        
        # Calculate pagination
        if page_size > 0:
            total_pages = (total_count + page_size - 1) // page_size
            start = (page_number - 1) * page_size
            end = start + page_size
            has_previous = page_number > 1
            has_next = page_number < total_pages
        else:
            # If pageSize is 0, return all results
            total_pages = 0
            start = 0
            end = None
            has_previous = False
            has_next = False
        
        # Get paginated results
        if end is not None:
            tags = qs[start:end]
        else:
            tags = qs[start:]
        
        # Serialize results using compatibility serializer
        tag_serializer = BlogTagCompatibilitySerializer(tags, many=True)
        
        # Build response matching old Swagger format
        response_data = {
            'data': tag_serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous,
            'hasNextPage': has_next,
            'messages': None,  # Old Swagger shows null, not empty array
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['BlogTags'],
    operation_id='blogtags_all',
    summary='Retrieves all blog tags',
    description='Retrieves all blog tags matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of all blog tags',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [
                            {
                                'id': 1,
                                'title': 'string',
                                'slug': 'string',
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
class BlogTagsAllView(APIView):
    """GET /api/v1/blogtags/all - Get all blog tags"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all blog tags matching old Swagger format."""
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagCompatibilitySerializer(tags, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogTags'],
    operation_id='blogtags_client_all',
    summary='Retrieves all blog tags for client-side use',
    description='Retrieves all blog tags specifically for client-side use matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of all blog tags for client',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [
                            {
                                'id': 1,
                                'title': 'string',
                                'slug': 'string',
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
class BlogTagsClientAllView(APIView):
    """GET /api/v1/blogtags/client/all - Get all blog tags for client"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all blog tags for client matching old Swagger format."""
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagCompatibilitySerializer(tags, many=True)
        return create_success_response(data=serializer.data)

