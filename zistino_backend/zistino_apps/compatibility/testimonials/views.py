"""
Views for Testimonials compatibility layer.
Implements all endpoints matching old Swagger format.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from django.db.models import Q

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from zistino_apps.content.models import Testimonial
from .serializers import (
    TestimonialCreateRequestSerializer,
    TestimonialSearchRequestSerializer,
    TestimonialDetailSerializer,
)


@extend_schema(tags=['Testimonials'])
class TestimonialsViewSet(viewsets.ViewSet):
    """
    ViewSet for Testimonials endpoints.
    All endpoints will appear under "Testimonials" folder in Swagger UI.
    """
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]  # retrieve is AllowAny

    @extend_schema(
        tags=['Testimonials'],
        operation_id='testimonials_create',
        summary='Create a new testimonial',
        description='Creates a new testimonial matching old Swagger format.',
        request=TestimonialCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Testimonial (default)',
                value={
                    "name": "string",
                    "text": "string",
                    "imageUrl": "string",
                    "thumbnail": "string",
                    "rate": 0,
                    "productId": "string",
                    "examId": 0,
                    "jobId": 0,
                    "blogId": 0,
                    "locale": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Testimonial created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request):
        """Create a new testimonial matching old Swagger format."""
        try:
            serializer = TestimonialCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Create testimonial (ignore productId, examId, jobId, blogId, thumbnail as they're not in model)
            testimonial = Testimonial.objects.create(
                name=validated_data['name'],
                text=validated_data['text'],
                image_url=validated_data.get('imageUrl') or validated_data.get('thumbnail') or '',
                rate=validated_data.get('rate', 0),
                locale=validated_data.get('locale', 'fa')
            )
            
            return create_success_response(
                data=testimonial.id,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating testimonial: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Testimonials'],
        operation_id='testimonials_search',
        summary='Search testimonials',
        description='Search testimonials with pagination and filters matching old Swagger format.',
        request=TestimonialSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": ["string"],
                        "keyword": "string",
                        "groupBy": ["string"]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": ["string"],
                    "productId": "string",
                    "examId": 0,
                    "jobId": 0,
                    "blogId": 0,
                    "locale": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results',
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
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search testimonials with pagination and filters matching old Swagger format."""
        try:
            serializer = TestimonialSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Handle pagination (0 means default)
            page_number = validated_data.get('pageNumber', 0)
            if page_number == 0:
                page_number = 1
            page_size = validated_data.get('pageSize', 0)
            if page_size == 0:
                page_size = 10  # Default page size
            
            # Build query
            qs = Testimonial.objects.all()
            
            # Keyword search
            keyword = validated_data.get('keyword', '').strip()
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '').strip()
            
            if keyword:
                qs = qs.filter(
                    Q(name__icontains=keyword) |
                    Q(text__icontains=keyword)
                )
            
            # Filter by locale
            locale = validated_data.get('locale')
            if locale:
                qs = qs.filter(locale=locale)
            
            # Ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out blank strings and validate fields
                valid_order_by = []
                for field in order_by:
                    if field and field.strip():
                        # Map field names
                        field_mapping = {
                            'name': 'name',
                            'text': 'text',
                            'rate': 'rate',
                            'createdAt': 'created_at',
                            'created_at': 'created_at',
                        }
                        mapped_field = field_mapping.get(field.strip(), None)
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-rate', '-created_at')
            else:
                qs = qs.order_by('-rate', '-created_at')
            
            # Pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
            
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]
            
            # Serialize results
            serializer = TestimonialDetailSerializer(items, many=True)
            
            return create_success_response(
                data=serializer.data,
                pagination={
                    "currentPage": page_number,
                    "totalPages": total_pages,
                    "totalCount": total_count,
                    "pageSize": page_size,
                    "hasPreviousPage": page_number > 1,
                    "hasNextPage": page_number < total_pages,
                }
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching testimonials: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Testimonials'],
        operation_id='testimonials_client',
        summary='Search testimonials (client)',
        description='Search testimonials for client with pagination and filters matching old Swagger format.',
        request=TestimonialSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Client Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": ["string"],
                        "keyword": "string",
                        "groupBy": ["string"]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": ["string"],
                    "productId": "string",
                    "examId": 0,
                    "jobId": 0,
                    "blogId": 0,
                    "locale": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results',
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
    @action(detail=False, methods=['post'], url_path='client')
    def client(self, request):
        """Search testimonials for client matching old Swagger format (same as search)."""
        # Same implementation as search
        return self.search(request)

    @extend_schema(
        tags=['Testimonials'],
        operation_id='testimonials_retrieve',
        summary='Get testimonial by ID',
        description='Retrieves a testimonial by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Testimonial ID')
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Testimonial details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "name": "new test mon",
                                "text": "string",
                                "imageUrl": "string",
                                "thumbnail": "string",
                                "rate": 0,
                                "productId": "94860000-b419-c60d-2b41-08dc425c06b1",
                                "examId": None,
                                "jobId": None,
                                "blogId": None,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Testimonial not found'}
        }
    )
    def retrieve(self, request, pk=None):
        """Get testimonial by ID matching old Swagger format."""
        try:
            try:
                testimonial = Testimonial.objects.get(id=pk)
            except Testimonial.DoesNotExist:
                return create_error_response(
                    error_message=f'Testimonial with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Testimonial with ID "{pk}" not found.']}
                )
            
            serializer = TestimonialDetailSerializer(testimonial)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Testimonials'],
        operation_id='testimonials_update',
        summary='Update testimonial',
        description='Updates a testimonial by ID matching old Swagger format.',
        request=TestimonialCreateRequestSerializer,
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Testimonial ID')
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Testimonial updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "name": "new test mon",
                                "text": "string",
                                "imageUrl": "string",
                                "thumbnail": "string",
                                "rate": 0,
                                "productId": None,
                                "examId": None,
                                "jobId": None,
                                "blogId": None,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """Update testimonial matching old Swagger format."""
        try:
            try:
                testimonial = Testimonial.objects.get(id=pk)
            except Testimonial.DoesNotExist:
                return create_error_response(
                    error_message=f'Testimonial with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Testimonial with ID "{pk}" not found.']}
                )
            
            serializer = TestimonialCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update testimonial
            testimonial.name = validated_data['name']
            testimonial.text = validated_data['text']
            testimonial.image_url = validated_data.get('imageUrl') or validated_data.get('thumbnail') or testimonial.image_url
            testimonial.rate = validated_data.get('rate', testimonial.rate)
            testimonial.locale = validated_data.get('locale', testimonial.locale)
            testimonial.save()
            
            # Return updated testimonial
            detail_serializer = TestimonialDetailSerializer(testimonial)
            return create_success_response(data=detail_serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating testimonial: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Testimonials'],
        operation_id='testimonials_destroy',
        summary='Delete testimonial',
        description='Deletes a testimonial by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Testimonial ID')
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Testimonial deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "name": "new test mon",
                                "text": "string",
                                "imageUrl": "string",
                                "thumbnail": "string",
                                "rate": 0,
                                "productId": None,
                                "examId": None,
                                "jobId": None,
                                "blogId": None,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, pk=None):
        """Delete testimonial matching old Swagger format."""
        try:
            try:
                testimonial = Testimonial.objects.get(id=pk)
            except Testimonial.DoesNotExist:
                return create_error_response(
                    error_message=f'Testimonial with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Testimonial with ID "{pk}" not found.']}
                )
            
            # Serialize before deletion
            serializer = TestimonialDetailSerializer(testimonial)
            testimonial_data = serializer.data
            
            # Delete testimonial
            testimonial.delete()
            
            return create_success_response(data=testimonial_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting testimonial: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Testimonials'],
    operation_id='testimonials_dapper',
    summary='Get testimonials (dapper)',
    description='Get testimonials in dapper context. Accepts optional id parameter.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Optional testimonial ID'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Testimonials data',
            examples=[
                OpenApiExample(
                    'Success Response (no ID)',
                    value={
                        "data": None,
                        "messages": [],
                        "succeeded": True
                    }
                ),
                OpenApiExample(
                    'Success Response (with ID)',
                    value={
                        "data": {
                            "id": 1,
                            "name": "new test mon",
                            "text": "string",
                            "imageUrl": "string",
                            "thumbnail": "string",
                            "rate": 0,
                            "productId": None,
                            "examId": None,
                            "jobId": None,
                            "blogId": None,
                            "locale": "string"
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class TestimonialsDapperView(APIView):
    """GET /api/v1/testimonials/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get testimonials in dapper context matching old Swagger format."""
        try:
            testimonial_id = request.query_params.get('id')
            
            if testimonial_id:
                try:
                    testimonial = Testimonial.objects.get(id=testimonial_id)
                    serializer = TestimonialDetailSerializer(testimonial)
                    return create_success_response(data=serializer.data, messages=[])
                except Testimonial.DoesNotExist:
                    return create_error_response(
                        error_message=f'Testimonial with ID "{testimonial_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Testimonial with ID "{testimonial_id}" not found.']}
                    )
            else:
                # No ID provided, return null
                return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
