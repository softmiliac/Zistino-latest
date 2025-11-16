from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from zistino_apps.users.permissions import IsManager

from .models import Category, Product, Color, Price, Specification, Warranty, FAQ, ProductSection, Problem, ProductCode
from zistino_apps.notifications.models import Comment
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ColorSerializer,
    PriceSerializer,
    SpecificationSerializer,
    WarrantySerializer,
    FAQSerializer,
    ProductCommentSerializer,
    ProductIdRequestSerializer,
    ProductSearchRequestSerializer,
    ProductSectionSerializer,
    FAQSearchRequestSerializer,
    WarrantySearchRequestSerializer,
    SpecificationSearchRequestSerializer,
    ProductSectionSearchRequestSerializer,
    ProblemSerializer,
    ProblemSearchRequestSerializer,
    ProductCodeSerializer,
    ProductCodeBulkImportSerializer,
)


@extend_schema(tags=['Products'])
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return all categories (including inactive) for admin, active only for others."""
        if self.action in ['list', 'retrieve']:
            # For GET requests, use the default queryset (active only)
            return Category.objects.filter(is_active=True)
        # For admin operations, return all
        return Category.objects.all()

    def get_permissions(self):
        """Admin-only for create/update/delete, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='categories_search',
        request=ProductSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search categories',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': 'herbs'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for categories with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        order_by = request.data.get('orderBy', ['name'])
        
        qs = Category.objects.all()  # Admin sees all categories
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        
        # Handle orderBy if provided
        if order_by and isinstance(order_by, list) and len(order_by) > 0:
            qs = qs.order_by(*order_by)
        else:
            qs = qs.order_by('name')
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': CategorySerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Products'], exclude=True)  # Excluded: using compatibility layer instead
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return all products (including inactive) for admin, active only for others."""
        if self.action in ['list', 'retrieve']:
            # For GET requests, use the default queryset (active only)
            return Product.objects.filter(is_active=True)
        # For admin operations, return all
        return Product.objects.all()

    def get_permissions(self):
        """Admin-only for create/update/delete, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='products_search',
        request=ProductSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search products',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': 'product name',
                    'orderBy': ['name']
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for products with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        order_by = request.data.get('orderBy', ['name'])
        
        qs = Product.objects.all()  # Admin sees all products (including inactive)
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        
        # Handle orderBy if provided
        if order_by and isinstance(order_by, list) and len(order_by) > 0:
            qs = qs.order_by(*order_by)
        else:
            qs = qs.order_by('name')
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': ProductSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })

    @extend_schema(tags=['Customer'], operation_id='products_client_search', request=ProductSearchRequestSerializer)
    @action(detail=False, methods=['post'], url_path='client/search', permission_classes=[AllowAny])
    def client_search(self, request):
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        qs = self.get_queryset()
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs.order_by('name')[start:end]
        return Response({
            'items': ProductSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })

    @extend_schema(tags=['Customer'], operation_id='products_by_type')
    @action(detail=False, methods=['get'], url_path='client/by-type/(?P<type_id>[^/.]+)', permission_classes=[AllowAny])
    def by_type(self, request, type_id=None):
        # Placeholder: map type_id to categories or flags as needed
        qs = self.get_queryset()
        return Response(ProductSerializer(qs[:50], many=True).data)

    @extend_schema(tags=['Customer'], operation_id='products_by_categoryid')
    @action(detail=False, methods=['get'], url_path='client/by-categoryid', permission_classes=[AllowAny])
    def by_categoryid(self, request):
        category_id = request.query_params.get('categoryId')
        qs = self.get_queryset()
        if category_id:
            qs = qs.filter(category_id=category_id)
        return Response(ProductSerializer(qs[:50], many=True).data)

    @extend_schema(tags=['Customer'], operation_id='products_byproductid')
    @action(detail=False, methods=['get'], url_path='byproductid', permission_classes=[AllowAny])
    def by_product_id(self, request):
        pid = request.query_params.get('id')
        if not pid:
            return Response({'detail': 'id is required'}, status=400)
        try:
            obj = Product.objects.get(pk=pid, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        return Response(ProductSerializer(obj).data)

    @extend_schema(
        tags=['Products'],
        operation_id='product_comments',
        summary='Get product comments',
        description='Get all comments/reviews for a specific product. Returns comments with user information, ratings, and timestamps.',
        responses={
            200: {
                'description': 'Comments retrieved successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'with_comments': {
                                'summary': 'Product with comments',
                                'value': {
                                    'product_id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'comments': [
                                        {
                                            'id': 1,
                                            'product': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'user_id': 1,
                                            'user_full_name': 'John Doe',
                                            'user_image_url': 'https://example.com/media/profiles/user.jpg',
                                            'text': 'Great product! Very satisfied.',
                                            'rate': 5,
                                            'is_accepted': True,
                                            'created_on': '2025-01-15T10:30:00Z'
                                        },
                                        {
                                            'id': 2,
                                            'product': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'user_id': 2,
                                            'user_full_name': 'Jane Smith',
                                            'user_image_url': None,
                                            'text': 'Good quality, fast delivery.',
                                            'rate': 4,
                                            'is_accepted': True,
                                            'created_on': '2025-01-14T09:00:00Z'
                                        }
                                    ],
                                    'total': 2,
                                    'average_rating': 4.5
                                }
                            },
                            'no_comments': {
                                'summary': 'Product with no comments',
                                'value': {
                                    'product_id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'comments': [],
                                    'total': 0,
                                    'average_rating': 0.0
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Product not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['get'], url_path='comments', permission_classes=[AllowAny])
    def comments(self, request, pk=None):
        """Get all comments for a specific product."""
        from django.db.models import Avg
        from .serializers import ProductCommentSerializer
        
        # Verify product exists
        try:
            product = self.get_object()
        except Product.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        
        # Get all accepted comments for this product
        comments_qs = Comment.objects.filter(
            product_id=pk,
            is_accepted=True
        ).order_by('-created_on')
        
        # Calculate average rating
        avg_rating = comments_qs.aggregate(Avg('rate'))['rate__avg'] or 0.0
        
        # Serialize comments with request context for absolute URLs
        comments_data = ProductCommentSerializer(comments_qs, many=True, context={'request': request}).data
        
        return Response({
            'product_id': str(pk),
            'comments': comments_data,
            'total': len(comments_data),
            'average_rating': round(float(avg_rating), 2) if avg_rating else 0.0
        }, status=200)

    @extend_schema(
        tags=['Admin'],
        operation_id='product_codes_list',
        summary='List product codes',
        description='List codes for a specific product with optional status filter (unused, assigned, used).'
    )
    @action(detail=True, methods=['get'], url_path='codes', permission_classes=[IsAuthenticated, IsManager])
    def list_codes(self, request, pk=None):
        from .serializers import ProductCodeSerializer
        status_filter = request.query_params.get('status')
        qs = ProductCode.objects.filter(product_id=pk)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(ProductCodeSerializer(qs.order_by('status', 'created_at'), many=True).data)

    @extend_schema(
        tags=['Admin'],
        operation_id='product_codes_bulk_import',
        summary='Bulk import product codes',
        description='Bulk import redeemable codes for a product. Duplicate codes are skipped by unique constraint.',
        examples=[OpenApiExample('Bulk import', value={'codes': ['ABC-123', 'XYZ-789']})]
    )
    @action(detail=True, methods=['post'], url_path='codes/bulk-import', permission_classes=[IsAuthenticated, IsManager])
    def bulk_import_codes(self, request, pk=None):
        from .serializers import ProductCodeBulkImportSerializer
        serializer = ProductCodeBulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        codes = serializer.validated_data['codes']
        product = self.get_object()

        imported = 0
        skipped = 0
        for code in codes:
            code = (code or '').strip()
            if not code:
                continue
            try:
                ProductCode.objects.create(product=product, code=code, status='unused')
                imported += 1
            except Exception:
                skipped += 1

        return Response({'imported': imported, 'skipped': skipped})


@extend_schema(tags=['Products'])
class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['Products'])
class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['Products'], exclude=True)  # Excluded: using compatibility layer instead
class SpecificationViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='productspecifications_search',
        request=SpecificationSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Get all specifications',
                value={}
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for specifications - returns all specifications."""
        qs = Specification.objects.all().order_by('-id')
        return Response(SpecificationSerializer(qs, many=True).data)


@extend_schema(tags=['Products'], exclude=True)  # Excluded: using compatibility layer instead
class WarrantyViewSet(viewsets.ModelViewSet):
    queryset = Warranty.objects.all()
    serializer_class = WarrantySerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='warranties_search',
        request=WarrantySearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Get all warranties',
                value={}
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for warranties - returns all warranties."""
        qs = Warranty.objects.all().order_by('-id')
        return Response(WarrantySerializer(qs, many=True).data)


@extend_schema(tags=['Admin'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Faqs" folder instead
class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for search, AllowAny for read."""
        if self.action == 'search':
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='faqs_search',
        request=FAQSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Get all FAQs',
                value={}
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for FAQs - returns all FAQs (no pagination needed per panel)."""
        qs = FAQ.objects.all().order_by('-created_at')
        return Response(FAQSerializer(qs, many=True).data)

    @extend_schema(tags=['Customer'], operation_id='faqs_client_search')
    @action(detail=False, methods=['post'], url_path='client/search', permission_classes=[AllowAny])
    def client_search(self, request):
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        qs = self.get_queryset()
        if keyword:
            qs = qs.filter(question__icontains=keyword)
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        return Response({
            'items': FAQSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Customer'])
class ProductCommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_on')
    serializer_class = ProductCommentSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Customer'],
        operation_id='commentsbyproductidasync',
        request=ProductIdRequestSerializer,
        examples=[
            OpenApiExample(
                'By productId',
                description='Provide productId to fetch comments',
                value={'productId': '46e818ce-0518-4c64-8438-27bc7163a706'},
            )
        ],
    )
    @action(detail=False, methods=['post'], url_path='commentsbyproductidasync')
    def by_product(self, request):
        product_id = (
            request.data.get('productId')
            or request.data.get('product_id')
            or request.data.get('product')
            or request.data.get('id')
        )
        if not product_id:
            return Response({'detail': 'productId required'}, status=400)
        qs = self.queryset.filter(product_id=product_id)
        return Response(ProductCommentSerializer(qs, many=True).data)

    def perform_create(self, serializer):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            serializer.save(user=user)
        else:
            # Anonymous comments not allowed
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Authentication required')


@extend_schema(tags=['Customer'], operation_id='faqs_client_search')
class FaqClientSearchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        return Response({'items': [], 'pageNumber': page_number, 'pageSize': page_size, 'total': 0})


@extend_schema(tags=['Customer'], operation_id='comments_byproductidasync')
class CommentsByProductView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'items': []})

    def post(self, request):
        return Response({'message': 'comment received'}, status=201)


@extend_schema(
    tags=['Customer'],
    operation_id='cms_by_page',
    parameters=[
        OpenApiParameter(
            name='page',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Page name to filter sections (default: "home"). Examples: "home", "h5", etc.',
            examples=[
                OpenApiExample('home', value='home'),
                OpenApiExample('h5', value='h5'),
            ]
        ),
    ],
    examples=[
        OpenApiExample(
            'Get home page',
            description='Example: GET /api/v1/cms/by-page?page=home',
            value={},
        ),
    ]
)
class CMSByPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = request.query_params.get('page', 'home')
        qs = ProductSection.objects.filter(page=page, is_active=True).order_by('id')
        data = ProductSectionSerializer(qs, many=True).data
        return Response(data)


@extend_schema(
    tags=['Customer'],
    operation_id='cms_by_group_name',
    parameters=[
        OpenApiParameter(
            name='groupName',
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Group name to filter product sections (e.g., "herbs", "featured", etc.)',
            examples=[
                OpenApiExample('herbs', value='herbs'),
                OpenApiExample('featured', value='featured'),
            ]
        ),
    ],
    examples=[
        OpenApiExample(
            'Get by group',
            description='Example: GET /api/v1/cms/by-group-name?groupName=herbs',
            value={},
        ),
    ]
)
class CMSByGroupNameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        group_name = request.query_params.get('groupName', '')
        if not group_name:
            return Response({'detail': 'groupName is required'}, status=400)
        qs = ProductSection.objects.filter(group_name=group_name, is_active=True).order_by('id')
        data = ProductSectionSerializer(qs, many=True).data
        return Response(data)


@extend_schema(
    tags=['Customer'],
    operation_id='cms_page_view',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'page': {'type': 'string', 'example': 'home'},
            }
        }
    },
    examples=[
        OpenApiExample('Track page view', value={'page': 'home'}),
    ]
)
class CMSPageViewView(APIView):
    """Track page views (optional analytics endpoint)."""
    permission_classes = [AllowAny]

    def post(self, request):
        page = request.data.get('page', 'home')
        # Placeholder: can log to analytics DB later
        return Response({'message': 'Page view tracked', 'page': page})


