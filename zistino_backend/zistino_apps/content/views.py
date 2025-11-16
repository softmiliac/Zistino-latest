from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from .models import Testimonial, Tag, MenuLink, BlogCategory, BlogTag, BlogPost
from .serializers import (
    TestimonialSerializer, TagSerializer, MenuLinkSerializer,
    TestimonialSearchRequestSerializer, TagSearchRequestSerializer,
    MenuLinkSearchRequestSerializer,
    BlogCategorySerializer, BlogTagSerializer, BlogPostSerializer,
    BlogPostSearchRequestSerializer, BlogCategorySearchRequestSerializer,
    BlogTagSearchRequestSerializer
)


@extend_schema(tags=['Content'], exclude=True)  # Excluded: using compatibility layer instead
class TestimonialViewSet(viewsets.ModelViewSet):
    """ViewSet for managing testimonials."""
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='testimonials_search',
        request=TestimonialSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all testimonials',
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
                    'keyword': 'excellent'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for testimonials with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()

        qs = Testimonial.objects.all()

        if keyword:
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(text__icontains=keyword)
            )

        qs = qs.order_by('-rate', '-created_at')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        return Response({
            'items': TestimonialSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Content'], exclude=True)  # Excluded: using compatibility layer instead
class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tags."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='tags_search',
        request=TagSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all tags',
                value={
                    'pageNumber': 1,
                    'pageSize': 8
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for tags with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 8)

        qs = Tag.objects.all().order_by('text')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        total = qs.count()
        total_pages = (total + page_size - 1) // page_size

        return Response({
            'data': TagSerializer(items, many=True).data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'hasNextPage': page_number < total_pages,
            'hasPreviousPage': page_number > 1,
        })


@extend_schema(tags=['Content'])
class MenuLinkViewSet(viewsets.ModelViewSet):
    """ViewSet for managing menu links."""
    queryset = MenuLink.objects.all()
    serializer_class = MenuLinkSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='menulinks_search',
        request=MenuLinkSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all menu links',
                value={
                    'pageNumber': 1,
                    'pageSize': 7,
                    'keyword': '',
                    'orderBy': ['name']
                }
            ),
            OpenApiExample(
                'Search by keyword',
                value={
                    'pageNumber': 1,
                    'pageSize': 7,
                    'keyword': 'home',
                    'orderBy': ['name']
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for menu links with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 7)
        keyword = (request.data.get('keyword') or '').strip()
        order_by = request.data.get('orderBy', ['name'])

        qs = MenuLink.objects.all()

        if keyword:
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(link_url__icontains=keyword)
            )

        # Handle orderBy if provided
        if order_by and isinstance(order_by, list) and len(order_by) > 0:
            qs = qs.order_by(*order_by)
        else:
            qs = qs.order_by('name')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        total = qs.count()
        total_pages = (total + page_size - 1) // page_size

        return Response({
            'data': MenuLinkSerializer(items, many=True).data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'hasNextPage': page_number < total_pages,
            'hasPreviousPage': page_number > 1,
        })

    @extend_schema(
        tags=['Admin'],
        operation_id='menulinks_all',
        examples=[
            OpenApiExample(
                'Get all menu links',
                value={}
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='all', permission_classes=[AllowAny])
    def all(self, request):
        """Get all menu links without pagination (for dropdowns)."""
        qs = MenuLink.objects.all().order_by('name')
        return Response({
            'data': MenuLinkSerializer(qs, many=True).data
        })


@extend_schema(tags=['BlogPosts'])
class BlogPostViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog posts."""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_search',
        summary='Search BlogPosts using available Filters',
        description='Search BlogPosts using available Filters.',
        request=BlogPostSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all blog posts',
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
                    'keyword': 'django'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for blog posts with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()

        qs = BlogPost.objects.all().select_related('category').prefetch_related('tags')

        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword) |
                Q(content__icontains=keyword) |
                Q(excerpt__icontains=keyword) |
                Q(author_name__icontains=keyword)
            )

        qs = qs.order_by('-published_at', '-created_at')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        return Response({
            'items': BlogPostSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })

    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_dapper',
        summary='Get blog posts (dapper context)',
        description='Get blog posts in dapper context.',
        responses={200: BlogPostSerializer}
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get blog posts in dapper context."""
        posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_all',
        summary='Retrieves all blog posts',
        description='Retrieves all blog posts.',
        responses={200: BlogPostSerializer}
    )
    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        """Get all blog posts."""
        posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)


    @extend_schema(
        tags=['BlogPosts'],
        operation_id='blogposts_client_search',
        summary='Search blog posts for client',
        description='Search blog posts for client-side use. orderBy values: "Newest".',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'keyword': {'type': 'string', 'description': 'Search keyword'},
                    'pageNumber': {'type': 'integer', 'description': 'Page number (default: 1)'},
                    'pageSize': {'type': 'integer', 'description': 'Page size (default: 20)'},
                    'orderBy': {'type': 'string', 'description': 'Order by (e.g., "Newest")'},
                }
            }
        },
        responses={200: {
            'description': 'Search results',
            'content': {
                'application/json': {
                    'example': {
                        'items': [],
                        'pageNumber': 1,
                        'pageSize': 20,
                        'total': 0
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='client/search')
    def client_search(self, request):
        """Client search endpoint for blog posts with pagination."""
        page_number = int(request.data.get('pageNumber', 1))
        page_size = int(request.data.get('pageSize', 20))
        keyword = (request.data.get('keyword') or '').strip()
        order_by = request.data.get('orderBy', 'Newest')

        qs = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags')

        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword) |
                Q(content__icontains=keyword) |
                Q(excerpt__icontains=keyword) |
                Q(author_name__icontains=keyword)
            )

        # Order by newest (most recent first)
        if order_by == 'Newest':
            qs = qs.order_by('-published_at', '-created_at')
        else:
            qs = qs.order_by('-published_at', '-created_at')

        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        serializer = BlogPostSerializer(items, many=True)
        return Response({
            'items': serializer.data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': total,
        })


# ============================================================================
# SEPARATE APIView CLASSES FOR CUSTOM ENDPOINTS WITH PATH PARAMETERS
# These need custom URL patterns because they don't fit router pattern
# ============================================================================

@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_by_parentid',
    summary='Get blog posts by parent ID',
    description='Get blog posts by parent ID (category ID).',
    responses={200: BlogPostSerializer}
)
class BlogPostsByParentIdView(APIView):
    """GET /api/v1/blogposts/by-parentid/{id} - Get blog posts by parent/category ID"""
    permission_classes = [AllowAny]
    
    def get(self, request, id):
        posts = BlogPost.objects.filter(category_id=id, is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_client_recents',
    summary='Get recent blog posts for client',
    description='Get recent blog posts for client-side use.',
    responses={200: BlogPostSerializer}
)
class BlogPostsClientRecentsView(APIView):
    """GET /api/v1/blogposts/client/recents/{count} - Get recent blog posts for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, count):
        count = int(count) if count else 10
        posts = BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('tags').order_by('-published_at', '-created_at')[:count]
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=['BlogPosts'],
    operation_id='blogposts_client_byslug',
    summary='Get blog post by slug for client',
    description='Get blog post by slug for client-side use.',
    responses={200: BlogPostSerializer}
)
class BlogPostsClientBySlugView(APIView):
    """GET /api/v1/blogposts/client/byslug/{slug} - Get blog post by slug for client"""
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug, is_published=True)
            # Increment views count
            post.views_count += 1
            post.save(update_fields=['views_count'])
            serializer = BlogPostSerializer(post)
            return Response(serializer.data)
        except BlogPost.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Blog'])
class BlogCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog categories."""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Admin'],
        operation_id='blogcategories_search',
        request=BlogCategorySearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all blog categories',
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
                    'keyword': 'technology'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for blog categories with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()

        qs = BlogCategory.objects.all()

        if keyword:
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(slug__icontains=keyword)
            )

        qs = qs.order_by('name')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        return Response({
            'items': BlogCategorySerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['BlogTags'])
class BlogTagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog tags."""
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_search',
        summary='Search BlogTags using available Filters',
        description='Search BlogTags using available Filters.',
        request=BlogTagSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search all blog tags',
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
                    'keyword': 'python'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for blog tags with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()

        qs = BlogTag.objects.all()

        if keyword:
            qs = qs.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(slug__icontains=keyword)
            )

        qs = qs.order_by('name')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        return Response({
            'items': BlogTagSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })

    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_dapper',
        summary='Get blog tags (dapper context)',
        description='Get blog tags in dapper context.',
        responses={200: BlogTagSerializer}
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get blog tags in dapper context."""
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagSerializer(tags, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_all',
        summary='Retrieves all blog tags',
        description='Retrieves all blog tags.',
        responses={200: BlogTagSerializer}
    )
    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        """Get all blog tags."""
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagSerializer(tags, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['BlogTags'],
        operation_id='blogtags_client_all',
        summary='Retrieves all blog tags for client-side use',
        description='Retrieves all blog tags specifically for client-side use.',
        responses={200: BlogTagSerializer}
    )
    @action(detail=False, methods=['get'], url_path='client/all')
    def client_all(self, request):
        """Get all blog tags for client."""
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagSerializer(tags, many=True)
        return Response(serializer.data)

