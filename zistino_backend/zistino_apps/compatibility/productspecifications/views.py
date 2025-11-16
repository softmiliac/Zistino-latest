"""
Views for ProductSpecifications compatibility layer.
Provides all 7 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from django.shortcuts import get_object_or_404
from django.db.models import Q

from zistino_apps.products.models import Specification, Product
from zistino_apps.products.serializers import SpecificationSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from .serializers import (
    ProductSpecificationCreateRequestSerializer,
    ProductSpecificationSearchRequestSerializer,
    ProductSpecificationCompatibilitySerializer,
)


@extend_schema(tags=['ProductSpecifications'])
class ProductSpecificationsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductSpecifications endpoints.
    Wraps the existing SpecificationViewSet functionality and adds compatibility endpoints.
    """
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_list',
        summary='List all product specifications',
    )
    def list(self, request, *args, **kwargs):
        """List all product specifications."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_retrieve',
        summary='Retrieve a product specification by ID',
        responses={
            200: {
                'description': 'Product specification details',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 1,
                                'category': 'string',
                                'content': 'string',
                                'locale': 'string'
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
        """Retrieve a product specification by ID matching old Swagger format."""
        instance = self.get_object()
        serializer = ProductSpecificationCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_create',
        summary='Create a new product specification',
        request=ProductSpecificationCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create product specification',
                value={
                    'category': 'string',
                    'content': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: {
                'description': 'Product specification created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new product specification matching old Swagger format."""
        serializer = ProductSpecificationCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Validate content is required for create
        content = validated_data.get('content')
        if not content:
            return create_error_response(
                error_message='content field is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'content': ['This field is required.']}
            )
        
        # Note: The old Swagger format has category, content, locale
        # But the Specification model has product (OneToOneField), size, level
        # We'll map content to size, and we need a product
        # Since product is required in the model but not in the request, we'll need to handle this
        # For now, we'll create a specification with content mapped to size
        # But we need a product - this is a problem since product is OneToOneField and required
        
        # Try to find or create a product for this specification
        # Since we don't have productId in the request, we'll need to handle this differently
        # For now, let's create a specification with a dummy product or return an error
        
        # Actually, looking at the model, Specification has OneToOneField with Product
        # So we can't create a Specification without a Product
        # The old Swagger might be expecting a different structure
        
        # Let's check if we can create a Specification with just the content
        # We'll need to either:
        # 1. Require productId in the request (but old Swagger doesn't have it)
        # 2. Create a temporary product
        # 3. Store the data differently
        
        # For now, let's create a minimal product and then the specification
        # This is not ideal but matches the old Swagger format
        
        try:
            from zistino_apps.products.models import Category
            
            # Get category if provided
            category_name = validated_data.get('category', '').strip()
            category = None
            if category_name:
                # Try to find existing category by name
                try:
                    category = Category.objects.filter(name__icontains=category_name).first()
                except:
                    pass
            
            # If no category found, get first available category
            # Product model requires a category (ForeignKey, not nullable)
            if not category:
                category = Category.objects.first()
                if not category:
                    return create_error_response(
                        error_message='No category available. Please create a category first.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'category': ['No category available in the system.']}
                    )
            
            # Create a product for this specification
            # Note: Specification model requires a Product (OneToOneField)
            # The old Swagger format doesn't include productId, so we create a minimal product
            product_name = f'Specification - {content[:50]}' if len(content) > 50 else f'Specification - {content}'
            temp_product = Product.objects.create(
                name=product_name,
                description=content,  # Use content as description
                category=category,
                price_per_unit=0,
                unit='kg',
                is_active=True
            )
            
            # Create Specification with content mapped to size
            specification = Specification.objects.create(
                product=temp_product,
                size=content,
                level=category_name if category_name else ''  # Store category in level field
            )
            
            return create_success_response(data=specification.id)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating product specification: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_update',
        summary='Update a product specification',
        request=ProductSpecificationCreateRequestSerializer,
        responses={
            200: {
                'description': 'Product specification updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 1,
                                'category': 'string',
                                'content': 'string',
                                'locale': 'string'
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
        """Update a product specification matching old Swagger format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ProductSpecificationCreateRequestSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Map old Swagger fields to Django model fields
        content = validated_data.get('content')
        category_name = validated_data.get('category', '').strip()
        
        # Update size field (content)
        if 'content' in validated_data:
            instance.size = content
        
        # Update level field (category)
        if 'category' in validated_data:
            instance.level = category_name if category_name else ''
        
        # Handle category update for product if needed
        if category_name and instance.product:
            from zistino_apps.products.models import Category
            try:
                category = Category.objects.filter(name__icontains=category_name).first()
                if category:
                    instance.product.category = category
                    instance.product.save()
            except:
                pass
        
        instance.save()
        
        response_serializer = ProductSpecificationCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=response_serializer.data)

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_partial_update',
        summary='Partially update a product specification',
        request=ProductSpecificationCreateRequestSerializer,
        responses={
            200: {
                'description': 'Product specification updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 1,
                                'category': 'string',
                                'content': 'string',
                                'locale': 'string'
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
        """Partially update a product specification matching old Swagger format."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_destroy',
        summary='Delete a product specification',
        responses={
            200: {
                'description': 'Product specification deleted successfully',
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
        """Delete a product specification matching old Swagger format."""
        instance = self.get_object()
        instance.delete()
        return create_success_response(data=None)

    @extend_schema(
        tags=['ProductSpecifications'],
        operation_id='productspecifications_search',
        summary='Search product specifications using available filters',
        request=ProductSpecificationSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search product specifications',
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
            200: {
                'description': 'Product specifications search results',
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
        """Search product specifications with pagination and filters matching old Swagger format."""
        serializer = ProductSpecificationSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Get keyword from advancedSearch or top-level
        keyword = validated_data.get('keyword', '').strip()
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and isinstance(advanced_search, dict):
            advanced_keyword = advanced_search.get('keyword') or ''
            keyword = advanced_keyword or keyword
        
        # Get pagination (0 defaults to 1)
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        if page_number == 0:
            page_number = 1
        if page_size == 0:
            page_size = 1
        
        # Build query
        qs = Specification.objects.all()
        
        # Apply keyword filter
        if keyword:
            qs = qs.filter(
                Q(size__icontains=keyword) |
                Q(level__icontains=keyword) |
                Q(product__name__icontains=keyword)
            )
        
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
        serialized_items = SpecificationSerializer(items, many=True).data
        
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


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['ProductSpecifications'],
    parameters=[
        OpenApiParameter('id', int, location=OpenApiParameter.QUERY, description='Optional specification ID', required=False),
    ],
    responses={
        200: {
            'description': 'Product specifications in dapper context',
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
class ProductSpecificationsDapperView(APIView):
    """GET /api/v1/productspecifications/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get product specifications in dapper context. Accepts optional id parameter."""
        specification_id = request.query_params.get('id')
        
        if specification_id:
            try:
                specification = Specification.objects.get(id=specification_id)
                serializer = ProductSpecificationCompatibilitySerializer(specification, context={'request': request})
                return create_success_response(data=serializer.data)
            except Specification.DoesNotExist:
                return create_success_response(data=None)
        
        return create_success_response(data=None)


@extend_schema(
    tags=['ProductSpecifications'],
    responses={
        200: {
            'description': 'Product specification cloned successfully',
            'content': {
                'application/json': {
                    'example': {
                        'data': 2,
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class ProductSpecificationsCloneView(APIView):
    """GET /api/v1/productspecifications/clone/{id}"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, id):
        """Clone a product specification matching old Swagger format."""
        original = get_object_or_404(Specification, id=id)
        
        try:
            # Create a new product for the cloned specification
            from zistino_apps.products.models import Category
            
            # Get category from original product or use first available
            category = original.product.category if original.product and original.product.category else Category.objects.first()
            
            if not category:
                return create_error_response(
                    error_message='No category available. Please create a category first.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'category': ['No category available in the system.']}
                )
            
            # Create a new product for the cloned specification
            cloned_product = Product.objects.create(
                name=f'Cloned - {original.product.name if original.product else "Specification"}',
                description=original.product.description if original.product else original.size,
                category=category,
                price_per_unit=original.product.price_per_unit if original.product else 0,
                unit=original.product.unit if original.product else 'kg',
                is_active=True
            )
            
            # Create cloned specification
            cloned_specification = Specification.objects.create(
                product=cloned_product,
                size=original.size,
                level=original.level
            )
            
            return create_success_response(data=cloned_specification.id)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while cloning product specification: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