@extend_schema(tags=['Products'], exclude=True)  # Excluded: using compatibility layer instead
class ProductSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product sections (CMS content)."""
    queryset = ProductSection.objects.all()
    serializer_class = ProductSectionSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='productsections_search',
        request=ProductSectionSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all sections',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': ''
                }
            ),
            OpenApiExample(
                'Search by keyword',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': 'featured'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for product sections with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        
        qs = ProductSection.objects.all()
        
        if keyword:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(page__icontains=keyword) |
                Q(group_name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        qs = qs.order_by('-id')
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': ProductSectionSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Products'], exclude=True)  # Excluded: using compatibility layer instead
class ProblemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product problems."""
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='problems_search',
        request=ProblemSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all problems',
                value={
                    'pageNumber': 1,
                    'pageSize': 20
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for problems with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)

        qs = Problem.objects.all().select_related('product', 'parent').order_by('-priority', 'title')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        return Response({
            'data': ProblemSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })

    @extend_schema(
        tags=['Admin'],
        request=ProblemSerializer,
        examples=[
            OpenApiExample(
                'Create a problem',
                value={
                    'title': 'Battery Replacement',
                    'description': 'Replace battery for iPhone models',
                    'iconUrl': 'https://example.com/icons/battery.png',
                    'parentId': 5,
                    'repairDuration': 30,
                    'price': '25.00',
                    'priority': 2,
                    'locale': 'en',
                    'productId': '46e818ce-0518-4c64-8438-27bc7163a706'
                }
            ),
            OpenApiExample(
                'Create a problem without parent',
                value={
                    'title': 'Screen Repair',
                    'description': 'Fix cracked screen for mobile devices',
                    'iconUrl': 'https://example.com/icons/screen-repair.png',
                    'repairDuration': 60,
                    'price': '50.00',
                    'priority': 1,
                    'locale': 'fa',
                    'productId': '46e818ce-0518-4c64-8438-27bc7163a706'
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        """Create a new problem. Requires productId (Product UUID)."""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=['Admin'],
        request=ProblemSerializer,
        examples=[
            OpenApiExample(
                'Update a problem - full',
                value={
                    'title': 'Screen Repair Updated',
                    'description': 'Fix cracked screen - updated description',
                    'iconUrl': 'https://example.com/icons/screen-repair-v2.png',
                    'repairDuration': 90,
                    'price': '75.00',
                    'priority': 2,
                    'locale': 'en',
                    'productId': '46e818ce-0518-4c64-8438-27bc7163a706'
                }
            ),
            OpenApiExample(
                'Update a problem - partial',
                value={
                    'title': 'Screen Repair - Quick Fix',
                    'price': '45.00',
                    'productId': '46e818ce-0518-4c64-8438-27bc7163a706'
                }
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        """Update a problem. All fields can be updated."""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['Admin'],
        request=ProblemSerializer,
        examples=[
            OpenApiExample(
                'Partial update a problem',
                value={
                    'price': '60.00',
                    'priority': 3
                }
            ),
            OpenApiExample(
                'Update only repair duration',
                value={
                    'repairDuration': 120
                }
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a problem."""
        return super().partial_update(request, *args, **kwargs)
