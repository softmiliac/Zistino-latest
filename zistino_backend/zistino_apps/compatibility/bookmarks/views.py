"""
Compatibility views for Bookmarks endpoints.
All endpoints will appear under "Bookmarks" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Bookmarks
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
import uuid

from zistino_apps.products.models import Bookmark, Product
from zistino_apps.authentication.models import User
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    BookmarkSerializer,
    BookmarkCompatibilitySerializer,
    BookmarkCreateRequestSerializer,
    BookmarkClientCreateRequestSerializer,
    BookmarkSearchRequestSerializer
)


@extend_schema(tags=['Bookmarks'])
class BookmarkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookmarks.
    All endpoints will appear under "Bookmarks" folder in Swagger UI.
    """
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return bookmarks for the current user."""
        return Bookmark.objects.filter(user=self.request.user).select_related('product', 'product__category').order_by('-created_at')

    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_list',
        summary='List all bookmarks',
        description='Get list of all bookmarks for the current user matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of bookmarks',
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
    def list(self, request, *args, **kwargs):
        """List all bookmarks for the current user matching old Swagger format."""
        bookmarks = self.get_queryset()
        serializer = BookmarkCompatibilitySerializer(bookmarks, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_search',
        summary='Search Bookmarks using available Filters',
        description='Search Bookmarks using available Filters matching old Swagger format.',
        request=BookmarkSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search bookmarks',
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
                            'messages': ['string'],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 0,
                                    'userId': 'string',
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
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search bookmarks with pagination matching old Swagger format."""
        serializer = BookmarkSearchRequestSerializer(data=request.data)
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

        qs = self.get_queryset()

        # Apply keyword search
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(product__name__icontains=keyword.strip()) |
                Q(product__description__icontains=keyword.strip())
            )

        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Parse orderBy fields (e.g., "created_at", "-created_at" for descending)
            order_fields = []
            for field in order_by:
                if field and field.strip():
                    # Map common field names
                    field_mapped = field.strip()
                    if field_mapped == 'createdAt' or field_mapped == 'created_at':
                        field_mapped = '-created_at'  # Default to descending for dates
                    elif field_mapped.startswith('-'):
                        # Already has descending indicator
                        pass
                    order_fields.append(field_mapped)
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

        # Use BookmarkCompatibilitySerializer to match old Swagger format (id, userId, content)
        bookmark_serializer = BookmarkCompatibilitySerializer(items, many=True)
        items_data = bookmark_serializer.data
        
        # Build response matching old Swagger format
        # If pageSize is 0, show actual number of items returned (or 1 if empty)
        response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 1)
        
        # Old Swagger format: messages and succeeded before data
        response_data = {
            'messages': ['string'],  # Old Swagger shows ["string"], not null
            'succeeded': True,
            'data': items_data,
            'currentPage': effective_page,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': response_page_size,
            'hasPreviousPage': has_previous,
            'hasNextPage': has_next
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_dapper',
        summary='Get bookmarks (dapper context)',
        description='Get bookmarks in dapper context. If id query parameter is provided, returns single bookmark.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Bookmark ID (integer hash). If provided, returns single bookmark.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark(s) data',
                examples=[
                    OpenApiExample(
                        'Success response (single bookmark)',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'content': 'bookmark'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    ),
                    OpenApiExample(
                        'Success response (all bookmarks)',
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
        """Get bookmarks in dapper context matching old Swagger format."""
        bookmark_id = request.query_params.get('id')
        
        if bookmark_id:
            # Return single bookmark by ID (integer hash)
            import hashlib
            bookmarks = self.get_queryset()
            bookmark = None
            
            # Try to find by matching hash
            for bm in bookmarks:
                bm_id_int = int(hashlib.md5(str(bm.id).encode()).hexdigest(), 16) % (10 ** 10)
                if bm_id_int == int(bookmark_id):
                    bookmark = bm
                    break
            
            if bookmark:
                serializer = BookmarkCompatibilitySerializer(bookmark)
                return create_success_response(data=serializer.data)
            else:
                return create_error_response(
                    error_message=f'Bookmark with ID "{bookmark_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all bookmarks
            bookmarks = self.get_queryset()
            serializer = BookmarkCompatibilitySerializer(bookmarks, many=True)
            return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_client_get',
        summary='Get Bookmarks of currently logged in user',
        description='Get Bookmarks of currently logged in user matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark data',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 2,
                                'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                'content': 'new client'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_client_post',
        summary='Set Bookmark for currently logged in user',
        description='Set Bookmark for currently logged in user matching old Swagger format.',
        request=BookmarkClientCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create bookmark (client)',
                value={
                    'content': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark created/retrieved successfully',
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
        },
        methods=['POST']
    )
    @action(detail=False, methods=['get', 'post'], url_path='client')
    def client(self, request):
        """Handle GET and POST for client bookmarks matching old Swagger format."""
        # Prepare response with old Swagger headers
        def add_old_swagger_headers(response):
            """Add headers matching old Swagger format."""
            response['access-control-allow-origin'] = '*'
            response['access-control-expose-headers'] = 'Upload-Offset,Location,Upload-Length,Tus-Version,Tus-Resumable,Tus-Max-Size,Tus-Extension,Upload-Metadata,Upload-Defer-Length,Upload-Concat,Location,Upload-Offset,Upload-Length'
            response['api-supported-versions'] = '1.0'
            response['server'] = 'Microsoft-IIS/10.0'
            response['x-powered-by'] = 'ASP.NET'
            return response
        
        if request.method == 'GET':
            """Get bookmarks of currently logged in user matching old Swagger format."""
            bookmarks = self.get_queryset()
            if bookmarks.exists():
                # Return first bookmark in compatibility format
                bookmark = bookmarks.first()
                serializer = BookmarkCompatibilitySerializer(bookmark)
                response = create_success_response(data=serializer.data)
            else:
                # Return empty/null if no bookmarks
                response = create_success_response(data=None)
            return add_old_swagger_headers(response)
        
        elif request.method == 'POST':
            """Set bookmark for currently logged in user matching old Swagger format. Returns bookmark ID."""
            # Validate input using old Swagger format serializer
            input_serializer = BookmarkClientCreateRequestSerializer(data=request.data)
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
            
            # Get product ID from content
            content = validated_data.get('content')
            
            # Try to parse as UUID or find product
            product = None
            try:
                product_uuid = uuid.UUID(content)
                try:
                    product = Product.objects.get(id=product_uuid, is_active=True)
                except Product.DoesNotExist:
                    pass
            except ValueError:
                # Not a UUID, try to find by name
                try:
                    product = Product.objects.get(name__iexact=content, is_active=True)
                except Product.DoesNotExist:
                    pass
            
            # If no product found, create a product with the content as name (old Swagger behavior)
            if not product:
                # Get or create a default category for bookmark products
                from zistino_apps.products.models import Category
                default_category, _ = Category.objects.get_or_create(
                    name='Bookmark Products',
                    defaults={
                        'description': 'Auto-created category for bookmark products',
                        'is_active': True
                    }
                )
                
                product, created = Product.objects.get_or_create(
                    name=content,
                    defaults={
                        'category': default_category,
                        'price_per_unit': 0.00,
                        'unit': 'piece',
                        'is_active': True,
                        'description': f'Auto-created bookmark product: {content}'
                    }
                )
            
            # Check if bookmark already exists
            bookmark, created = Bookmark.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={}
            )
            
            # Return just the bookmark ID wrapped in standard response
            # Convert UUID to integer for compatibility (using hash)
            import hashlib
            bookmark_id_int = int(hashlib.md5(str(bookmark.id).encode()).hexdigest(), 16) % (10 ** 10)
            response = create_success_response(data=bookmark_id_int, status_code=status.HTTP_200_OK)
            return add_old_swagger_headers(response)

    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_create',
        summary='Creates a new bookmark',
        description='Creates a new bookmark matching old Swagger format.',
        request=BookmarkCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create bookmark',
                value={
                    'userId': 'string',
                    'content': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark created successfully',
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
        """Create a new bookmark matching old Swagger format. Returns bookmark ID."""
        # Validate input using old Swagger format serializer
        input_serializer = BookmarkCreateRequestSerializer(data=request.data)
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
        
        # Get user - use userId if provided, otherwise use current user
        user = request.user
        if validated_data.get('userId'):
            try:
                user_id = uuid.UUID(validated_data.get('userId'))
                user = User.objects.get(id=user_id)
            except (ValueError, User.DoesNotExist):
                return create_error_response(
                    error_message=f'User with ID "{validated_data.get("userId")}" not found.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userId': [f'User with ID "{validated_data.get("userId")}" not found.']}
                )
        
        # Get product ID from content
        content = validated_data.get('content')
        
        # Try to parse as UUID or find product
        product = None
        try:
            product_uuid = uuid.UUID(content)
            try:
                product = Product.objects.get(id=product_uuid, is_active=True)
            except Product.DoesNotExist:
                pass
        except ValueError:
            # Not a UUID, try to find by name
            try:
                product = Product.objects.get(name__iexact=content, is_active=True)
            except Product.DoesNotExist:
                pass
        
        # If no product found, create a product with the content as name (old Swagger behavior)
        if not product:
            # Get or create a default category for bookmark products
            from zistino_apps.products.models import Category
            default_category, _ = Category.objects.get_or_create(
                name='Bookmark Products',
                defaults={
                    'description': 'Auto-created category for bookmark products',
                    'is_active': True
                }
            )
            
            product, created = Product.objects.get_or_create(
                name=content,
                defaults={
                    'category': default_category,
                    'price_per_unit': 0.00,
                    'unit': 'piece',
                    'is_active': True,
                    'description': f'Auto-created bookmark product: {content}'
                }
            )
        
        # Check if bookmark already exists
        bookmark, created = Bookmark.objects.get_or_create(
            user=user,
            product=product,
            defaults={}
        )
        
        # Return just the bookmark ID wrapped in standard response
        # Convert UUID to integer for compatibility (using hash)
        import hashlib
        bookmark_id_int = int(hashlib.md5(str(bookmark.id).encode()).hexdigest(), 16) % (10 ** 10)
        return create_success_response(data=bookmark_id_int)  # 200 OK to match old Swagger
    
    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_retrieve',
        summary='Retrieves a bookmark by its ID',
        description='Retrieves a bookmark by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Bookmark ID (integer hash)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'content': 'bookmark'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Bookmark not found'}
        }
    )
    def retrieve(self, request, pk=None):
        """Get bookmark by ID matching old Swagger format."""
        # Find bookmark by integer ID (hash of UUID)
        import hashlib
        bookmarks = self.get_queryset()
        bookmark = None
        
        # Try to find by matching hash
        for bm in bookmarks:
            bm_id_int = int(hashlib.md5(str(bm.id).encode()).hexdigest(), 16) % (10 ** 10)
            if bm_id_int == int(pk):
                bookmark = bm
                break
        
        if not bookmark:
            return create_error_response(
                error_message=f'Bookmark with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BookmarkCompatibilitySerializer(bookmark)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_update',
        summary='Updates an existing bookmark by its ID',
        description='Updates an existing bookmark by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Bookmark ID (integer hash)'
            )
        ],
        request=BookmarkCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update bookmark',
                value={
                    'userId': 'string',
                    'content': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'content': 'bookmark'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Bookmark not found'}
        }
    )
    def update(self, request, pk=None):
        """Update bookmark matching old Swagger format."""
        # Find bookmark by integer ID (hash of UUID)
        import hashlib
        bookmarks = self.get_queryset()
        bookmark = None
        
        # Try to find by matching hash
        for bm in bookmarks:
            bm_id_int = int(hashlib.md5(str(bm.id).encode()).hexdigest(), 16) % (10 ** 10)
            if bm_id_int == int(pk):
                bookmark = bm
                break
        
        if not bookmark:
            return create_error_response(
                error_message=f'Bookmark with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = BookmarkCreateRequestSerializer(data=request.data)
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
        
        # Get user - use userId if provided, otherwise keep current user
        if validated_data.get('userId'):
            try:
                user_id = uuid.UUID(validated_data.get('userId'))
                user = User.objects.get(id=user_id)
                bookmark.user = user
            except (ValueError, User.DoesNotExist):
                return create_error_response(
                    error_message=f'User with ID "{validated_data.get("userId")}" not found.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userId': [f'User with ID "{validated_data.get("userId")}" not found.']}
                )
        
        # Get product ID from content (serializer already validated and returned UUID string)
        content = validated_data.get('content')
        if content:
            # Content is already validated by serializer - it's either a UUID string or was converted to UUID string
            product_uuid = uuid.UUID(content)
            try:
                product = Product.objects.get(id=product_uuid, is_active=True)
                bookmark.product = product
            except Product.DoesNotExist:
                return create_error_response(
                    error_message='Product not found or inactive.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'content': ['Product not found or inactive.']}
                )
        
        bookmark.save()
        
        # Return updated bookmark in compatibility format
        serializer = BookmarkCompatibilitySerializer(bookmark)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Bookmarks'],
        operation_id='bookmarks_delete',
        summary='Deletes a bookmark by its ID',
        description='Deletes a bookmark by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Bookmark ID (integer hash)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Bookmark deleted successfully',
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
            404: {'description': 'Bookmark not found'}
        }
    )
    def destroy(self, request, pk=None):
        """Delete bookmark matching old Swagger format."""
        # Find bookmark by integer ID (hash of UUID)
        import hashlib
        bookmarks = self.get_queryset()
        bookmark = None
        
        # Try to find by matching hash
        for bm in bookmarks:
            bm_id_int = int(hashlib.md5(str(bm.id).encode()).hexdigest(), 16) % (10 ** 10)
            if bm_id_int == int(pk):
                bookmark = bm
                break
        
        if not bookmark:
            return create_error_response(
                error_message=f'Bookmark with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        bookmark.delete()
        return create_success_response(data=None)

