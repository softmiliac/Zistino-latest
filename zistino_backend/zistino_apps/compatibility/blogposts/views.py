"""
Compatibility views for BlogPosts endpoints.
All endpoints will appear under "BlogPosts" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogPosts
"""
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.content.models import BlogPost, BlogCategory, BlogTag
from zistino_apps.content.serializers import BlogPostSerializer
from django.db.models import Q
from .serializers import (
    BlogPostCreateRequestSerializer,
    BlogPostCompatibilitySerializer,
    BlogPostSearchRequestSerializer,
    BlogPostClientSearchRequestSerializer
)


# ============================================================================
# STANDARD REST ENDPOINTS
# ============================================================================

class BlogPostsListView(APIView):
    """GET/POST /api/v1/blogposts - List/Create blog posts"""
    permission_classes = [AllowAny]  # GET is public, POST needs auth (can be changed)
    
    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_list',
        summary='List all blog posts',
        description='Get list of all blog posts matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of blog posts',
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
    def get(self, request):
        """Get list of blog posts matching old Swagger format."""
        posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
        serializer = BlogPostCompatibilitySerializer(posts, many=True)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_create',
        summary='Creates a new blog post',
        description='Creates a new blog post matching old Swagger format.',
        request=BlogPostCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create blog post',
                value={
                    'authorId': 'string',
                    'parentId': 0,
                    'title': 'string',
                    'type': 0,
                    'metaTitle': 'string',
                    'slug': 'string',
                    'imageUrl': 'string',
                    'thumbnail': 'string',
                    'summery': 'string',
                    'content': 'string',
                    'published': '2025-11-09T08:33:15.734Z',
                    'categories': 'string',
                    'categoryIds': [0],
                    'tags': 'string',
                    'tagIds': [0],
                    'productIds': ['string'],
                    'locale': 'string',
                    'files': [
                        {
                            'id': 0,
                            'type': 0,
                            'rowId': 0,
                            'fileUrl': 'string'
                        }
                    ]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog post created successfully',
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
        """Create blog post matching old Swagger format. Returns post ID."""
        # Validate input using old Swagger format serializer
        input_serializer = BlogPostCreateRequestSerializer(data=request.data)
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
        # Handle category (use first categoryId or parentId)
        category_id = None
        if validated_data.get('categoryIds'):
            category_id = validated_data.get('categoryIds')[0]
        elif validated_data.get('parentId'):
            category_id = validated_data.get('parentId')
        
        category = None
        if category_id:
            try:
                category = BlogCategory.objects.get(id=category_id)
            except BlogCategory.DoesNotExist:
                return create_error_response(
                    error_message=f'Category with ID "{category_id}" not found.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'categoryIds': [f'Category with ID "{category_id}" not found.']}
                )
        
        # Handle published_at
        published_at = validated_data.get('published')
        is_published = published_at is not None if published_at else False
        
        # Create post directly using model
        try:
            post = BlogPost.objects.create(
                title=validated_data.get('title'),
                slug=validated_data.get('slug') or '',
                content=validated_data.get('content'),
                excerpt=validated_data.get('summery') or '',
                featured_image=validated_data.get('imageUrl') or '',
                category=category,
                author_name=validated_data.get('authorId') or '',
                is_published=is_published,
                published_at=published_at,
                locale=validated_data.get('locale') or 'fa',
            )
        except Exception as e:
            return create_error_response(
                error_message=f'Error creating blog post: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'detail': [str(e)]}
            )
        
        # Handle tags (ManyToMany)
        tag_ids = validated_data.get('tagIds', [])
        if tag_ids:
            try:
                tags = BlogTag.objects.filter(id__in=tag_ids)
                if tags.count() != len(tag_ids):
                    # Some tags not found
                    found_ids = set(tags.values_list('id', flat=True))
                    missing_ids = set(tag_ids) - found_ids
                    return create_error_response(
                        error_message=f'Some tags not found: {list(missing_ids)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'tagIds': [f'Tags with IDs {list(missing_ids)} not found.']}
                    )
                post.tags.set(tags)
            except Exception as e:
                return create_error_response(
                    error_message=f'Error setting tags: {str(e)}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'tagIds': [str(e)]}
                )
        
        # Return just the post ID wrapped in standard response
        return create_success_response(data=post.id)  # 200 OK to match old Swagger


class BlogPostsDetailView(APIView):
    """GET/PUT/DELETE /api/v1/blogposts/{id} - Retrieve/Update/Delete blog post"""
    permission_classes = [AllowAny]  # GET is public, PUT/DELETE need auth (can be changed)
    
    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_retrieve',
        summary='Retrieves a blog post by its ID',
        description='Retrieves a blog post by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog post ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog post details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'authorId': 'string',
                                'parentId': 0,
                                'title': 'string',
                                'type': 0,
                                'metaTitle': 'string',
                                'slug': 'string',
                                'imageUrl': 'string',
                                'thumbnail': 'string',
                                'summery': 'string',
                                'content': 'string',
                                'published': '2025-11-09T08:33:15.734Z',
                                'categories': 'string',
                                'categoryIds': [0],
                                'tags': 'string',
                                'tagIds': [0],
                                'productIds': ['string'],
                                'locale': 'string',
                                'files': []
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Blog post not found'}
        }
    )
    def get(self, request, id):
        """Get blog post by ID matching old Swagger format."""
        try:
            post = BlogPost.objects.get(id=id)
            serializer = BlogPostCompatibilitySerializer(post)
            return create_success_response(data=serializer.data)
        except BlogPost.DoesNotExist:
            return create_error_response(
                error_message=f'Blog post with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_update',
        summary='Updates an existing blog post by its ID',
        description='Updates an existing blog post by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog post ID'
            )
        ],
        request=BlogPostCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update blog post',
                value={
                    'authorId': 'string',
                    'parentId': 0,
                    'title': 'string',
                    'type': 0,
                    'metaTitle': 'string',
                    'slug': 'string',
                    'imageUrl': 'string',
                    'thumbnail': 'string',
                    'summery': 'string',
                    'content': 'string',
                    'published': '2025-11-09T08:33:15.734Z',
                    'categories': 'string',
                    'categoryIds': [0],
                    'tags': 'string',
                    'tagIds': [0],
                    'productIds': ['string'],
                    'locale': 'string',
                    'files': []
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog post updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'authorId': 'string',
                                'parentId': 0,
                                'title': 'string',
                                'type': 0,
                                'metaTitle': 'string',
                                'slug': 'string',
                                'imageUrl': 'string',
                                'thumbnail': 'string',
                                'summery': 'string',
                                'content': 'string',
                                'published': '2025-11-09T08:33:15.734Z',
                                'categories': 'string',
                                'categoryIds': [0],
                                'tags': 'string',
                                'tagIds': [0],
                                'productIds': ['string'],
                                'locale': 'string',
                                'files': []
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Blog post not found'}
        }
    )
    def put(self, request, id):
        """Update blog post matching old Swagger format."""
        try:
            post = BlogPost.objects.get(id=id)
        except BlogPost.DoesNotExist:
            return create_error_response(
                error_message=f'Blog post with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = BlogPostCreateRequestSerializer(data=request.data)
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
        
        # Handle category (use first categoryId or parentId)
        category_id = None
        if validated_data.get('categoryIds'):
            category_id = validated_data.get('categoryIds')[0]
        elif validated_data.get('parentId'):
            category_id = validated_data.get('parentId')
        
        category = None
        if category_id:
            try:
                category = BlogCategory.objects.get(id=category_id)
            except BlogCategory.DoesNotExist:
                return create_error_response(
                    error_message=f'Category with ID "{category_id}" not found.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'categoryIds': [f'Category with ID "{category_id}" not found.']}
                )
        
        # Handle published_at
        published_at = validated_data.get('published')
        is_published = published_at is not None if published_at else post.is_published
        
        # Update post fields
        if 'title' in validated_data:
            post.title = validated_data.get('title')
        if 'slug' in validated_data:
            post.slug = validated_data.get('slug') or ''
        if 'content' in validated_data:
            post.content = validated_data.get('content')
        if 'summery' in validated_data:
            post.excerpt = validated_data.get('summery') or ''
        if 'imageUrl' in validated_data:
            post.featured_image = validated_data.get('imageUrl') or ''
        if category:
            post.category = category
        if 'authorId' in validated_data:
            post.author_name = validated_data.get('authorId') or ''
        if published_at is not None:
            post.published_at = published_at
            post.is_published = is_published
        if 'locale' in validated_data:
            post.locale = validated_data.get('locale') or 'fa'
        
        post.save()
        
        # Handle tags (ManyToMany)
        tag_ids = validated_data.get('tagIds', [])
        if tag_ids is not None:  # Only update if tagIds is provided
            try:
                tags = BlogTag.objects.filter(id__in=tag_ids)
                if tags.count() != len(tag_ids):
                    # Some tags not found
                    found_ids = set(tags.values_list('id', flat=True))
                    missing_ids = set(tag_ids) - found_ids
                    return create_error_response(
                        error_message=f'Some tags not found: {list(missing_ids)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'tagIds': [f'Tags with IDs {list(missing_ids)} not found.']}
                    )
                post.tags.set(tags)
            except Exception as e:
                return create_error_response(
                    error_message=f'Error setting tags: {str(e)}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'tagIds': [str(e)]}
                )
        
        # Return updated post
        serializer = BlogPostCompatibilitySerializer(post)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_delete',
        summary='Deletes a blog post by its ID',
        description='Deletes a blog post by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Blog post ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Blog post deleted successfully',
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
            404: {'description': 'Blog post not found'}
        }
    )
    def delete(self, request, id):
        """Delete blog post matching old Swagger format."""
        try:
            post = BlogPost.objects.get(id=id)
            post.delete()  # Hard delete
            return create_success_response(data=None)
        except BlogPost.DoesNotExist:
            return create_error_response(
                error_message=f'Blog post with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_search',
    summary='Search blog posts using available Filters',
    description='Search blog posts using available Filters matching old Swagger format.',
    request=BlogPostSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Search blog posts',
            value={
                'advancedSearch': {
                    'fields': ['string'],
                    'keyword': 'new',
                    'groupBy': ['']
                },
                'keyword': 'new',
                'pageNumber': 0,
                'pageSize': 1,
                'orderBy': [''],
                'type': 0
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
class BlogPostsSearchView(APIView):
    """POST /api/v1/blogposts/search - Search blog posts (admin)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search blog posts matching old Swagger format."""
        # Validate input
        serializer = BlogPostSearchRequestSerializer(data=request.data)
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
        
        # Build query - admin search can see all posts (published and unpublished)
        qs = BlogPost.objects.all().select_related('category').prefetch_related('tags')
        
        # Apply keyword search
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(title__icontains=keyword.strip()) |
                Q(content__icontains=keyword.strip()) |
                Q(excerpt__icontains=keyword.strip()) |
                Q(author_name__icontains=keyword.strip())
            )
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Parse orderBy fields (e.g., "published_at", "-published_at" for descending)
            order_fields = []
            for field in order_by:
                if field and field.strip():
                    # Map old Swagger field names to Django model fields
                    field_mapping = {
                        'newest': '-published_at',
                        'Newest': '-published_at',
                        'oldest': 'published_at',
                        'Oldest': 'published_at',
                        'published': '-published_at',
                        '-published': 'published_at',
                        'title': 'title',
                        '-title': '-title',
                        'created': '-created_at',
                        '-created': 'created_at',
                    }
                    mapped_field = field_mapping.get(field.strip())
                    if mapped_field:
                        order_fields.append(mapped_field)
                    # If not in mapping, skip it (don't use field.strip() directly to avoid FieldError)
            if order_fields:
                qs = qs.order_by(*order_fields)
            else:
                # If no valid fields, use default ordering
                qs = qs.order_by('-published_at', '-created_at')
        else:
            # Default ordering
            qs = qs.order_by('-published_at', '-created_at')
        
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
            posts = qs[start:end]
        else:
            posts = qs[start:]
        
        # Serialize results using compatibility serializer
        post_serializer = BlogPostCompatibilitySerializer(posts, many=True)
        
        # Build response matching old Swagger format
        response_data = {
            'data': post_serializer.data,
            'currentPage': page_number if page_size > 0 else 1,
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
    tags=['BlogPosts'],
    operation_id='blogposts_client_search',
    summary='Search blog posts for client',
    description='Search blog posts for client-side use matching old Swagger format.',
    request=BlogPostClientSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Client search blog posts',
            value={
                'pageNumber': 0,
                'pageSize': 1,
                'orderBy': [''],
                'keyword': 'new',
                'blogPostCategoryId': 1,
                'type': 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Paginated search results (nested)',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': {
                            'data': [],
                            'currentPage': 0,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 1,
                            'hasPreviousPage': False,
                            'hasNextPage': False,
                            'messages': None,
                            'succeeded': True
                        },
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'}
    }
)
class BlogPostsClientSearchView(APIView):
    """POST /api/v1/blogposts/client/search - Search blog posts (client)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Search blog posts for client matching old Swagger format with nested response."""
        # Validate input
        serializer = BlogPostClientSearchRequestSerializer(data=request.data)
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
        
        # Handle pageNumber 0 as page 1 (first page)
        if page_number == 0:
            page_number = 1
        
        # Get keyword
        keyword = validated_data.get('keyword') or ''
        
        # Get category filter
        category_id = validated_data.get('blogPostCategoryId')
        
        # Build query - client search only shows published posts
        qs = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags')
        
        # Apply category filter
        if category_id:
            qs = qs.filter(category_id=category_id)
        
        # Apply keyword search
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(title__icontains=keyword.strip()) |
                Q(content__icontains=keyword.strip()) |
                Q(excerpt__icontains=keyword.strip()) |
                Q(author_name__icontains=keyword.strip())
            )
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Parse orderBy fields
            order_fields = []
            for field in order_by:
                if field and field.strip():
                    # Map old Swagger field names to Django model fields
                    field_mapping = {
                        'newest': '-published_at',
                        'Newest': '-published_at',
                        'oldest': 'published_at',
                        'Oldest': 'published_at',
                        'title': 'title',
                        '-title': '-title',
                        'created': '-created_at',
                        '-created': 'created_at',
                    }
                    mapped_field = field_mapping.get(field.strip())
                    if mapped_field:
                        order_fields.append(mapped_field)
                    # If not in mapping, skip it (don't use field.strip() directly to avoid FieldError)
            if order_fields:
                qs = qs.order_by(*order_fields)
            else:
                # If no valid fields, use default ordering
                qs = qs.order_by('-published_at', '-created_at')
        else:
            # Default ordering
            qs = qs.order_by('-published_at', '-created_at')
        
        # Get total count
        total_count = qs.count()
        
        # Calculate pagination
        if page_size > 0:
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            start = (page_number - 1) * page_size
            # Ensure start is not negative
            if start < 0:
                start = 0
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
            posts = qs[start:end]
        else:
            posts = qs[start:]
        
        # Serialize results using compatibility serializer
        post_serializer = BlogPostCompatibilitySerializer(posts, many=True)
        
        # Build nested response matching old Swagger format
        # Use original pageNumber from request (0) in response, not the adjusted one
        original_page_number = validated_data.get('pageNumber', 0)
        inner_response = {
            'data': post_serializer.data,
            'currentPage': original_page_number,  # Return original pageNumber (0) in response
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous,
            'hasNextPage': has_next,
            'messages': None,  # Old Swagger shows null, not empty array
            'succeeded': True
        }
        
        # Wrap in outer response
        response_data = {
            'data': inner_response,
            'messages': [],
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


# ============================================================================
# SPECIAL ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_all',
    summary='Retrieves all blog posts',
    description='Retrieves all blog posts matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of all blog posts',
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
class BlogPostsAllView(APIView):
    """GET /api/v1/blogposts/all - Get all blog posts"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all blog posts matching old Swagger format."""
        posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
        serializer = BlogPostCompatibilitySerializer(posts, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_dapper',
    summary='Get blog posts (dapper context)',
    description='Get blog posts in dapper context. If id query parameter is provided, returns single post.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Blog post ID. If provided, returns single post.'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Blog post(s) data',
            examples=[
                OpenApiExample(
                    'Success response (single post)',
                    value={
                        'data': None,
                        'messages': [],
                        'succeeded': True
                    }
                ),
                OpenApiExample(
                    'Success response (all posts)',
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
class BlogPostsDapperView(APIView):
    """GET /api/v1/blogposts/dapper - Get blog posts (dapper context)"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get blog posts in dapper context matching old Swagger format."""
        post_id = request.query_params.get('id')
        
        if post_id:
            # Return single post by ID
            try:
                post = BlogPost.objects.get(id=int(post_id), is_published=True)
                serializer = BlogPostCompatibilitySerializer(post)
                return create_success_response(data=serializer.data)
            except (BlogPost.DoesNotExist, ValueError):
                # Return null if not found (matching old Swagger behavior)
                return create_success_response(data=None)
        else:
            # Return all published posts
            posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
            serializer = BlogPostCompatibilitySerializer(posts, many=True)
            return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_by_parentid',
    summary='Get blog posts by parent ID',
    description='Get blog posts by parent/category ID matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Parent/Category ID'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of blog posts for the category',
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
class BlogPostsByParentIdView(APIView):
    """GET /api/v1/blogposts/by-parentid/{id} - Get blog posts by parent/category ID"""
    permission_classes = [AllowAny]
    
    def get(self, request, id):
        """Get blog posts by category ID matching old Swagger format."""
        posts = BlogPost.objects.filter(category_id=id, is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
        serializer = BlogPostCompatibilitySerializer(posts, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_client_recents',
    summary='Get recent blog posts for client',
    description='Get recent blog posts for client-side use matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='count',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Number of recent posts to return'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of recent blog posts',
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
class BlogPostsClientRecentsView(APIView):
    """GET /api/v1/blogposts/client/recents/{count} - Get recent blog posts for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, count):
        """Get recent blog posts for client matching old Swagger format."""
        posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')[:count]
        serializer = BlogPostCompatibilitySerializer(posts, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_client_byslug',
    summary='Get blog post by slug for client',
    description='Get blog post by slug for client-side use matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='slug',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='Blog post slug'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Blog post details',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': {
                            'id': 1,
                            'authorId': 'string',
                            'parentId': 0,
                            'title': 'string',
                            'type': 0,
                            'metaTitle': 'string',
                            'slug': 'string',
                            'imageUrl': 'string',
                            'thumbnail': 'string',
                            'summery': 'string',
                            'content': 'string',
                            'published': '2025-11-09T08:33:15.734Z',
                            'categories': 'string',
                            'categoryIds': [0],
                            'tags': 'string',
                            'tagIds': [0],
                            'productIds': ['string'],
                            'locale': 'string',
                            'files': []
                        },
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        ),
        404: {'description': 'Blog post not found'}
    }
)
class BlogPostsClientBySlugView(APIView):
    """GET /api/v1/blogposts/client/byslug/{slug} - Get blog post by slug for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Get blog post by slug for client matching old Swagger format."""
        try:
            post = BlogPost.objects.get(slug=slug, is_published=True)
            # Increment views count
            post.views_count += 1
            post.save(update_fields=['views_count'])
            serializer = BlogPostCompatibilitySerializer(post)
            return create_success_response(data=serializer.data)
        except BlogPost.DoesNotExist:
            return create_error_response(
                error_message=f'Blog post with slug "{slug}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

