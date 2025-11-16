"""
Compatibility views for Categories endpoints.
All endpoints will appear under "Categories" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Categories
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count
from zistino_apps.users.permissions import IsManager

from zistino_apps.products.models import Category
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.products.serializers import URLImageField
from .serializers import (
    CategorySerializer, 
    CategorySearchRequestSerializer,
    CategoryCreateRequestSerializer,
    CategoryCompatibilitySerializer,
    CategoryClientSerializer
)


@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    All endpoints will appear under "Categories" folder in Swagger UI.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategoryCompatibilitySerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # Use 'id' as lookup field
    lookup_url_kwarg = 'id'  # URL parameter name

    def get_queryset(self):
        """Return all categories (including inactive) for admin, active only for others."""
        if self.action in ['list', 'retrieve']:
            return Category.objects.filter(is_active=True)
        return Category.objects.all()

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_object(self):
        """Override to support both UUID and integer ID lookups."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        
        # Try UUID first (normal Django behavior)
        try:
            from uuid import UUID
            uuid_obj = UUID(lookup_value)
            return Category.objects.get(id=uuid_obj)
        except (ValueError, TypeError, Category.DoesNotExist):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(lookup_value)
                # Find category whose UUID hash matches the integer ID
                import hashlib
                categories = Category.objects.all()
                for category in categories:
                    # Calculate hash the same way as serializer (using MD5 for deterministic results)
                    uuid_str = str(category.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        return category
                # If not found, raise DoesNotExist
                from django.http import Http404
                raise Http404(f'No Category matches the given query with ID: {lookup_value}')
            except (ValueError, TypeError):
                # Not a valid integer either
                from django.http import Http404
                raise Http404(f'Invalid ID format: {lookup_value}. Expected UUID or integer.')

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_retrieve',
        summary='Retrieve a category by ID',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Category ID (UUID or integer hash). Example: "9707d950-290b-4f14-94da-926b276eae68" or "1422176302"'
            )
        ],
        responses={
            200: CategoryCompatibilitySerializer,
            404: {'description': 'Category not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a category by ID. Returns format matching old Swagger."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_success_response(data=serializer.data)

    def list(self, request, *args, **kwargs):
        """List all categories. Returns format matching old Swagger."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_create',
        summary='Create a new category',
        request=CategoryCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create category',
                value={
                    'parentId': 1,
                    'name': 'string',
                    'description': 'string',
                    'shortDescription': 'string',
                    'type': 0,
                    'imagePath': 'string',
                    'thumbnail': 'string',
                    'masterId': None,
                    'sortOrder': 0,
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: {
                'description': 'Category created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': 19,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            },
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new category matching old Swagger format. Returns only the ID."""
        # Validate input using old Swagger format serializer
        input_serializer = CategoryCreateRequestSerializer(data=request.data)
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
            'name': validated_data.get('name'),
            'description': validated_data.get('description') or '',
        }
        
        # Handle imagePath - can be a file path, URL, or empty string
        image_path = validated_data.get('imagePath')
        if image_path and image_path.strip():
            # Use URLImageField to handle file paths, URLs, or local files
            try:
                image_field = URLImageField()
                category_data['image'] = image_field.to_internal_value(image_path)
            except Exception as e:
                # If image processing fails, continue without image
                pass
        
        # Create category using Django model serializer
        category_serializer = CategorySerializer(data=category_data, context={'request': request})
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
        
        # Convert UUID to integer hash (matching old Swagger format)
        import hashlib
        uuid_str = str(category.id)
        hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
        hash_int = int(hash_obj.hexdigest(), 16)
        category_id_hash = hash_int % 2147483647  # Max 32-bit integer
        
        # Return only the ID (integer hash) matching old Swagger format
        return create_success_response(data=category_id_hash, messages=[], status_code=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_update',
        summary='Update a category by ID',
        description='Updates an existing category by its ID. Accepts both UUID and integer ID formats.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Category ID (UUID or integer hash). Example: "9707d950-290b-4f14-94da-926b276eae68" or "961086872"'
            )
        ],
        request=CategoryCreateRequestSerializer,
        responses={
            200: CategoryCompatibilitySerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Category not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a category by ID. Accepts both UUID and integer ID formats."""
        instance = self.get_object()
        
        # Validate input using old Swagger format serializer
        input_serializer = CategoryCreateRequestSerializer(data=request.data)
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
        if 'name' in validated_data:
            instance.name = validated_data.get('name')
        if 'description' in validated_data:
            instance.description = validated_data.get('description') or ''
        if 'shortDescription' in validated_data:
            # shortDescription maps to description if provided
            instance.description = validated_data.get('shortDescription') or instance.description
        
        # Handle imagePath - can be a file path, URL, or empty string
        image_path = validated_data.get('imagePath') or validated_data.get('thumbnail')
        if image_path and image_path.strip():
            try:
                image_field = URLImageField()
                instance.image = image_field.to_internal_value(image_path)
            except Exception:
                # If image processing fails, continue without updating image
                pass
        
        # Handle type if provided
        if 'type' in validated_data and validated_data.get('type') is not None:
            instance.type = validated_data.get('type')
        
        # Handle locale if provided
        if 'locale' in validated_data:
            # Locale is not stored in Category model, but we accept it for compatibility
            pass
        
        instance.save()
        
        # Return with compatibility serializer (old Swagger format)
        compat_serializer = CategoryCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=compat_serializer.data)

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_partial_update',
        summary='Partially update a category by ID',
        description='Partially updates an existing category by its ID. Accepts both UUID and integer ID formats.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Category ID (UUID or integer hash). Example: "9707d950-290b-4f14-94da-926b276eae68" or "961086872"'
            )
        ],
        request=CategoryCreateRequestSerializer,
        responses={
            200: CategoryCompatibilitySerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Category not found'}
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a category by ID. Accepts both UUID and integer ID formats."""
        instance = self.get_object()
        
        # Validate input using old Swagger format serializer (partial=True allows partial updates)
        input_serializer = CategoryCreateRequestSerializer(data=request.data, partial=True)
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
        
        # Update only provided fields
        if 'name' in validated_data:
            instance.name = validated_data.get('name')
        if 'description' in validated_data:
            instance.description = validated_data.get('description') or ''
        if 'shortDescription' in validated_data:
            instance.description = validated_data.get('shortDescription') or instance.description
        
        # Handle imagePath - can be a file path, URL, or empty string
        image_path = validated_data.get('imagePath') or validated_data.get('thumbnail')
        if image_path is not None:  # Check if provided (even if empty)
            if image_path and image_path.strip():
                try:
                    image_field = URLImageField()
                    instance.image = image_field.to_internal_value(image_path)
                except Exception:
                    pass
            else:
                # Empty string means remove image
                instance.image = None
        
        # Handle type if provided
        if 'type' in validated_data and validated_data.get('type') is not None:
            instance.type = validated_data.get('type')
        
        instance.save()
        
        # Return with compatibility serializer (old Swagger format)
        compat_serializer = CategoryCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=compat_serializer.data)

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_destroy',
        summary='Delete a category by ID',
        description='Deletes a category by its ID. Accepts both UUID and integer ID formats.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Category ID (UUID or integer hash). Example: "9707d950-290b-4f14-94da-926b276eae68" or "961086872"'
            )
        ],
        responses={
            200: {
                'description': 'Category deleted successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            },
            404: {'description': 'Category not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a category by ID. Accepts both UUID and integer ID formats."""
        instance = self.get_object()
        # Soft delete by setting is_active to False
        instance.is_active = False
        instance.save()
        return create_success_response(data=None)

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_search',
        summary='Search Categories using available Filters',
        description='Search Categories using available Filters matching old Swagger format.',
        request=CategorySearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search categories',
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
                    'id': 0,
                    'type': 0
                }
            )
        ],
        responses={
            200: {
                'description': 'Paginated categories',
                'content': {
                    'application/json': {
                        'example': {
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
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search categories with pagination matching old Swagger format."""
        serializer = CategorySearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Get pagination parameters
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        # Default to 1 if 0 or not provided
        if page_number <= 0:
            page_number = 1
        if page_size <= 0:
            page_size = 1
        
        # Get keyword from top-level or advancedSearch
        keyword = (validated_data.get('keyword') or '').strip()
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and advanced_search.get('keyword'):
            keyword = (advanced_search.get('keyword') or '').strip()
        
        # Get filters
        category_id = validated_data.get('id')
        category_type = validated_data.get('type')
        
        # Get orderBy
        order_by = validated_data.get('orderBy', [])
        
        # Start with all categories
        qs = Category.objects.all()
        
        # Filter by ID if provided
        if category_id is not None:
            # Convert integer ID to UUID lookup (same logic as get_object)
            import hashlib
            categories = Category.objects.all()
            matching_category = None
            for cat in categories:
                uuid_str = str(cat.id)
                hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                hash_int = int(hash_obj.hexdigest(), 16)
                hash_id = hash_int % 2147483647
                if hash_id == category_id:
                    matching_category = cat
                    break
            if matching_category:
                qs = qs.filter(id=matching_category.id)
            else:
                # No matching category found, return empty result
                qs = qs.none()
        
        # Filter by type if provided
        if category_type is not None:
            qs = qs.filter(type=category_type)
        
        # Apply keyword search
        if keyword:
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        # Apply ordering
        if order_by:
            # Convert orderBy strings to Django order_by format
            order_fields = []
            for field in order_by:
                if field:
                    # Handle descending order (e.g., "-name")
                    if field.startswith('-'):
                        order_fields.append(field)
                    else:
                        order_fields.append(field)
            if order_fields:
                qs = qs.order_by(*order_fields)
        else:
            # Default ordering
            qs = qs.order_by('name')
        
        total = qs.count()
        
        # Calculate pagination
        start = (page_number - 1) * page_size
        end = start + page_size
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        items = qs[start:end]

        # Serialize categories
        category_serializer = self.get_serializer(items, many=True)
        
        # Build response matching old Swagger format
        response_data = {
            'data': category_serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total,
            'pageSize': page_size,
            'hasPreviousPage': page_number > 1,
            'hasNextPage': page_number < total_pages,
            'messages': None,  # Old Swagger uses null, not []
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        operation_id='categories_dapper',
        summary='Get categories (dapper context)',
        description='Get categories in dapper context. If id query parameter is provided, returns single category.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Category ID (UUID or integer hash). If provided, returns single category. Example: "9707d950-290b-4f14-94da-926b276eae68" or "6"'
            )
        ],
        responses={
            200: CategoryCompatibilitySerializer,
            404: {'description': 'Category not found'}
        }
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get categories in dapper context. If id is provided, returns single category."""
        category_id = request.query_params.get('id')
        
        if category_id:
            # Return single category matching the ID
            try:
                # Use the same lookup logic as retrieve
                lookup_value = category_id
                
                # Try UUID first
                try:
                    from uuid import UUID
                    uuid_obj = UUID(lookup_value)
                    # Try active first, then all categories
                    try:
                        category = Category.objects.get(id=uuid_obj, is_active=True)
                    except Category.DoesNotExist:
                        category = Category.objects.get(id=uuid_obj)
                except (ValueError, TypeError, Category.DoesNotExist):
                    # If not a valid UUID, try as integer ID
                    try:
                        integer_id = int(lookup_value)
                        # Find category whose UUID hash matches the integer ID
                        # Search all categories (including inactive) since old system might have different status
                        import hashlib
                        categories = Category.objects.all()
                        category = None
                        for cat in categories:
                            uuid_str = str(cat.id)
                            # Use MD5 hash for deterministic results (same as serializer)
                            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                            hash_int = int(hash_obj.hexdigest(), 16)
                            hash_id = hash_int % 2147483647
                            if hash_id == integer_id:
                                category = cat
                                break
                        if not category:
                            from django.http import Http404
                            raise Http404(f'No Category matches the given query with ID: {lookup_value}')
                    except (ValueError, TypeError):
                        from django.http import Http404
                        raise Http404(f'Invalid ID format: {lookup_value}. Expected UUID or integer.')
                
                serializer = self.get_serializer(category)
                return create_success_response(data=serializer.data)
            except Category.DoesNotExist:
                from django.http import Http404
                raise Http404(f'No Category matches the given query with ID: {category_id}')
        else:
            # Return all categories
            categories = Category.objects.filter(is_active=True).order_by('name')
            serializer = self.get_serializer(categories, many=True)
            return create_success_response(data=serializer.data)


# ============================================================================
# SEPARATE APIView CLASSES FOR CUSTOM ENDPOINTS WITH PATH PARAMETERS
# These need custom URL patterns because they don't fit router pattern
# ============================================================================

@extend_schema(
    tags=['Categories'],
    operation_id='categories_by_type_nolocal',
    summary='Get categories by type (no localization)',
    description='Retrieves categories by a specified type, excluding localizations.',
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category type (0-32)'
        )
    ],
    responses={
        200: {
            'description': 'List of categories by type',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 6,
                                'parentId': 0,
                                'parName': None,
                                'name': 'string',
                                'shortDescription': None,
                                'type': 1,
                                'thumbnail': 'string',
                                'masterId': None,
                                'masterName': None,
                                'sortOrder': None,
                                'locale': 'en'
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesByTypeNoLocalView(APIView):
    """GET /api/v1/categories/by-type-nolocal/{type} - Get categories by type (no local)"""
    permission_classes = [AllowAny]
    
    def get(self, request, type):
        """Get categories by type matching old Swagger format."""
        try:
            type_int = int(type)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid type parameter: {type}. Expected integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'type': [f'Invalid type: {type}. Expected integer.']}
            )
        
        # Filter categories by type
        categories = Category.objects.filter(type=type_int, is_active=True).order_by('name')
        serializer = CategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Categories'],
    operation_id='categories_by_type',
    summary='Get categories by type',
    description='Retrieves categories by a specified type.',
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category type (0-32)'
        )
    ],
    responses={
        200: {
            'description': 'List of categories by type',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 11,
                                'parentId': 0,
                                'parName': None,
                                'name': 'string',
                                'shortDescription': None,
                                'type': 2,
                                'thumbnail': 'string',
                                'masterId': None,
                                'masterName': None,
                                'sortOrder': None,
                                'locale': 'en'
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesByTypeView(APIView):
    """GET /api/v1/categories/by-type/{type} - Get categories by type"""
    permission_classes = [AllowAny]
    
    def get(self, request, type):
        """Get categories by type matching old Swagger format."""
        try:
            type_int = int(type)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid type parameter: {type}. Expected integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'type': [f'Invalid type: {type}. Expected integer.']}
            )
        
        # Filter categories by type
        categories = Category.objects.filter(type=type_int, is_active=True).order_by('name')
        serializer = CategoryCompatibilitySerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Categories'],
    operation_id='categories_client_by_type',
    summary='Get client categories by type',
    description='Retrieves client-specific categories by a specified type.',
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category type (0-32)'
        )
    ],
    responses={
        200: {
            'description': 'List of categories by type',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 9,
                                'parentId': 0,
                                'name': 'string',
                                'imagePath': None,
                                'thumbnail': None,
                                'count': None,
                                'lastModifiedOn': '0001-01-01T00:00:00',
                                'children': []
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesClientByTypeView(APIView):
    """GET /api/v1/categories/client/by-type/{type} - Get client categories by type"""
    permission_classes = [AllowAny]
    
    def get(self, request, type):
        """Get client categories by type matching old Swagger format."""
        try:
            type_int = int(type)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid type parameter: {type}. Expected integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'type': [f'Invalid type: {type}. Expected integer.']}
            )
        
        # Filter categories by type
        categories = Category.objects.filter(type=type_int, is_active=True).order_by('name')
        serializer = CategoryClientSerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Categories'],
    operation_id='categories_client_by_type_sort',
    summary='Get client categories by type (sorted)',
    description='Retrieves client-specific categories by a specified type, sorted.',
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category type (0-32)'
        )
    ],
    responses={
        200: {
            'description': 'List of categories by type (sorted)',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 8,
                                'parentId': 0,
                                'name': 'نحوه ارسال',
                                'imagePath': '',
                                'thumbnail': None,
                                'count': None,
                                'lastModifiedOn': '0001-01-01T00:00:00',
                                'children': []
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesClientByTypeSortView(APIView):
    """GET /api/v1/categories/client/by-type-sort/{type} - Get client categories by type (sorted)"""
    permission_classes = [AllowAny]
    
    def get(self, request, type):
        """Get client categories by type (sorted) matching old Swagger format."""
        try:
            type_int = int(type)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid type parameter: {type}. Expected integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'type': [f'Invalid type: {type}. Expected integer.']}
            )
        
        # Filter categories by type and sort by name
        categories = Category.objects.filter(type=type_int, is_active=True).order_by('name')
        serializer = CategoryClientSerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Categories'],
    operation_id='categories_client_by_type_sort_desc',
    summary='Get client categories by type (sorted descending)',
    description='Retrieves client-specific categories by a specified type, sorted in descending order.',
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category type (0-32)'
        )
    ],
    responses={
        200: {
            'description': 'List of categories by type (sorted descending)',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 8,
                                'parentId': 0,
                                'name': 'string',
                                'imagePath': '',
                                'thumbnail': None,
                                'count': None,
                                'shortDescription': None,
                                'lastModifiedOn': '0001-01-01T00:00:00',
                                'children': []
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesClientByTypeSortDescView(APIView):
    """GET /api/v1/categories/client/by-type-sort-desc/{type} - Get client categories by type (sorted desc)"""
    permission_classes = [AllowAny]
    
    def get(self, request, type):
        """Get client categories by type (sorted descending) matching old Swagger format."""
        try:
            type_int = int(type)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid type parameter: {type}. Expected integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'type': [f'Invalid type: {type}. Expected integer.']}
            )
        
        # Filter categories by type and sort by name descending
        categories = Category.objects.filter(type=type_int, is_active=True).order_by('-name')
        serializer = CategoryClientSerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Categories'],
    operation_id='categories_client_parents',
    summary='Get parent categories for client',
    description='Retrieves parent categories for a given ID in a client context.',
    parameters=[
        OpenApiParameter(
            name='Id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category ID (UUID or integer hash). Example: "9707d950-290b-4f14-94da-926b276eae68" or "1"'
        )
    ],
    responses={
        200: {
            'description': 'List of parent categories',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 1,
                                'parentId': 0,
                                'parName': None,
                                'name': 'زباله تر',
                                'description': '',
                                'shortDescription': None,
                                'type': 1,
                                'imagePath': '/uploads/app/3f799048734c4fadaf293eb61b1793bf.webp',
                                'thumbnail': '/uploads/app/3f799048734c4fadaf293eb61b1793bf.webp',
                                'masterId': None,
                                'masterName': None,
                                'sortOrder': None,
                                'locale': 'en'
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesClientParentsView(APIView):
    """GET /api/v1/categories/client/parents/{Id} - Get parent categories for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, Id):
        """Get parent categories for a given category ID matching old Swagger format."""
        # Note: Category model doesn't have a parent field yet
        # For now, return the category itself if it exists (as parent)
        # TODO: Add parent field to Category model if hierarchical categories are needed
        
        # Try UUID first
        try:
            from uuid import UUID
            uuid_obj = UUID(Id)
            try:
                category = Category.objects.get(id=uuid_obj, is_active=True)
            except Category.DoesNotExist:
                # Try all categories (including inactive)
                try:
                    category = Category.objects.get(id=uuid_obj)
                except Category.DoesNotExist:
                    return create_success_response(data=[])
        except (ValueError, TypeError):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(Id)
                # Find category whose UUID hash matches the integer ID
                import hashlib
                categories = Category.objects.all()
                category = None
                for cat in categories:
                    uuid_str = str(cat.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        category = cat
                        break
                if not category:
                    return create_success_response(data=[])
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid ID format: {Id}. Expected UUID or integer.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'Id': [f'Invalid ID format: {Id}. Expected UUID or integer.']}
                )
        
        # Return category using compatibility serializer
        serializer = CategoryCompatibilitySerializer(category, context={'request': request})
        return create_success_response(data=[serializer.data])


@extend_schema(
    tags=['Categories'],
    operation_id='categories_client_by_type_count',
    summary='Get client categories by type with product count',
    description='Retrieves client-specific categories by a specified type with product count.',
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category type (0-32)'
        )
    ],
    responses={
        200: {
            'description': 'List of categories by type with product count',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 8,
                                'parentId': 0,
                                'name': 'string',
                                'imagePath': '',
                                'thumbnail': None,
                                'count': 2,
                                'children': []
                            }
                        ]
                    }
                }
            }
        }
    }
)
class CategoriesClientByTypeCountView(APIView):
    """GET /api/v1/categories/client/by-type-count/{type} - Get client categories by type with count"""
    permission_classes = [AllowAny]
    
    def get(self, request, type):
        """Get client categories by type with product count matching old Swagger format."""
        try:
            type_int = int(type)
        except (ValueError, TypeError):
            return create_error_response(
                error_message=f'Invalid type parameter: {type}. Expected integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'type': [f'Invalid type: {type}. Expected integer.']}
            )
        
        # Filter categories by type and annotate with product count
        categories = Category.objects.filter(
            type=type_int, 
            is_active=True
        ).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('name')
        
        # Set product count on each category object for the serializer
        for category in categories:
            category._product_count = category.product_count
        
        serializer = CategoryClientSerializer(categories, many=True, context={'request': request})
        return create_success_response(data=serializer.data)

