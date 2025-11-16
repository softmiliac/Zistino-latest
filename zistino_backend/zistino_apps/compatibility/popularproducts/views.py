"""
Compatibility views for PopularProducts endpoints.
All endpoints will appear under "PopularProducts" folder in Swagger UI.

Note: This controller doesn't exist in the old Swagger, but Flutter app expects it.
We'll create basic endpoints that return products, potentially filtered/sorted for popularity.
Popularity can be determined by:
- Most ordered products
- Most viewed products
- Products in "popular" ProductSection group
- Or any custom logic

For now, we'll return active products sorted by creation date (newest first) as a placeholder.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.db.models import Q, Count, Avg

from zistino_apps.products.models import Product, ProductSection
from zistino_apps.products.serializers import ProductSerializer
from zistino_apps.compatibility.products.views import apply_order_by
from zistino_apps.compatibility.utils import create_success_response
from zistino_apps.compatibility.products.serializers import (
    ProductCompatibilitySerializer,
    ProductAdminSearchExtResponseSerializer,
)

from .serializers import (
    PopularProductSearchRequestSerializer,
    PopularProductClientSearchRequestSerializer,
)


@extend_schema(tags=['PopularProducts'])
class PopularProductsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing popular products.
    All endpoints will appear under "PopularProducts" folder in Swagger UI.
    
    Note: This is a read-only viewset since popularity is typically calculated,
    not manually set. Admin can manage products through the Products controller.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductCompatibilitySerializer  # Use compatibility serializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Get popular products.
        Popularity can be determined by:
        1. Most ordered products (from OrderItem counts)
        2. Products in "popular" ProductSection group
        3. Most recently created (as fallback)
        """
        # Try to get products from "popular" ProductSection group first
        popular_sections = ProductSection.objects.filter(
            group_name__icontains='popular',
            is_active=True
        )
        
        if popular_sections.exists():
            # If there are ProductSections with "popular" in group_name,
            # we could return products from those sections
            # For now, just return active products sorted by creation date
            pass
        
        # Calculate popularity based on order count
        # Products that appear in more orders are more popular
        # Note: OrderItem has product_name (string), not a ForeignKey to Product
        # So we'll use a different approach: count by product name matching
        # For now, return active products sorted by creation date (newest first)
        # TODO: Implement proper popularity calculation when product_id is added to OrderItem
        qs = Product.objects.filter(is_active=True).order_by('-created_at')
        
        return qs

    @extend_schema(
        tags=['PopularProducts'],
        operation_id='popularproducts_list',
        summary='List all popular products',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of popular products',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 'string',
                                    'name': 'string',
                                    'description': 'string',
                                    'rate': 0,
                                    'categories': 'string',
                                    'categoryIds': [0],
                                    'viewsCount': 0,
                                    'likesCount': 0,
                                    'commentsCount': 0,
                                    'ordersCount': 0,
                                    'size': 'string',
                                    'isMaster': True,
                                    'masterId': 'string',
                                    'colorsList': 'string',
                                    'masterColor': 'string',
                                    'pricesList': 'string',
                                    'masterPrice': 0,
                                    'imagesList': 'string',
                                    'masterImage': 'string',
                                    'thumbnail': 'string',
                                    'warranty': 'string',
                                    'specifications': 'string',
                                    'tags': 'string',
                                    'tagIds': [0],
                                    'brandId': 'string',
                                    'brandName': 'string',
                                    'discountPercent': 0,
                                    'inStock': 0,
                                    'isActive': True,
                                    'locale': 'string',
                                    'productTexts': [],
                                    'hieght': 0,
                                    'width': 0,
                                    'length': 0,
                                    'weight': 'string',
                                    'type': 0,
                                    'city': 'string',
                                    'country': 'string',
                                    'state': 'string',
                                    'unitCount': 0,
                                    'inStockAlert': True,
                                    'buyPrice': 0,
                                    'code': 'string',
                                    'barCode': 'string',
                                    'atLeast': 0,
                                    'atMost': 0,
                                    'jsonExt': 'string',
                                    'seoSetting': 'string',
                                    'verify': 0,
                                    'issue': 'string',
                                    'expaireDate': '2025-11-11T08:05:20.203Z',
                                    'p1': 'string',
                                    'p2': 'string',
                                    'p3': 'string',
                                    'p4': 'string',
                                    'p5': 'string',
                                    'f1': 0,
                                    'f2': 0,
                                    'f3': 0,
                                    'f4': 0,
                                    'f5': 0,
                                    'r1': 0,
                                    'r2': 0,
                                    'r3': 0,
                                    'r4': 0,
                                    'r5': 0
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    def list(self, request, *args, **kwargs):
        """List all popular products. Returns format matching products/list."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ProductCompatibilitySerializer(queryset, many=True, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['PopularProducts'],
        operation_id='popularproducts_retrieve',
        summary='Retrieve a popular product by ID',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Popular product details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': {
                                'id': 'string',
                                'name': 'string',
                                'description': 'string',
                                'rate': 0,
                                'categories': 'string',
                                'categoryIds': [0],
                                'viewsCount': 0,
                                'likesCount': 0,
                                'commentsCount': 0,
                                'ordersCount': 0,
                                'size': 'string',
                                'isMaster': True,
                                'masterId': 'string',
                                'colorsList': 'string',
                                'masterColor': 'string',
                                'pricesList': 'string',
                                'masterPrice': 0,
                                'imagesList': 'string',
                                'masterImage': 'string',
                                'thumbnail': 'string',
                                'warranty': 'string',
                                'specifications': 'string',
                                'tags': 'string',
                                'tagIds': [0],
                                'brandId': 'string',
                                'brandName': 'string',
                                'discountPercent': 0,
                                'inStock': 0,
                                'isActive': True,
                                'locale': 'string',
                                'productTexts': [],
                                'hieght': 0,
                                'width': 0,
                                'length': 0,
                                'weight': 'string',
                                'type': 0,
                                'city': 'string',
                                'country': 'string',
                                'state': 'string',
                                'unitCount': 0,
                                'inStockAlert': True,
                                'buyPrice': 0,
                                'code': 'string',
                                'barCode': 'string',
                                'atLeast': 0,
                                'atMost': 0,
                                'jsonExt': 'string',
                                'seoSetting': 'string',
                                'verify': 0,
                                'issue': 'string',
                                'expaireDate': '2025-11-11T08:05:20.203Z',
                                'p1': 'string',
                                'p2': 'string',
                                'p3': 'string',
                                'p4': 'string',
                                'p5': 'string',
                                'f1': 0,
                                'f2': 0,
                                'f3': 0,
                                'f4': 0,
                                'f5': 0,
                                'r1': 0,
                                'r2': 0,
                                'r3': 0,
                                'r4': 0,
                                'r5': 0
                            }
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a popular product by ID. Returns format matching products/retrieve."""
        instance = self.get_object()
        serializer = ProductCompatibilitySerializer(instance, context={'request': request})
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['PopularProducts'],
        operation_id='popularproducts_search',
        summary='Search Popular Products',
        description='Search popular products using available filters matching products/search format.',
        request=PopularProductSearchRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results with pagination',
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
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[AllowAny])
    def search(self, request):
        """Search popular products with pagination matching products/search format."""
        # Handle empty request body - all fields are optional
        request_data = request.data if request.data else {}
        serializer = PopularProductSearchRequestSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Build query - start with active products
        qs = Product.objects.filter(is_active=True)
        
        # Apply keyword search
        keyword = validated_data.get('keyword') or ''
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and isinstance(advanced_search, dict):
            # Use keyword from advancedSearch if provided, otherwise use top-level keyword
            advanced_keyword = advanced_search.get('keyword') or ''
            keyword = advanced_keyword or keyword
        
        # Only apply keyword filter if keyword is not empty
        if keyword and keyword.strip():
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        # Apply brand filter
        brand_id = validated_data.get('brandId')
        if brand_id and brand_id.strip():
            try:
                from uuid import UUID
                brand_uuid = UUID(brand_id)
                # TODO: Filter by brand when brand relationship is implemented
                # qs = qs.filter(brand_id=brand_uuid)
            except (ValueError, TypeError):
                pass  # Invalid UUID, skip filter
        
        # Apply rate filter (from comments)
        min_rate = validated_data.get('minimumRate', 0)
        max_rate = validated_data.get('maximumRate', 0)
        if min_rate > 0 or max_rate > 0:
            # Filter products by average rating from comments
            products_with_ratings = Product.objects.annotate(
                avg_rating=Avg('comments__rate', filter=Q(comments__is_accepted=True))
            ).filter(avg_rating__gte=min_rate if min_rate > 0 else 0)
            
            if max_rate > 0:
                products_with_ratings = products_with_ratings.filter(avg_rating__lte=max_rate)
            
            product_ids = products_with_ratings.values_list('id', flat=True)
            qs = qs.filter(id__in=product_ids)
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        # Filter out empty strings and None values from orderBy list
        order_by = [field for field in order_by if field and field.strip()]
        # If orderBy is empty or only contains empty strings, default to newest
        if not order_by:
            order_by = ['newest']  # Default to newest when empty
        qs = apply_order_by(qs, order_by)
        
        # Get total count before pagination
        total_count = qs.count()
        
        # Handle pagination (pageNumber: 0 defaults to 1, pageSize: 0 defaults to 1)
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        if page_number == 0:
            page_number = 1
        if page_size == 0:
            page_size = 1
        
        # Apply pagination
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        # Use ProductCompatibilitySerializer for output
        product_serializer = ProductCompatibilitySerializer(items, many=True, context={'request': request})
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
        has_previous_page = page_number > 1
        has_next_page = page_number < total_pages if total_pages > 0 else False
        
        # Return format matching old Swagger: data array with pagination fields at root level, messages: null
        return Response({
            "data": product_serializer.data,
            "currentPage": page_number,
            "totalPages": total_pages,
            "totalCount": total_count,
            "pageSize": page_size,
            "hasPreviousPage": has_previous_page,
            "hasNextPage": has_next_page,
            "messages": None,
            "succeeded": True
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['PopularProducts'],
        operation_id='popularproducts_client_search',
        summary='Client Search Popular Products',
        description='Client search for popular products matching products/client/search format.',
        request=PopularProductClientSearchRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Products matching search criteria',
                examples=[
                    OpenApiExample(
                        'Success response with data',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': {
                                'data': [],
                                'currentPage': 0,
                                'totalPages': -2147483648,
                                'totalCount': 0,
                                'pageSize': 0,
                                'hasPreviousPage': False,
                                'hasNextPage': False,
                                'messages': None,
                                'succeeded': True
                            }
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='client/search', permission_classes=[AllowAny])
    def client_search(self, request):
        """Client search for popular products matching products/client/search format."""
        serializer = PopularProductClientSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        page_number = serializer.validated_data.get('pageNumber', 0) or 1
        page_size = serializer.validated_data.get('pageSize', 0) or 20
        keyword = serializer.validated_data.get('keyword', '').strip() if serializer.validated_data.get('keyword') else ''
        brands = serializer.validated_data.get('brands', '').strip() if serializer.validated_data.get('brands') else ''
        category_id = serializer.validated_data.get('categoryId')
        min_price = serializer.validated_data.get('minPrice')
        max_price = serializer.validated_data.get('maxPrice')
        order_by = serializer.validated_data.get('orderBy', [])

        qs = Product.objects.filter(is_active=True)
        
        # Apply filters
        if keyword:
            qs = qs.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
        if brands:
            # TODO: Filter by brand name when brand relationship is implemented
            pass
        if category_id:
            qs = qs.filter(category_id=category_id)
        if min_price is not None:
            qs = qs.filter(price_per_unit__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price_per_unit__lte=max_price)
        
        qs = apply_order_by(qs, order_by)
        
        # Paginate
        start = (page_number - 1) * page_size if page_size > 0 else 0
        end = start + page_size if page_size > 0 else 0
        items = qs[start:end] if page_size > 0 else qs[:20]
        total_count = qs.count()

        # Use ProductAdminSearchExtResponseSerializer for output
        product_serializer = ProductAdminSearchExtResponseSerializer(items, many=True, context={'request': request})
        
        # Calculate totalPages (matching old Swagger behavior: -2147483648 when pageSize is 0)
        if page_size > 0:
            total_pages = (total_count + page_size - 1) // page_size
        else:
            total_pages = -2147483648  # Match old Swagger behavior
        
        # Return nested format: data.data with pagination fields inside data
        return create_success_response(data={
            'data': product_serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': page_number > 1,
            'hasNextPage': end < total_count if page_size > 0 else False,
            'messages': None,
            'succeeded': True
        })

