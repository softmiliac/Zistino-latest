"""
Compatibility views for BlogCategories endpoints.
These views wrap the existing BlogCategoryViewSet and add Swagger tags for proper grouping.
All endpoints will appear under "BlogCategories" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogCategories
"""
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.content import views as content_views
from zistino_apps.content.models import BlogCategory
from zistino_apps.content.serializers import BlogCategorySerializer
from zistino_apps.products.serializers import URLImageField
from django.db.models import Q
from .serializers import (
    BlogCategoryCreateRequestSerializer,
    BlogCategoryUpdateRequestSerializer,
    BlogCategoryCompatibilitySerializer,
    BlogCategorySearchRequestSerializer
)


@extend_schema(tags=['BlogCategories'], exclude=True)  # Exclude from Swagger - we use separate APIView classes
class BlogCategoriesViewSet(content_views.BlogCategoryViewSet):
    """
    Compatibility viewset for blog categories endpoints.
    Inherits all functionality from BlogCategoryViewSet but with 'BlogCategories' tag for Swagger grouping.
    All endpoints will appear under "BlogCategories" folder in Swagger UI.
    NOTE: This ViewSet is excluded from Swagger - we use separate APIView classes for proper documentation.
    """
    pass


# ============================================================================
# SEPARATE APIView CLASSES FOR CUSTOM ENDPOINTS
# These are needed so Swagger can properly document them
# ============================================================================

