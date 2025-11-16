"""
Views for ProductSections compatibility layer.
Provides all 10 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from django.db.models import Q

from zistino_apps.products.models import ProductSection, Product
from zistino_apps.products.serializers import ProductSectionSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from .serializers import (
    ProductSectionGroupSerializer,
    ProductSectionCreateRequestSerializer,
    ProductSectionSearchRequestSerializer,
    ProductSectionCompatibilitySerializer,
    ProductSectionGroupUpdateSerializer,
)


@extend_schema(tags=['ProductSections'])
class ProductSectionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductSections endpoints.
    Wraps the existing ProductSectionViewSet functionality and adds compatibility endpoints.
    """
    queryset = ProductSection.objects.all()
    serializer_class = ProductSectionSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'group']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_list',
        summary='List all product sections',
    )
    def list(self, request, *args, **kwargs):
        """List all product sections."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_retrieve',
        summary='Retrieve a product section by ID',
        responses={
            200: {
                'description': 'Product section details',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 4,
                                'parentId': None,
                                'startDate': None,
                                'endDate': None,
                                'type': None,
                                'name': 'string',
                                'groupName': 'string',
                                'page': 'home',
                                'version': 0,
                                'product': None,
                                'imagePath': '/uploads/app/image.webp',
                                'thumbnail': None,
                                'setting': '{"type": 5}',
                                'description': '',
                                'linkUrl': '/#',
                                'orderId': 0,
                                'locale': 'en'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a product section by ID matching old Swagger format."""
        instance = self.get_object()
        serializer = ProductSectionCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_create',
        summary='Create a new product section',
        request=ProductSectionCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create product section',
                value={
                    'parentId': 0,
                    'startDate': '2025-11-11T10:53:41.396Z',
                    'endDate': '2025-11-11T10:53:41.396Z',
                    'type': 0,
                    'name': 'string',
                    'groupName': 'string',
                    'page': 'string',
                    'version': 0,
                    'productId': 'string',
                    'imagePath': 'string',
                    'thumbnail': 'string',
                    'setting': 'string',
                    'description': 'string',
                    'linkUrl': 'string',
                    'orderId': 0,
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: {
                'description': 'Product section created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': 14,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new product section matching old Swagger format."""
        serializer = ProductSectionCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Validate name is required for create
        if not validated_data.get('name'):
            return create_error_response(
                error_message='name field is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'name': ['This field is required.']}
            )
        
        # Map old Swagger fields to Django model fields
        product_id = validated_data.get('productId')
        product = None
        if product_id and product_id.strip():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return create_error_response(
                    error_message=f'Product with ID "{product_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'productId': [f'Product with ID "{product_id}" not found.']}
                )
        
        # Create ProductSection
        product_section = ProductSection.objects.create(
            name=validated_data.get('name'),
            page=validated_data.get('page', 'home') or 'home',
            group_name=validated_data.get('groupName', '') or '',
            version=validated_data.get('version', 0) or 0,
            product=product,
            image_path=validated_data.get('imagePath', '') or '',
            setting_type=validated_data.get('type', 0) or 0,
            expire_date=validated_data.get('endDate') or validated_data.get('startDate'),  # Use endDate or startDate
            description=validated_data.get('description', '') or '',
            link_url=validated_data.get('linkUrl', '') or '',
            locale=validated_data.get('locale', 'en') or 'en',
            is_active=True
        )
        
        return create_success_response(data=product_section.id)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_update',
        summary='Update a product section',
        request=ProductSectionCreateRequestSerializer,
        responses={
            200: {
                'description': 'Product section updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 4,
                                'parentId': None,
                                'startDate': None,
                                'endDate': None,
                                'type': None,
                                'name': 'string',
                                'groupName': 'string',
                                'page': 'home',
                                'version': 0,
                                'product': None,
                                'imagePath': '/uploads/app/image.webp',
                                'thumbnail': None,
                                'setting': '{"type": 5}',
                                'description': '',
                                'linkUrl': '/#',
                                'orderId': 0,
                                'locale': 'en'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a product section matching old Swagger format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ProductSectionCreateRequestSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Map old Swagger fields to Django model fields
        product_id = validated_data.get('productId')
        if product_id and product_id.strip():
            try:
                product = Product.objects.get(id=product_id)
                instance.product = product
            except Product.DoesNotExist:
                return create_error_response(
                    error_message=f'Product with ID "{product_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'productId': [f'Product with ID "{product_id}" not found.']}
                )
        elif 'productId' in validated_data and not product_id:
            # Explicitly set to None if productId is provided as empty/null
            instance.product = None
        
        # Update ProductSection fields (only if provided in partial update)
        if 'name' in validated_data:
            instance.name = validated_data.get('name')
        if 'page' in validated_data:
            instance.page = validated_data.get('page')
        if 'groupName' in validated_data:
            instance.group_name = validated_data.get('groupName', '')
        if 'version' in validated_data:
            instance.version = validated_data.get('version')
        if 'imagePath' in validated_data:
            instance.image_path = validated_data.get('imagePath', '')
        if 'type' in validated_data:
            instance.setting_type = validated_data.get('type', 0)
        if 'endDate' in validated_data or 'startDate' in validated_data:
            instance.expire_date = validated_data.get('endDate') or validated_data.get('startDate')
        if 'description' in validated_data:
            instance.description = validated_data.get('description', '')
        if 'linkUrl' in validated_data:
            instance.link_url = validated_data.get('linkUrl', '')
        if 'locale' in validated_data:
            instance.locale = validated_data.get('locale', 'en')
        
        instance.save()
        
        response_serializer = ProductSectionCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=response_serializer.data)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_partial_update',
        summary='Partially update a product section',
        request=ProductSectionCreateRequestSerializer,
        responses={
            200: {
                'description': 'Product section updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 4,
                                'parentId': None,
                                'startDate': None,
                                'endDate': None,
                                'type': None,
                                'name': 'string',
                                'groupName': 'string',
                                'page': 'home',
                                'version': 0,
                                'product': None,
                                'imagePath': '/uploads/app/image.webp',
                                'thumbnail': None,
                                'setting': '{"type": 5}',
                                'description': '',
                                'linkUrl': '/#',
                                'orderId': 0,
                                'locale': 'en'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a product section matching old Swagger format."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_destroy',
        summary='Delete a product section',
        responses={
            200: {
                'description': 'Product section deleted successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a product section matching old Swagger format."""
        instance = self.get_object()
        instance.delete()
        return create_success_response(data=None)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_search',
        summary='Search product sections using available filters',
        request=ProductSectionSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search product sections',
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
                    'parentId': 0,
                    'startDate': '2025-11-11T10:54:50.297Z',
                    'endDate': '2025-11-11T10:54:50.297Z',
                    'type': 0
                }
            )
        ],
        responses={
            200: {
                'description': 'Product sections search results',
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
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search product sections with pagination and filters matching old Swagger format."""
        # Handle empty request body - all fields are optional
        request_data = request.data if request.data else {}
        serializer = ProductSectionSearchRequestSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Get keyword from advancedSearch or top-level
        keyword = validated_data.get('keyword', '').strip()
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and isinstance(advanced_search, dict):
            advanced_keyword = advanced_search.get('keyword') or ''
            keyword = advanced_keyword or keyword
        
        # Get filters
        section_type = validated_data.get('type', 0)
        start_date = validated_data.get('startDate')
        end_date = validated_data.get('endDate')
        
        # Get pagination (0 defaults to 1)
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        if page_number == 0:
            page_number = 1
        if page_size == 0:
            page_size = 1
        
        # Build query
        qs = ProductSection.objects.all()
        
        # Apply keyword filter
        if keyword:
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(page__icontains=keyword) |
                Q(group_name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        # Apply type filter (setting_type)
        if section_type is not None and section_type != 0:
            qs = qs.filter(setting_type=section_type)
        
        # Apply date filters
        if start_date:
            qs = qs.filter(expire_date__gte=start_date)
        if end_date:
            qs = qs.filter(expire_date__lte=end_date)
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and len(order_by) > 0:
            # Filter out empty strings
            order_by = [field for field in order_by if field and field.strip()]
            if order_by:
                # Try to apply ordering (default to -id if invalid)
                try:
                    qs = qs.order_by(*order_by)
                except:
                    qs = qs.order_by('-id')
            else:
                qs = qs.order_by('-id')
        else:
            qs = qs.order_by('-id')
        
        # Get total count before pagination
        total_count = qs.count()
        
        # Apply pagination
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        # Serialize items
        serialized_items = ProductSectionCompatibilitySerializer(items, many=True, context={'request': request}).data
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
        has_previous_page = page_number > 1
        has_next_page = page_number < total_pages if total_pages > 0 else False
        
        # Return format matching old Swagger
        return Response({
            'data': serialized_items,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous_page,
            'hasNextPage': has_next_page,
            'messages': None,
            'succeeded': True
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['ProductSections'],
        operation_id='productsections_group',
        summary='Update a group of product sections',
        request=ProductSectionGroupUpdateSerializer(many=True),
        examples=[
            OpenApiExample(
                'Update product sections group',
                value=[{
                    'id': 0,
                    'name': 'string',
                    'parentId': 0,
                    'startDate': '2025-11-11T11:01:56.420Z',
                    'endDate': '2025-11-11T11:01:56.420Z',
                    'type': 0,
                    'groupName': 'string',
                    'page': 'string',
                    'version': 0,
                    'productId': 'string',
                    'imagePath': 'string',
                    'thumbnail': 'string',
                    'setting': 'string',
                    'description': 'string',
                    'linkUrl': 'string',
                    'orderId': 0,
                    'locale': 'string'
                }]
            )
        ],
        responses={
            200: {
                'description': 'Product sections updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['put'], url_path='group')
    def group(self, request):
        """Update a group of product sections matching old Swagger format."""
        serializer = ProductSectionGroupUpdateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        updated_count = 0
        for item_data in serializer.validated_data:
            section_id = item_data.get('id', 0)
            if section_id and section_id > 0:
                try:
                    section = ProductSection.objects.get(id=section_id)
                except ProductSection.DoesNotExist:
                    continue
            else:
                # Create new section if id is 0 or not provided
                section = ProductSection()
            
            # Map old Swagger fields to Django model fields
            product_id = item_data.get('productId')
            product = None
            if product_id and product_id.strip():
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    continue
            
            # Update section
            section.name = item_data.get('name', section.name if hasattr(section, 'name') else '')
            section.page = item_data.get('page', section.page if hasattr(section, 'page') else 'home')
            section.group_name = item_data.get('groupName', section.group_name if hasattr(section, 'group_name') else '')
            section.version = item_data.get('version', section.version if hasattr(section, 'version') else 0)
            section.product = product if product else (section.product if hasattr(section, 'product') else None)
            section.image_path = item_data.get('imagePath', section.image_path if hasattr(section, 'image_path') else '')
            section.setting_type = item_data.get('type', section.setting_type if hasattr(section, 'setting_type') else 0)
            section.expire_date = item_data.get('endDate') or item_data.get('startDate') or (section.expire_date if hasattr(section, 'expire_date') else None)
            section.description = item_data.get('description', section.description if hasattr(section, 'description') else '')
            section.link_url = item_data.get('linkUrl', section.link_url if hasattr(section, 'link_url') else '')
            section.locale = item_data.get('locale', section.locale if hasattr(section, 'locale') else 'en')
            section.is_active = True
            section.save()
            updated_count += 1
        
        return create_success_response(data=None)


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['ProductSections'],
    parameters=[
        OpenApiParameter('id', int, location=OpenApiParameter.QUERY, description='Optional section ID', required=False),
    ],
)
class ProductSectionsDapperView(APIView):
    """GET /api/v1/productsections/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get product sections in dapper context. Accepts optional id parameter."""
        section_id = request.query_params.get('id')
        
        if section_id:
            try:
                section = ProductSection.objects.get(id=section_id, is_active=True)
                serializer = ProductSectionCompatibilitySerializer(section, context={'request': request})
                return create_success_response(data=serializer.data)
            except ProductSection.DoesNotExist:
                return create_success_response(data=None)
        
        return create_success_response(data=None)


@extend_schema(
    tags=['ProductSections'],
    responses={
        200: {
            'description': 'List of all product sections',
            'content': {
                'application/json': {
                    'example': {
                        'data': [{
                            'id': 4,
                            'parentId': None,
                            'startDate': None,
                            'endDate': None,
                            'type': None,
                            'name': 'string',
                            'groupName': 'string',
                            'page': 'home',
                            'version': 0,
                            'product': None,
                            'imagePath': '/uploads/app/image.webp',
                            'thumbnail': None,
                            'setting': '{"type": 5}',
                            'description': '',
                            'linkUrl': '/#',
                            'orderId': 0,
                            'locale': 'en'
                        }],
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class ProductSectionsAllView(APIView):
    """GET /api/v1/productsections/all"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all product sections matching old Swagger format."""
        sections = ProductSection.objects.filter(is_active=True).order_by('-id')
        serializer = ProductSectionCompatibilitySerializer(sections, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['ProductSections'],
    parameters=[
        OpenApiParameter('groupName', str, location=OpenApiParameter.QUERY, description='Group name to filter sections'),
    ],
    responses={
        200: {
            'description': 'Product sections by group name',
            'content': {
                'application/json': {
                    'example': {
                        'data': [],
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class ProductSectionsByGroupNameView(APIView):
    """GET /api/v1/productsections/by-group-name"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get product sections by group name matching old Swagger format."""
        group_name = request.query_params.get('groupName', '').strip()
        if not group_name:
            return create_success_response(data=[])
        
        sections = ProductSection.objects.filter(
            group_name=group_name,
            is_active=True
        ).order_by('-id')
        
        serializer = ProductSectionCompatibilitySerializer(sections, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['ProductSections'],
    parameters=[
        OpenApiParameter('page', str, location=OpenApiParameter.QUERY, description='Page name (e.g., "home")'),
        OpenApiParameter('pageNumber', int, location=OpenApiParameter.QUERY, description='Page number for pagination'),
        OpenApiParameter('pageSize', int, location=OpenApiParameter.QUERY, description='Page size for pagination'),
    ],
    responses={
        200: {
            'description': 'Product sections by page',
            'content': {
                'application/json': {
                    'example': {
                        'data': [],
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class ProductSectionsByPageView(APIView):
    """GET /api/v1/productsections/by-page"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get product sections by page matching old Swagger format."""
        page_name = request.query_params.get('page', 'home')
        
        qs = ProductSection.objects.filter(
            page=page_name,
            is_active=True
        ).order_by('-id')
        
        serializer = ProductSectionCompatibilitySerializer(qs, many=True, context={'request': request})
        return create_success_response(data=serializer.data)

