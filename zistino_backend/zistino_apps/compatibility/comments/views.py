"""
Compatibility views for Comments endpoints.
All endpoints will appear under "Comments" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Comments
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

from zistino_apps.notifications.models import Comment
from zistino_apps.notifications.serializers import CommentSerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    CommentSearchRequestSerializer,
    CommentCreateSerializer,
    CommentCreateRequestSerializer,
    CommentAnonymousSerializer,
    CommentAnonymousRequestSerializer,
    CommentByUserIdSerializer,
    CommentByUserIdRequestSerializer,
    CommentNotifyMeSerializer,
    CommentCompatibilitySerializer,
    CommentWithChildrenSerializer
)


@extend_schema(tags=['Comments'])
class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    All endpoints will appear under "Comments" folder in Swagger UI.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return all comments for admin, user's own comments for authenticated users."""
        if self.action in ['list', 'retrieve']:
            # For GET requests, return accepted comments only
            return Comment.objects.filter(is_accepted=True).select_related('user', 'product', 'parent').order_by('-created_on')
        # For admin operations, return all
        return Comment.objects.all().select_related('user', 'product', 'parent').order_by('-created_on')

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'searchadmin']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Set user when creating comment."""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # For anonymous comments, user will be None
            serializer.save()

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_create',
        summary='Create a new comment',
        description='Creates a new comment matching old Swagger format.',
        request=CommentCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create comment (default values)',
                value={
                    'parentId': 0,
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'trackId': 0,
                    'blogId': 0,
                    'files': 'string',
                    'helpFul': 0,
                    'reported': 0,
                    'title': 'string',
                    'type': 0,
                    'rate': 0,
                    'text': 'string',
                    'isAccepted': True
                }
            ),
            OpenApiExample(
                'Create comment (actual values)',
                value={
                    'parentId': 1,
                    'productId': '94860000-b419-c60d-e381-08de1e92a377',
                    'examId': None,
                    'jobId': None,
                    'trackId': None,
                    'blogId': None,
                    'files': 'string',
                    'helpFul': 0,
                    'reported': 0,
                    'title': 'string',
                    'type': 0,
                    'rate': 0,
                    'text': 'asd',
                    'isAccepted': True
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 10002,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Product not found'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new comment matching old Swagger format. Returns comment ID."""
        # Validate input using old Swagger format serializer
        # text is required for create
        if not request.data.get('text'):
            return create_error_response(
                error_message='text is required',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'text': ['text is required']}
            )
        
        input_serializer = CommentCreateRequestSerializer(data=request.data)
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
        product_id = validated_data.get('productId')
        
        # productId is required for create
        if not product_id or product_id == 'string':
            return create_error_response(
                error_message='productId is required and must be a valid UUID',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'productId': ['productId is required and must be a valid UUID']}
            )
        
        # Validate product exists
        from zistino_apps.products.models import Product
        import uuid
        try:
            product_uuid = uuid.UUID(product_id)
            product = Product.objects.get(id=product_uuid, is_active=True)
        except Product.DoesNotExist:
            return create_error_response(
                error_message=f'Product with ID "{product_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'productId': [f'Product with ID "{product_id}" not found.']}
            )
        
        # Handle parentId (0 or null means no parent)
        parent_id = validated_data.get('parentId')
        parent = None
        if parent_id and parent_id > 0:
            try:
                parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                return create_error_response(
                    error_message=f'Parent comment with ID "{parent_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'parentId': [f'Parent comment with ID "{parent_id}" not found.']}
                )
        
        # Get user (must be authenticated for this endpoint)
        user = request.user
        if not user.is_authenticated:
            return create_error_response(
                error_message='Authentication required',
                status_code=status.HTTP_401_UNAUTHORIZED,
                errors={'authentication': ['Authentication required']}
            )
        
        # Create comment
        comment = Comment.objects.create(
            user=user,
            product=product,
            parent=parent,
            rate=validated_data.get('rate', 0),
            text=validated_data.get('text', ''),
            is_accepted=validated_data.get('isAccepted', True),  # Admin can set this
            user_full_name=validated_data.get('user_full_name', '') or (user.first_name + ' ' + user.last_name).strip() or user.username or '',
            user_image_url=validated_data.get('user_image_url', ''),
            product_image=validated_data.get('product_image', '')
        )
        
        # Return just the comment ID wrapped in standard response
        return create_success_response(data=comment.id)  # 200 OK to match old Swagger

    def _perform_search(self, request, filter_accepted=True, reverse_order=False):
        """Helper method to perform comment search with old Swagger format."""
        # Validate input
        serializer = CommentSearchRequestSerializer(data=request.data)
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
        if filter_accepted:
            qs = Comment.objects.filter(is_accepted=True).select_related('user', 'product', 'parent')
        else:
            qs = Comment.objects.all().select_related('user', 'product', 'parent')
        
        # Apply keyword search
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(text__icontains=keyword.strip()) |
                Q(user_full_name__icontains=keyword.strip()) |
                Q(user__phone_number__icontains=keyword.strip()) |
                Q(user__username__icontains=keyword.strip())
            )
        
        # Filter by productId
        product_id = validated_data.get('productId')
        if product_id and product_id.strip() and product_id != 'string':
            try:
                import uuid
                product_uuid = uuid.UUID(product_id)
                qs = qs.filter(product_id=product_uuid)
            except (ValueError, TypeError):
                pass  # Invalid UUID, skip filter
        
        # Filter by isAccepted (only if filter_accepted is False, otherwise already filtered)
        if not filter_accepted:
            is_accepted = validated_data.get('isAccepted')
            if is_accepted is not None:
                qs = qs.filter(is_accepted=is_accepted)
        
        # Filter by parentId
        parent_id = validated_data.get('parentId')
        if parent_id is not None:
            if parent_id == 0:
                # Top-level comments (no parent)
                qs = qs.filter(parent__isnull=True)
            elif parent_id > 0:
                # Replies to specific parent
                qs = qs.filter(parent_id=parent_id)
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Validate fields exist in Comment model
            valid_fields = ['id', 'created_on', 'rate', 'text', 'is_accepted']
            order_fields = []
            invalid_fields = []
            
            for field in order_by:
                if field and field.strip():
                    # Remove leading minus for validation
                    field_name = field.strip().lstrip('-')
                    # Map old Swagger field names to Django field names
                    field_mapping = {
                        'createdOn': 'created_on',
                        'isAccepted': 'is_accepted',
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
                    if reverse_order:
                        qs = qs.order_by('created_on')
                    else:
                        qs = qs.order_by('-created_on')
            else:
                if reverse_order:
                    qs = qs.order_by('created_on')
                else:
                    qs = qs.order_by('-created_on')
        else:
            # Default ordering
            if reverse_order:
                qs = qs.order_by('created_on')  # Oldest first
            else:
                qs = qs.order_by('-created_on')  # Newest first
        
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
        
        # Serialize results using compatibility serializer
        item_serializer = CommentCompatibilitySerializer(items, many=True, context={'request': request})
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

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_search',
        summary='Search Comment using available Filters',
        description='Search Comment using available Filters matching old Swagger format.',
        request=CommentSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search comments',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'string',
                        'groupBy': ['string']
                    },
                    'keyword': 'string',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string'],
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'blogId': 0,
                    'trackId': 0,
                    'isAccepted': True
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
        """Search comments with pagination (admin) matching old Swagger format."""
        return self._perform_search(request, filter_accepted=False)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_searchadmin',
        summary='Search Comment using available Filters',
        description='Search Comment using available Filters (admin) matching old Swagger format.',
        request=CommentSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search comments',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'string',
                        'groupBy': ['string']
                    },
                    'keyword': 'string',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string'],
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'blogId': 0,
                    'trackId': 0,
                    'isAccepted': True
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
    @action(detail=False, methods=['post'], url_path='searchadmin', permission_classes=[IsAuthenticated, IsManager])
    def searchadmin(self, request):
        """Admin search comments with pagination matching old Swagger format."""
        return self._perform_search(request, filter_accepted=False)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_dapper',
        summary='Get comments (dapper context)',
        description='Get comments in dapper context. If id query parameter is provided, returns single comment. Otherwise returns null.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Comment ID. If provided, returns single comment.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment data or null',
                examples=[
                    OpenApiExample(
                        'Success response (with id)',
                        value={
                            'data': {
                                'id': 10002,
                                'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                'userEmail': 'admin@root.com',
                                'userPhoneNumber': '09876543212',
                                'userFullName': 'مدیر آروین ویرا',
                                'userThumbnail': '/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp',
                                'parentId': 1,
                                'productId': '94860000-b419-c60d-e381-08de1e92a377',
                                'productName': 'new',
                                'examId': None,
                                'jobId': None,
                                'blogId': None,
                                'files': 'string',
                                'helpFul': 0,
                                'reported': 0,
                                'title': 'string',
                                'type': 0,
                                'rate': 0,
                                'text': 'asd',
                                'isAccepted': True,
                                'createdOn': '2025-11-09T12:26:42.6895487'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    ),
                    OpenApiExample(
                        'Success response (without id)',
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
        """Get comments in dapper context matching old Swagger format."""
        comment_id = request.query_params.get('id')
        
        if comment_id:
            # Return single comment by ID
            try:
                comment = Comment.objects.select_related('user', 'product', 'parent').get(id=int(comment_id))
                serializer = CommentCompatibilitySerializer(comment, context={'request': request})
                return create_success_response(data=serializer.data)
            except (Comment.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Comment with ID "{comment_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return null if no id provided
            return create_success_response(data=None)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_retrieve',
        summary='Retrieve a comment by ID',
        description='Retrieves a comment by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Comment ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 10002,
                                'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                'userEmail': 'admin@root.com',
                                'userPhoneNumber': '09876543212',
                                'userFullName': 'مدیر آروین ویرا',
                                'userThumbnail': '/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp',
                                'parentId': 1,
                                'productId': '94860000-b419-c60d-e381-08de1e92a377',
                                'productName': 'new',
                                'examId': None,
                                'jobId': None,
                                'blogId': None,
                                'files': 'string',
                                'helpFul': 0,
                                'reported': 0,
                                'title': 'string',
                                'type': 0,
                                'rate': 0,
                                'text': 'asd',
                                'isAccepted': True,
                                'createdOn': '2025-11-09T12:26:42.6895487'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Comment not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a comment by ID matching old Swagger format."""
        instance = self.get_object()
        serializer = CommentCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_update',
        summary='Update a comment by ID',
        description='Updates an existing comment by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Comment ID'
            )
        ],
        request=CommentCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update comment',
                value={
                    'parentId': 1,
                    'productId': '94860000-b419-c60d-e381-08de1e92a377',
                    'examId': None,
                    'jobId': None,
                    'trackId': None,
                    'blogId': None,
                    'files': 'string',
                    'helpFul': 0,
                    'reported': 0,
                    'title': 'string',
                    'type': 0,
                    'rate': 5,
                    'text': 'Updated comment text',
                    'isAccepted': True
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 10002,
                                'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                'userEmail': 'admin@root.com',
                                'userPhoneNumber': '09876543212',
                                'userFullName': 'مدیر آروین ویرا',
                                'userThumbnail': '/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp',
                                'parentId': 1,
                                'productId': '94860000-b419-c60d-e381-08de1e92a377',
                                'productName': 'new',
                                'examId': None,
                                'jobId': None,
                                'blogId': None,
                                'files': 'string',
                                'helpFul': 0,
                                'reported': 0,
                                'title': 'string',
                                'type': 0,
                                'rate': 5,
                                'text': 'Updated comment text',
                                'isAccepted': True,
                                'createdOn': '2025-11-09T12:26:42.6895487'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Comment not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a comment by ID matching old Swagger format."""
        instance = self.get_object()
        
        # Validate input using old Swagger format serializer
        input_serializer = CommentCreateRequestSerializer(data=request.data)
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
        # Handle parentId (0 or null means no parent)
        parent_id = validated_data.get('parentId')
        parent = None
        if parent_id and parent_id > 0:
            try:
                parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                return create_error_response(
                    error_message=f'Parent comment with ID "{parent_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'parentId': [f'Parent comment with ID "{parent_id}" not found.']}
                )
        
        # Update comment fields
        if 'text' in validated_data:
            instance.text = validated_data.get('text', '')
        if 'rate' in validated_data:
            instance.rate = validated_data.get('rate', 0)
        if 'isAccepted' in validated_data:
            instance.is_accepted = validated_data.get('isAccepted', True)
        if parent is not None:
            instance.parent = parent
        
        instance.save()
        
        # Return updated comment in old Swagger format
        serializer = CommentCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_partial_update',
        summary='Partially update a comment by ID',
        description='Partially updates an existing comment by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Comment ID'
            )
        ],
        request=CommentCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 10002,
                                'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                'userEmail': 'admin@root.com',
                                'userPhoneNumber': '09876543212',
                                'userFullName': 'مدیر آروین ویرا',
                                'userThumbnail': '/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp',
                                'parentId': 1,
                                'productId': '94860000-b419-c60d-e381-08de1e92a377',
                                'productName': 'new',
                                'examId': None,
                                'jobId': None,
                                'blogId': None,
                                'files': 'string',
                                'helpFul': 0,
                                'reported': 0,
                                'title': 'string',
                                'type': 0,
                                'rate': 5,
                                'text': 'Updated comment text',
                                'isAccepted': True,
                                'createdOn': '2025-11-09T12:26:42.6895487'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Comment not found'}
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a comment by ID matching old Swagger format."""
        instance = self.get_object()
        
        # Validate input using old Swagger format serializer (partial=True allows partial updates)
        input_serializer = CommentCreateRequestSerializer(data=request.data, partial=True)
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
        
        # Handle parentId (0 or null means no parent)
        if 'parentId' in validated_data:
            parent_id = validated_data.get('parentId')
            parent = None
            if parent_id and parent_id > 0:
                try:
                    parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    return create_error_response(
                        error_message=f'Parent comment with ID "{parent_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'parentId': [f'Parent comment with ID "{parent_id}" not found.']}
                    )
            instance.parent = parent
        
        # Update only provided fields
        if 'text' in validated_data:
            instance.text = validated_data.get('text', '')
        if 'rate' in validated_data:
            instance.rate = validated_data.get('rate', 0)
        if 'isAccepted' in validated_data:
            instance.is_accepted = validated_data.get('isAccepted', True)
        
        instance.save()
        
        # Return updated comment in old Swagger format
        serializer = CommentCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_destroy',
        summary='Delete a comment by ID',
        description='Deletes a comment by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Comment ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment deleted successfully',
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
            404: {'description': 'Comment not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a comment by ID matching old Swagger format."""
        instance = self.get_object()
        instance.delete()  # Hard delete
        return create_success_response(data=None)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_comment_status',
        summary='Update comment status',
        description='Update comment status (accept/reject) matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Comment ID'
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'is_accepted': {'type': 'boolean', 'description': 'Accept or reject comment'},
                }
            }
        },
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment status updated successfully',
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
            404: {'description': 'Comment not found'}
        }
    )
    @action(detail=True, methods=['put'], url_path='comment-status', permission_classes=[IsAuthenticated, IsManager])
    def comment_status(self, request, pk=None):
        """Update comment status matching old Swagger format. Returns comment ID."""
        comment = self.get_object()
        is_accepted = request.data.get('is_accepted', comment.is_accepted)
        comment.is_accepted = is_accepted
        comment.save()
        # Return comment ID wrapped in standard response
        return create_success_response(data=comment.id)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_client_post',
        summary='Create comment for client',
        description='Create a comment for the authenticated user matching old Swagger format.',
        request=CommentCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create comment (default values)',
                value={
                    'parentId': 0,
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'trackId': 0,
                    'blogId': 0,
                    'files': 'string',
                    'helpFul': 0,
                    'reported': 0,
                    'title': 'string',
                    'type': 0,
                    'rate': 0,
                    'text': 'string',
                    'isAccepted': True
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 10003,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Product not found'}
        }
    )
    @action(detail=False, methods=['post'], url_path='client', permission_classes=[IsAuthenticated])
    def client_post(self, request):
        """Create comment for authenticated user matching old Swagger format. Returns comment ID."""
        # Validate input using old Swagger format serializer
        input_serializer = CommentCreateRequestSerializer(data=request.data)
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
        product_id = validated_data.get('productId')
        
        # productId is required for create
        if not product_id or product_id == 'string':
            return create_error_response(
                error_message='productId is required and must be a valid UUID',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'productId': ['productId is required and must be a valid UUID']}
            )
        
        # Validate product exists
        from zistino_apps.products.models import Product
        import uuid
        try:
            product_uuid = uuid.UUID(product_id)
            product = Product.objects.get(id=product_uuid, is_active=True)
        except Product.DoesNotExist:
            return create_error_response(
                error_message=f'Product with ID "{product_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'productId': [f'Product with ID "{product_id}" not found.']}
            )
        
        # Handle parentId (0 or null means no parent)
        parent_id = validated_data.get('parentId')
        parent = None
        if parent_id and parent_id > 0:
            try:
                parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                return create_error_response(
                    error_message=f'Parent comment with ID "{parent_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'parentId': [f'Parent comment with ID "{parent_id}" not found.']}
                )
        
        # Create comment
        comment = Comment.objects.create(
            user=request.user,
            product=product,
            parent=parent,
            rate=validated_data.get('rate', 0),
            text=validated_data.get('text', ''),
            is_accepted=False,  # Comments need admin approval
            user_full_name=validated_data.get('user_full_name', '') or (request.user.first_name + ' ' + request.user.last_name).strip() or request.user.username or '',
            user_image_url=validated_data.get('user_image_url', ''),
            product_image=validated_data.get('product_image', '')
        )
        
        # Return just the comment ID wrapped in standard response
        return create_success_response(data=comment.id)  # 200 OK to match old Swagger

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_client_anonymous',
        summary='Create anonymous comment',
        description='Create an anonymous comment (no authentication required) matching old Swagger format.',
        request=CommentAnonymousRequestSerializer,
        examples=[
            OpenApiExample(
                'Create anonymous comment (default values)',
                value={
                    'parentId': 0,
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'trackId': 0,
                    'blogId': 0,
                    'files': 'string',
                    'helpFul': 0,
                    'reported': 0,
                    'title': 'string',
                    'type': 0,
                    'rate': 0,
                    'text': 'string',
                    'isAccepted': True
                }
            ),
            OpenApiExample(
                'Create anonymous comment (actual values)',
                value={
                    'parentId': 1,
                    'productId': '94860000-b419-c60d-2b41-08dc425c06b1',
                    'examId': None,
                    'jobId': None,
                    'trackId': None,
                    'blogId': None,
                    'files': 'string',
                    'helpFul': 0,
                    'reported': 0,
                    'title': 'string',
                    'type': 0,
                    'rate': 4,
                    'text': 'string',
                    'isAccepted': True
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 10004,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Product not found'}
        }
    )
    @action(detail=False, methods=['post'], url_path='client/anonymous', permission_classes=[AllowAny])
    def client_anonymous(self, request):
        """Create anonymous comment matching old Swagger format. Returns comment ID."""
        try:
            # Validate input using old Swagger format serializer
            input_serializer = CommentAnonymousRequestSerializer(data=request.data)
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
            product_id = validated_data.get('productId')
            
            # Validate product exists
            from zistino_apps.products.models import Product
            import uuid
            try:
                product_uuid = uuid.UUID(product_id)
                product = Product.objects.get(id=product_uuid, is_active=True)
            except Product.DoesNotExist:
                return create_error_response(
                    error_message=f'Product with ID "{product_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'productId': [f'Product with ID "{product_id}" not found.']}
                )
            
            # Handle parentId (0 or null means no parent)
            parent_id = validated_data.get('parentId')
            parent = None
            if parent_id and parent_id > 0:
                try:
                    parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    return create_error_response(
                        error_message=f'Parent comment with ID "{parent_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'parentId': [f'Parent comment with ID "{parent_id}" not found.']}
                    )
            
            # Create anonymous comment
            # Since Comment model requires a user, we need to get or create an anonymous user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get or create an anonymous user for anonymous comments
            anonymous_user, created = User.objects.get_or_create(
                phone_number='anonymous',
                defaults={
                    'username': 'anonymous',
                    'email': 'anonymous@example.com',
                    'is_active': True,
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            try:
                comment = Comment.objects.create(
                    user=anonymous_user,  # Use anonymous user for anonymous comments
                    product=product,
                    parent=parent,
                    rate=validated_data.get('rate', 0),
                    text=validated_data.get('text', ''),
                    is_accepted=False,  # Comments need admin approval
                    user_full_name='',  # Anonymous comments don't have user_full_name in old Swagger
                    user_image_url='',
                    product_image=''
                )
            except Exception as e:
                # Handle database integrity errors and other exceptions
                from django.db import IntegrityError
                error_detail = str(e)
                error_type = type(e).__name__
                
                if isinstance(e, IntegrityError):
                    # Check for common integrity error messages
                    if 'UNIQUE constraint' in error_detail or 'unique constraint' in error_detail.lower():
                        return create_error_response(
                            error_message='A comment with these details already exists.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'comment': ['A comment with these details already exists.']}
                        )
                    elif 'NOT NULL constraint' in error_detail or 'not null constraint' in error_detail.lower() or 'user_id' in error_detail.lower():
                        # Check if it's a user field issue
                        if 'user' in error_detail.lower() or 'user_id' in error_detail.lower():
                            return create_error_response(
                                error_message='User field is required. Anonymous comments require a user account.',
                                status_code=status.HTTP_400_BAD_REQUEST,
                                errors={'user': ['User field is required. Anonymous comments require a user account.']}
                            )
                        return create_error_response(
                            error_message='Required fields are missing.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'comment': ['Required fields are missing.']}
                        )
                    elif 'FOREIGN KEY constraint' in error_detail or 'foreign key constraint' in error_detail.lower():
                        return create_error_response(
                            error_message='Invalid reference to related object.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'comment': ['Invalid reference to related object.']}
                        )
                    else:
                        return create_error_response(
                            error_message='Database constraint violation. Please check your input.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'comment': ['Database constraint violation. Please check your input.']}
                        )
                else:
                    # For other exceptions, return generic error
                    return create_error_response(
                        error_message=f'An error occurred while creating the comment: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{error_type}: {error_detail}']}
                    )
            
            # Return just the comment ID wrapped in standard response
            return create_success_response(data=comment.id)  # 200 OK to match old Swagger
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            # Check if it's a JSON parsing error
            if 'JSON' in error_type or 'json' in error_detail.lower() or 'parse' in error_detail.lower():
                return create_error_response(
                    error_message='Invalid JSON in request body',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'request': ['Invalid JSON format. Please check your request body.']}
                )
            
            # For other exceptions, return generic error
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_client_search',
        summary='Search comments for client',
        description='Search comments for client-side use matching old Swagger format.',
        request=CommentSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search comments',
                value={
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string'],
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'blogId': 0,
                    'trackId': 0,
                    'parentId': 0
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
    @action(detail=False, methods=['post'], url_path='client/search', permission_classes=[AllowAny])
    def client_search(self, request):
        """Search comments for client matching old Swagger format."""
        return self._perform_search(request, filter_accepted=True, reverse_order=False)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_client_searchrevers',
        summary='Search comments in reverse order',
        description='Search comments in reverse order (oldest first) matching old Swagger format.',
        request=CommentSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search comments',
                value={
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string'],
                    'productId': 'string',
                    'examId': 0,
                    'jobId': 0,
                    'blogId': 0,
                    'trackId': 0,
                    'parentId': 0
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
    @action(detail=False, methods=['post'], url_path='client/searchrevers', permission_classes=[AllowAny])
    def client_searchrevers(self, request):
        """Search comments in reverse order matching old Swagger format."""
        return self._perform_search(request, filter_accepted=True, reverse_order=True)

    @extend_schema(
        tags=['Comments'],
        operation_id='comments_client_by_userid',
        summary='Get comments by user ID',
        description='Get comments for a specific user ID with pagination matching old Swagger format.',
        request=CommentByUserIdRequestSerializer,
        examples=[
            OpenApiExample(
                'Get comments by user ID',
                value={
                    'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string']
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Paginated comments with children',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 2,
                                    'parentId': None,
                                    'children': [],
                                    'productId': '70a90000-324a-a6f6-7e45-08dac60d6175',
                                    'productName': None,
                                    'productImage': None,
                                    'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                    'userFullName': 'مدیر آروین ویرا',
                                    'userThumbnail': '/uploads/app/140b51ba994e4bbfa885d89860654c75.180.webp',
                                    'examId': 0,
                                    'jobId': None,
                                    'blogId': None,
                                    'files': '',
                                    'helpFul': None,
                                    'reported': None,
                                    'title': '',
                                    'type': None,
                                    'rate': 3,
                                    'text': '[{"text":"رفتار محترمانه","type":true},{"text":"وضعیت ظاهری و بهداشتی راننده","type":true}]',
                                    'isAccepted': True,
                                    'createdOn': '2025-10-13T06:05:06.7778209'
                                }
                            ],
                            'currentPage': 1,
                            'totalPages': 3,
                            'totalCount': 3,
                            'pageSize': 1,
                            'hasPreviousPage': False,
                            'hasNextPage': True,
                            'messages': None,
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='client/by-userid', permission_classes=[AllowAny])
    def client_by_userid(self, request):
        """Get comments by user ID with pagination matching old Swagger format."""
        # Validate input
        serializer = CommentByUserIdRequestSerializer(data=request.data)
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
        user_id = validated_data.get('userId')
        
        # Get pagination parameters (can be 0)
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        # Build query - only top-level comments (no parent) for user
        qs = Comment.objects.filter(
            user_id=user_id,
            is_accepted=True,
            parent__isnull=True  # Only top-level comments
        ).select_related('user', 'product', 'parent').prefetch_related('children')
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Validate fields exist in Comment model
            valid_fields = ['id', 'created_on', 'rate', 'text', 'is_accepted']
            order_fields = []
            invalid_fields = []
            
            for field in order_by:
                if field and field.strip():
                    # Remove leading minus for validation
                    field_name = field.strip().lstrip('-')
                    # Map old Swagger field names to Django field names
                    field_mapping = {
                        'createdOn': 'created_on',
                        'isAccepted': 'is_accepted',
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
                    qs = qs.order_by('-created_on')
            else:
                qs = qs.order_by('-created_on')
        else:
            # Default ordering
            qs = qs.order_by('-created_on')
        
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
        
        # Serialize results using compatibility serializer with children
        item_serializer = CommentWithChildrenSerializer(items, many=True, context={'request': request})
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


    @extend_schema(
        tags=['Comments'],
        operation_id='comments_notifyme',
        summary='Notify me about comments',
        description='Subscribe to notifications for comments on a product matching old Swagger format.',
        request=CommentNotifyMeSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Notification subscription',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value='done'
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='notifyme', permission_classes=[IsAuthenticated])
    def notifyme(self, request):
        """Subscribe to comment notifications matching old Swagger format. Returns 'done'."""
        serializer = CommentNotifyMeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Implement notification subscription
        # For now, return 'done' as per old Swagger
        return Response('done', status=status.HTTP_200_OK)


# ============================================================================
# SEPARATE APIView CLASSES FOR CLIENT ENDPOINTS WITH PATH PARAMETERS
# ============================================================================

@extend_schema(
    tags=['Comments'],
    operation_id='comments_client_get',
    summary='Get comment for client',
    description='Get a comment by ID (only own comments) matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Comment ID'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Comment ID',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': 10002,
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        ),
        404: {'description': 'Comment not found'},
        403: {'description': 'Forbidden - not your comment'}
    }
)
class CommentClientDetailView(APIView):
    """GET/DELETE /api/v1/comments/client/{id} - Get/Delete comment for client"""
    permission_classes = [IsAuthenticated]
    
    def get_comment(self, pk):
        """Get comment and check ownership."""
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return None, create_error_response(
                error_message=f'Comment with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user owns the comment
        if comment.user != self.request.user:
            return None, create_error_response(
                error_message='You can only access your own comments.',
                status_code=status.HTTP_403_FORBIDDEN,
                errors={'permission': ['You can only access your own comments.']}
            )
        
        return comment, None
    
    def get(self, request, pk):
        """Get comment for authenticated user (only own comments) matching old Swagger format. Returns comment ID."""
        comment, error_response = self.get_comment(pk)
        if error_response:
            return error_response
        
        # Return just the comment ID wrapped in standard response
        return create_success_response(data=comment.id)
    
    @extend_schema(
        tags=['Comments'],
        operation_id='comments_client_delete',
        summary='Delete comment for client',
        description='Delete a comment (only own comments) matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Comment ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Comment deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 10002,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Comment not found'},
            403: {'description': 'Forbidden - not your comment'}
        }
    )
    def delete(self, request, pk):
        """Delete comment for authenticated user (only own comments) matching old Swagger format. Returns comment ID."""
        comment, error_response = self.get_comment(pk)
        if error_response:
            return error_response
        
        comment_id = comment.id
        comment.delete()
        # Return comment ID wrapped in standard response
        return create_success_response(data=comment_id)

