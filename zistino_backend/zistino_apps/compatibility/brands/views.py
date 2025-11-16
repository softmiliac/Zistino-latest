"""
Compatibility views for Brands endpoints.
All endpoints will appear under "Brands" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Brands
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager
import uuid
import random
import time

from zistino_apps.products.models import Brand, Product
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    BrandSerializer,
    BrandCompatibilitySerializer,
    BrandDetailCompatibilitySerializer,
    BrandCreateRequestSerializer,
    BrandSearchRequestSerializer,
    BrandGenerateRandomRequestSerializer
)


@extend_schema(tags=['Brands'])
class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing brands.
    All endpoints will appear under "Brands" folder in Swagger UI.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'searchwithdescription', 'generate_random', 'delete_random']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_create',
        summary='Creates a new brand',
        description='Creates a new brand matching old Swagger format.',
        request=BrandCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create brand',
                value={
                    'name': 'string',
                    'description': 'string',
                    'imageUrl': 'string',
                    'thumbnail': 'string',
                    'locale': 'string',
                    'masterId': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Brand created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': '94860000-b419-c60d-0a25-08de1f794aa0',
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
        """Create a new brand matching old Swagger format. Returns brand UUID as string."""
        # Validate input using old Swagger format serializer
        input_serializer = BrandCreateRequestSerializer(data=request.data)
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
        
        # Validate masterId (product ID) if provided
        master_id = validated_data.get('masterId')
        if master_id and master_id.strip():
            try:
                product_uuid = uuid.UUID(master_id)
                # Verify product exists (optional validation)
                try:
                    Product.objects.get(id=product_uuid, is_active=True)
                except Product.DoesNotExist:
                    # Product doesn't exist, but we'll still create the brand (old Swagger behavior)
                    pass
            except ValueError:
                # Invalid UUID format, but we'll still create the brand (old Swagger behavior)
                pass
        
        # Use thumbnail if provided, otherwise use imageUrl
        image_url = validated_data.get('thumbnail') or validated_data.get('imageUrl') or ''
        
        # Create brand
        brand = Brand.objects.create(
            name=validated_data.get('name'),
            description=validated_data.get('description') or '',
            image_url=image_url,
            locale=validated_data.get('locale') or 'fa'
        )
        
        # Return brand UUID as string wrapped in standard response
        return create_success_response(data=str(brand.id))  # 200 OK to match old Swagger

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_list',
        summary='List all brands',
        description='List all brands matching old Swagger format (same as /all endpoint).',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all brands',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': '94860000-b419-c60d-9da1-08dc425079d8',
                                    'name': 'recycle',
                                    'thumbnail': None,
                                    'locale': None,
                                    'masterId': None
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
    def list(self, request, *args, **kwargs):
        """List all brands matching old Swagger format (same as /all endpoint)."""
        brands = Brand.objects.filter(is_active=True).order_by('name')
        serializer = BrandCompatibilitySerializer(brands, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_search',
        summary='Search Brands using available Filters',
        description='Search Brands using available Filters matching old Swagger format.',
        request=BrandSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search brands',
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
        """Search brands with pagination matching old Swagger format."""
        serializer = BrandSearchRequestSerializer(data=request.data)
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

        qs = Brand.objects.filter(is_active=True)

        # Apply keyword search on name field
        if keyword and keyword.strip():
            qs = qs.filter(name__icontains=keyword.strip())

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

        brand_serializer = self.get_serializer(items, many=True)
        items_data = brand_serializer.data
        
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
        tags=['Brands'],
        operation_id='brands_searchwithdescription',
        summary='Search Brands using available Filters',
        description='Search Brands using available Filters (with description) matching old Swagger format.',
        request=BrandSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search brands with description',
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
    @action(detail=False, methods=['post'], url_path='searchwithdescription', permission_classes=[IsAuthenticated, IsManager])
    def searchwithdescription(self, request):
        """Search brands with description field included in search matching old Swagger format."""
        serializer = BrandSearchRequestSerializer(data=request.data)
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

        qs = Brand.objects.filter(is_active=True)

        # Apply keyword search on name and description fields
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(name__icontains=keyword.strip()) |
                Q(description__icontains=keyword.strip())
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

        brand_serializer = self.get_serializer(items, many=True)
        items_data = brand_serializer.data
        
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
        tags=['Brands'],
        operation_id='brands_dapper',
        summary='Get brands (dapper context)',
        description='Get brands in dapper context. If id query parameter is provided, returns single brand.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Brand ID (UUID). If provided, returns single brand.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Brand(s) data',
                examples=[
                    OpenApiExample(
                        'Success response (single brand)',
                        value={
                            'data': {
                                'id': '94860000-b419-c60d-9da1-08dc425079d8',
                                'name': 'recycle',
                                'description': None,
                                'imageUrl': None,
                                'thumbnail': None,
                                'locale': None
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    ),
                    OpenApiExample(
                        'Success response (all brands)',
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
        """Get brands in dapper context matching old Swagger format."""
        brand_id = request.query_params.get('id')
        
        if brand_id:
            # Return single brand by ID
            try:
                brand = Brand.objects.get(id=brand_id, is_active=True)
                serializer = BrandDetailCompatibilitySerializer(brand)
                return create_success_response(data=serializer.data)
            except (Brand.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Brand with ID "{brand_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all brands
            brands = Brand.objects.filter(is_active=True).order_by('name')
            serializer = BrandCompatibilitySerializer(brands, many=True)
            return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_all',
        summary='Retrieves all brands',
        description='Retrieves all brands matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all brands',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': '94860000-b419-c60d-9da1-08dc425079d8',
                                    'name': 'recycle',
                                    'thumbnail': None,
                                    'locale': None,
                                    'masterId': None
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
        """Get all brands matching old Swagger format."""
        brands = Brand.objects.filter(is_active=True).order_by('name')
        serializer = BrandCompatibilitySerializer(brands, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_client_all',
        summary='Get All Brands',
        description='Get All Brands (for client-side use) matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all brands for client',
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
    @action(detail=False, methods=['get'], url_path='client/all')
    def client_all(self, request):
        """Get all brands for client matching old Swagger format."""
        brands = Brand.objects.filter(is_active=True).order_by('name')
        serializer = BrandCompatibilitySerializer(brands, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_client_description_all',
        summary='Get All Brands',
        description='Get All Brands (for client-side use, with descriptions) matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all brands with descriptions for client',
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
    @action(detail=False, methods=['get'], url_path='client/description/all')
    def client_description_all(self, request):
        """Get all brands with descriptions for client matching old Swagger format."""
        brands = Brand.objects.filter(is_active=True).order_by('name')
        serializer = BrandCompatibilitySerializer(brands, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_generate_random',
        summary='Generate random brands',
        description='Generates random brand entries (admin only). Brands are marked with "Random Brand" prefix for easy deletion.',
        request=BrandGenerateRandomRequestSerializer,
        examples=[
            OpenApiExample(
                'Generate random brands',
                value={
                    'nSeed': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Random brands generated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'message': 'Random brands generated successfully',
                                'count': 10
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
    @action(detail=False, methods=['post'], url_path='generate-random', permission_classes=[IsAuthenticated, IsManager])
    def generate_random(self, request):
        """Generate random brands matching old Swagger format."""
        # Validate input
        serializer = BrandGenerateRandomRequestSerializer(data=request.data)
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
        n_seed = validated_data.get('nSeed', 0)
        
        # Seed random number generator if nSeed is provided
        if n_seed:
            random.seed(n_seed)
        
        # Default count (can be adjusted based on nSeed or use a fixed number)
        # For now, we'll generate a reasonable number of brands
        # If nSeed is 0, generate 10 brands; otherwise use nSeed as count (with limits)
        if n_seed == 0:
            count = 10
        else:
            count = min(max(abs(n_seed), 1), 100)  # Limit between 1 and 100
        
        # Random brand name prefixes and suffixes
        prefixes = ['Premium', 'Elite', 'Pro', 'Ultra', 'Super', 'Max', 'Prime', 'Gold', 'Silver', 'Platinum']
        suffixes = ['Brand', 'Corp', 'Inc', 'Ltd', 'Group', 'Industries', 'Solutions', 'Systems', 'Tech', 'Global']
        adjectives = ['Fast', 'Smart', 'Power', 'Eco', 'Green', 'Clean', 'Pure', 'Fresh', 'New', 'Modern']
        
        locales = ['fa', 'en', 'ar', 'tr']
        descriptions = [
            'High quality brand for modern consumers',
            'Premium products with excellent quality',
            'Eco-friendly brand committed to sustainability',
            'Innovative solutions for everyday needs',
            'Trusted brand with years of experience',
            'Cutting-edge technology and design',
            'Affordable quality for everyone',
            'Luxury brand with exceptional standards',
            'Reliable products you can trust',
            'Leading brand in the industry'
        ]
        
        created_brands = []
        timestamp = int(time.time() * 1000)  # Use timestamp to ensure unique names
        
        for i in range(count):
            # Generate random name with "Random Brand" prefix for easy identification
            # Add timestamp to ensure uniqueness and avoid constraint violations
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            adjective = random.choice(adjectives)
            name = f"Random Brand {adjective} {prefix} {suffix} {timestamp}_{i+1}"
            
            # Check if name already exists, if so, add more uniqueness
            while Brand.objects.filter(name=name, is_active=True).exists():
                timestamp += 1
                name = f"Random Brand {adjective} {prefix} {suffix} {timestamp}_{i+1}"
            
            # Generate random description
            description = random.choice(descriptions)
            
            # Random locale
            locale = random.choice(locales)
            
            # Random image URL (optional, sometimes None)
            image_url = None
            if random.choice([True, False]):
                image_url = f"https://example.com/brands/brand_{timestamp}_{i+1}.jpg"
            
            # Create brand
            try:
                brand = Brand.objects.create(
                    name=name,
                    description=description,
                    image_url=image_url,
                    locale=locale,
                    is_active=True
                )
                created_brands.append(brand)
            except Exception as e:
                # If there's still a constraint violation, skip this one and continue
                continue
        
        return create_success_response(data={
            'message': 'Random brands generated successfully',
            'count': len(created_brands)
        })

    @extend_schema(
        tags=['Brands'],
        operation_id='brands_delete_random',
        summary='Delete random brands',
        description='Deletes randomly generated brand entries (admin only). Deletes all brands with "Random Brand" prefix.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Random brands deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'message': 'Random brands deleted successfully',
                                'count': 10
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['delete'], url_path='delete-random', permission_classes=[IsAuthenticated, IsManager])
    def delete_random(self, request):
        """Delete random brands matching old Swagger format."""
        # Find all brands with "Random Brand" prefix
        random_brands = Brand.objects.filter(name__startswith='Random Brand', is_active=True)
        count = random_brands.count()
        
        # Soft delete by setting is_active to False
        random_brands.update(is_active=False)
        
        return create_success_response(data={
            'message': 'Random brands deleted successfully',
            'count': count
        })
    
    @extend_schema(
        tags=['Brands'],
        operation_id='brands_retrieve',
        summary='Retrieves a brand by its ID',
        description='Retrieves a brand by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='Brand ID (UUID)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Brand details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': '94860000-b419-c60d-9da1-08dc425079d8',
                                'name': 'recycle',
                                'description': None,
                                'imageUrl': None,
                                'thumbnail': None,
                                'locale': None
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Brand not found'}
        }
    )
    def retrieve(self, request, pk=None):
        """Get brand by ID matching old Swagger format."""
        try:
            brand = Brand.objects.get(id=pk, is_active=True)
            serializer = BrandDetailCompatibilitySerializer(brand)
            return create_success_response(data=serializer.data)
        except Brand.DoesNotExist:
            return create_error_response(
                error_message=f'Brand with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['Brands'],
        operation_id='brands_update',
        summary='Updates an existing brand by its ID',
        description='Updates an existing brand by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='Brand ID (UUID)'
            )
        ],
        request=BrandCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update brand',
                value={
                    'name': 'string',
                    'description': 'string',
                    'imageUrl': 'string',
                    'thumbnail': 'string',
                    'locale': 'string',
                    'masterId': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Brand updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': '94860000-b419-c60d-9da1-08dc425079d8',
                                'name': 'recycle',
                                'description': None,
                                'imageUrl': None,
                                'thumbnail': None,
                                'locale': None
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Brand not found'}
        }
    )
    def update(self, request, pk=None):
        """Update brand matching old Swagger format."""
        try:
            brand = Brand.objects.get(id=pk, is_active=True)
        except Brand.DoesNotExist:
            return create_error_response(
                error_message=f'Brand with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = BrandCreateRequestSerializer(data=request.data)
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
        
        # Update brand fields
        if 'name' in validated_data:
            brand.name = validated_data.get('name')
        if 'description' in validated_data:
            brand.description = validated_data.get('description') or ''
        # Use thumbnail if provided, otherwise use imageUrl
        image_url = validated_data.get('thumbnail') or validated_data.get('imageUrl') or ''
        if 'thumbnail' in validated_data or 'imageUrl' in validated_data:
            brand.image_url = image_url
        if 'locale' in validated_data:
            brand.locale = validated_data.get('locale') or 'fa'
        
        brand.save()
        
        # Return updated brand in detail compatibility format
        serializer = BrandDetailCompatibilitySerializer(brand)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Brands'],
        operation_id='brands_delete',
        summary='Deletes a brand by its ID',
        description='Deletes a brand by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='Brand ID (UUID)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Brand deleted successfully',
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
            404: {'description': 'Brand not found'}
        }
    )
    def destroy(self, request, pk=None):
        """Delete brand matching old Swagger format."""
        try:
            brand = Brand.objects.get(id=pk, is_active=True)
            # Soft delete by setting is_active to False
            brand.is_active = False
            brand.save()
            return create_success_response(data=None)
        except Brand.DoesNotExist:
            return create_error_response(
                error_message=f'Brand with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