@extend_schema(
    tags=['BlogCategories'],
    operation_id='blogcategories_dapper',
    summary='Get blog categories (dapper context)',
    description='Get blog categories in dapper context. If id query parameter is provided, returns single category.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Category ID. If provided, returns single category.'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Category data',
            examples=[
                OpenApiExample(
                    'Success response (single category)',
                    value={
                        'data': {
                            'id': 1,
                            'title': 'new blog ca',
                            'image': 'string',
                            'slug': 'string',
                            'content': 'asdfasdfas',
                            'locale': 'fa'
                        },
                        'messages': [],
                        'succeeded': True
                    }
                ),
                OpenApiExample(
                    'Success response (all categories)',
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
class BlogCategoriesDapperView(APIView):
    """GET /api/v1/blogcategories/dapper - Get blog categories (dapper context)"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get blog categories in dapper context matching old Swagger format."""
        category_id = request.query_params.get('id')
        
        if category_id:
            # Return single category by ID
            try:
                category = BlogCategory.objects.get(id=int(category_id), is_active=True)
                serializer = BlogCategoryCompatibilitySerializer(category, context={'request': request})
                return create_success_response(data=serializer.data)
            except (BlogCategory.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Blog category with ID "{category_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all categories
            categories = BlogCategory.objects.filter(is_active=True).order_by('name')
            serializer = BlogCategoryCompatibilitySerializer(categories, many=True, context={'request': request})
            return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogCategories'],
    operation_id='blogcategories_search',
    summary='Search blog categories using available Filters',
    description='Search blog categories using available Filters matching old Swagger format.',
    request=BlogCategorySearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Search blog categories',
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
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 0,
                                'title': 'string',
                                'locale': 'string',
                                'image': 'string',
                                'slug': 'string',
                                'content': 'string'
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
        400: {'description': 'Validation error'}
    }
)
class BlogCategoriesSearchView(APIView):
    """POST /api/v1/blogcategories/search - Search blog categories"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search blog categories matching old Swagger format."""
        # Validate input
        serializer = BlogCategorySearchRequestSerializer(data=request.data)
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
        qs = BlogCategory.objects.filter(is_active=True)
        
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
            categories = qs[start:end]
        else:
            categories = qs[start:]
        
        # Serialize results using compatibility serializer
        category_serializer = BlogCategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        
        # Build response matching old Swagger format
        response_data = {
            'messages': [],
            'succeeded': True,
            'data': category_serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous,
            'hasNextPage': has_next
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['BlogCategories'],
    operation_id='blogcategories_all',
    summary='Retrieves all blog categories',
    description='Retrieves all blog categories matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of all blog categories',
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
class BlogCategoriesAllView(APIView):
    """GET /api/v1/blogcategories/all - Get all blog categories"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all blog categories matching old Swagger format."""
        categories = BlogCategory.objects.filter(is_active=True).order_by('name')
        serializer = BlogCategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogCategories'],
    operation_id='blogcategories_client_all',
    summary='Retrieves all blog categories for client-side use',
    description='Retrieves all blog categories specifically for client-side use matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of all blog categories for client',
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
class BlogCategoriesClientAllView(APIView):
    """GET /api/v1/blogcategories/client/all - Get all blog categories for client"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all blog categories for client matching old Swagger format."""
        categories = BlogCategory.objects.filter(is_active=True).order_by('name')
        serializer = BlogCategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogCategories'],
    operation_id='blogcategories_client_categories',
    summary='Retrieves categories specifically for client-side use',
    description='Retrieves categories specifically for client-side use matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of categories for client',
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
class BlogCategoriesClientCategoriesView(APIView):
    """GET /api/v1/blogcategories/client/categories - Get categories for client"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get categories for client matching old Swagger format."""
        categories = BlogCategory.objects.filter(is_active=True).order_by('name')
        serializer = BlogCategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


# ============================================================================
# STANDARD REST ENDPOINTS - Separate APIView classes for Swagger documentation
# ============================================================================

class BlogCategoriesListView(APIView):
    """GET/POST /api/v1/blogcategories - List/Create blog categories"""
    permission_classes = [AllowAny]  # GET is public, POST needs auth (can be changed)
    
    @extend_schema(
        tags=['BlogCategories'],
        operation_id='blogcategories_list',
        summary='List all blog categories',
        description='Get list of all blog categories matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of blog categories',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'title': 'new blog ca',
                                    'image': 'string',
                                    'slug': 'string',
                                    'content': 'asdfasdfas',
                                    'locale': 'fa'
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
        """Get list of blog categories matching old Swagger format."""
        categories = BlogCategory.objects.filter(is_active=True).order_by('name')
        serializer = BlogCategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['BlogCategories'],
        operation_id='blogcategories_create',
        summary='Creates a new blog category',
        description='Creates a new blog category matching old Swagger format.',
        request=BlogCategoryCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create blog category',
                value={
                    'title': 'string',
                    'image': 'string',
                    'slug': 'string',
                    'content': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog category created successfully',
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
    def post(self, request):
        """Create blog category matching old Swagger format. Returns category ID."""
        # Validate input using old Swagger format serializer
        input_serializer = BlogCategoryCreateRequestSerializer(data=request.data)
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
        category_data = {
            'name': validated_data.get('title'),
            'description': validated_data.get('content') or '',
            'slug': validated_data.get('slug') or '',
            'image_url': validated_data.get('image') or '',  # BlogCategory uses image_url (CharField)
            'locale': validated_data.get('locale') or 'en',
        }
        
        # Create category using Django model serializer
        category_serializer = BlogCategorySerializer(data=category_data, context={'request': request})
        if not category_serializer.is_valid():
            errors = {}
            for field, error_list in category_serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            return create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
        
        category = category_serializer.save()
        
        # Return just the category ID wrapped in standard response
        return create_success_response(data=category.id)  # 200 OK to match old Swagger


class BlogCategoriesDetailView(APIView):
    """GET/PUT/DELETE /api/v1/blogcategories/{id} - Retrieve/Update/Delete blog category"""
    permission_classes = [AllowAny]  # GET is public, PUT/DELETE need auth (handled in viewset)
    
    @extend_schema(
        tags=['BlogCategories'],
        operation_id='blogcategories_retrieve',
        summary='Retrieves a blog category by its ID',
        description='Retrieves a blog category by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog category ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog category details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'title': 'new blog ca',
                                'image': 'string',
                                'slug': 'string',
                                'content': 'asdfasdfas',
                                'locale': 'fa'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Blog category not found'}
        }
    )
    def get(self, request, id):
        """Get blog category by ID matching old Swagger format."""
        try:
            category = BlogCategory.objects.get(id=id, is_active=True)
            serializer = BlogCategoryCompatibilitySerializer(category, context={'request': request})
            return create_success_response(data=serializer.data)
        except BlogCategory.DoesNotExist:
            return create_error_response(
                error_message=f'Blog category with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['BlogCategories'],
        operation_id='blogcategories_update',
        summary='Updates an existing blog category by its ID',
        description='Updates an existing blog category by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog category ID'
            )
        ],
        request=BlogCategoryUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update blog category',
                value={
                    'title': 'string',
                    'image': 'string',
                    'slug': 'string',
                    'content': 'string',
                    'locale': 'string'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog category updated successfully',
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
            400: {'description': 'Validation error'},
            404: {'description': 'Blog category not found'}
        }
    )
    def put(self, request, id):
        """Update blog category matching old Swagger format."""
        try:
            category = BlogCategory.objects.get(id=id, is_active=True)
        except BlogCategory.DoesNotExist:
            return create_error_response(
                error_message=f'Blog category with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input (use update serializer where all fields are optional)
        input_serializer = BlogCategoryUpdateRequestSerializer(data=request.data)
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
        
        # Update category fields
        if 'title' in validated_data:
            category.name = validated_data.get('title')
        if 'content' in validated_data:
            category.description = validated_data.get('content') or ''
        if 'slug' in validated_data:
            category.slug = validated_data.get('slug') or ''
        if 'image' in validated_data:
            category.image_url = validated_data.get('image') or ''
        if 'locale' in validated_data:
            category.locale = validated_data.get('locale') or 'en'
        
        category.save()
        
        # Return just the category ID (matching old Swagger format)
        return create_success_response(data=category.id)
    
    @extend_schema(
        tags=['BlogCategories'],
        operation_id='blogcategories_delete',
        summary='Deletes a blog category by its ID',
        description='Deletes a blog category by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog category ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog category deleted successfully',
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
            404: {'description': 'Blog category not found'}
        }
    )
    def delete(self, request, id):
        """Delete blog category matching old Swagger format."""
        try:
            category = BlogCategory.objects.get(id=id, is_active=True)
            # Soft delete by setting is_active to False
            category.is_active = False
            category.save()
            return create_success_response(data=None)
        except BlogCategory.DoesNotExist:
            return create_error_response(
                error_message=f'Blog category with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

