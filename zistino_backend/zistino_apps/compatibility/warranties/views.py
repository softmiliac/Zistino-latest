"""
Views for Warranties compatibility layer.
Provides all 9 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from django.db.models import Q

from zistino_apps.products.models import Warranty, Product
from zistino_apps.products.serializers import WarrantySerializer, WarrantySearchRequestSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    WarrantyCompatibilitySerializer,
    WarrantyDetailSerializer,
    WarrantyCreateRequestSerializer
)


@extend_schema(tags=['Warranties'])
class WarrantiesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Warranties endpoints.
    Wraps the existing WarrantyViewSet functionality and adds compatibility endpoints.
    """
    queryset = Warranty.objects.all()
    serializer_class = WarrantySerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'searchwithdescription']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_list',
        summary='List all warranties',
    )
    def list(self, request, *args, **kwargs):
        """List all warranties."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_retrieve',
        summary='Retrieve a warranty by ID',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Warranty details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "name": "one year waran",
                                "imageUrl": "string",
                                "thumbnail": "string",
                                "description": "string",
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
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a warranty by ID matching old Swagger format."""
        try:
            warranty = self.get_object()
            serializer = WarrantyDetailSerializer(warranty)
            return create_success_response(data=serializer.data, messages=[])
        except Warranty.DoesNotExist:
            return create_error_response(
                error_message=f'Warranty with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Warranty with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_create',
        summary='Create a new warranty',
        request=WarrantyCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Warranty (default)',
                value={
                    "name": "string",
                    "imageUrl": "string",
                    "thumbnail": "string",
                    "description": "string",
                    "locale": "string"
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Warranty created successfully',
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
    def create(self, request, *args, **kwargs):
        """Create a new warranty matching old Swagger format."""
        try:
            serializer = WarrantyCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get or create a default product for warranty (warranties need a product)
            # For now, we'll use the first product or create a placeholder
            # TODO: This should be handled properly based on business logic
            default_product = Product.objects.first()
            if not default_product:
                return create_error_response(
                    error_message='No products available. Please create a product first.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'product': ['No products available. Please create a product first.']}
                )
            
            # Create warranty
            warranty = Warranty.objects.create(
                product=default_product,
                name=validated_data['name'],
                image_url=validated_data.get('imageUrl') or validated_data.get('thumbnail'),
                description=validated_data.get('description', ''),
                locale=validated_data.get('locale', '')
            )
            
            return create_success_response(data=warranty.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating warranty: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_update',
        summary='Update a warranty',
        request=WarrantyCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Warranty updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "name": "one year waran",
                                "imageUrl": "string",
                                "thumbnail": "string",
                                "description": "string",
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
    def update(self, request, *args, **kwargs):
        """Update a warranty matching old Swagger format."""
        try:
            warranty = self.get_object()
            serializer = WarrantyCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update warranty
            warranty.name = validated_data['name']
            warranty.image_url = validated_data.get('imageUrl') or validated_data.get('thumbnail') or warranty.image_url
            warranty.description = validated_data.get('description', warranty.description)
            warranty.locale = validated_data.get('locale', warranty.locale)
            warranty.save()
            
            # Return updated warranty
            detail_serializer = WarrantyDetailSerializer(warranty)
            return create_success_response(data=detail_serializer.data, messages=[])
        except Warranty.DoesNotExist:
            return create_error_response(
                error_message=f'Warranty with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Warranty with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating warranty: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_partial_update',
        summary='Partially update a warranty',
        request=WarrantySerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a warranty."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_destroy',
        summary='Delete a warranty',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Warranty deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "name": "one year waran",
                                "imageUrl": "string",
                                "thumbnail": "string",
                                "description": "string",
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
    def destroy(self, request, *args, **kwargs):
        """Delete a warranty matching old Swagger format."""
        try:
            warranty = self.get_object()
            
            # Serialize before deletion
            serializer = WarrantyDetailSerializer(warranty)
            warranty_data = serializer.data
            
            # Delete warranty
            warranty.delete()
            
            return create_success_response(data=warranty_data, messages=[])
        except Warranty.DoesNotExist:
            return create_error_response(
                error_message=f'Warranty with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Warranty with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting warranty: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_search',
        summary='Search Warranties using available Filters',
        request=WarrantySearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ]
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results with pagination',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "messages": [
                                "string"
                            ],
                            "succeeded": True,
                            "data": [
                                {
                                    "id": 0,
                                    "name": "string",
                                    "thumbnail": "string",
                                    "locale": "string"
                                }
                            ],
                            "currentPage": 0,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 0,
                            "hasPreviousPage": True,
                            "hasNextPage": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search warranties with pagination and filters matching old Swagger format."""
        try:
            # Get pagination parameters
            page_number = int(request.data.get('pageNumber') or 1)
            if page_number == 0:
                page_number = 1
            page_size = int(request.data.get('pageSize') or 20)
            if page_size == 0:
                page_size = 20
            keyword = (request.data.get('keyword') or '').strip()
            
            # Build query
            qs = Warranty.objects.all()
            
            # Apply keyword search
            if keyword:
                qs = qs.filter(
                    Q(name__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Handle orderBy if provided
            order_by = request.data.get('orderBy', [])
            if order_by and isinstance(order_by, list):
                # Map orderBy fields to model fields
                valid_order_by = []
                for field in order_by:
                    if field and isinstance(field, str):
                        # Map common fields
                        mapped_field = None
                        if field.lower() in ['name', 'id', 'locale']:
                            mapped_field = field.lower()
                        elif field.lower() == 'description':
                            mapped_field = 'description'
                        
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-id')
            else:
                qs = qs.order_by('-id')
            
            # Calculate pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
            current_page = page_number
            has_previous_page = current_page > 1
            has_next_page = current_page < total_pages
            
            # Get paginated items
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]
            
            # Serialize with compatibility serializer
            serializer = WarrantyCompatibilitySerializer(items, many=True)
            
            # Return in old Swagger format with pagination
            response_data = {
                'messages': ['string'] if serializer.data else [],
                'succeeded': True,
                'data': serializer.data,
                'currentPage': current_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
                'hasPreviousPage': has_previous_page,
                'hasNextPage': has_next_page
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching warranties: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Warranties'],
        operation_id='warranties_searchwithdescription',
        summary='Search Warranties using available Filters (with description)',
        request=WarrantySearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ]
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results with pagination',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "messages": [
                                "string"
                            ],
                            "succeeded": True,
                            "data": [
                                {
                                    "id": 0,
                                    "name": "string",
                                    "thumbnail": "string",
                                    "locale": "string"
                                }
                            ],
                            "currentPage": 0,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 0,
                            "hasPreviousPage": True,
                            "hasNextPage": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='searchwithdescription')
    def searchwithdescription(self, request):
        """Search warranties with description filter matching old Swagger format."""
        try:
            # Get pagination parameters
            page_number = int(request.data.get('pageNumber') or 1)
            if page_number == 0:
                page_number = 1
            page_size = int(request.data.get('pageSize') or 20)
            if page_size == 0:
                page_size = 20
            keyword = (request.data.get('keyword') or '').strip()
            
            # Build query
            qs = Warranty.objects.all()
            
            # Filter by description if keyword provided
            if keyword:
                qs = qs.filter(
                    Q(description__icontains=keyword) |
                    Q(name__icontains=keyword)
                )
            
            # Handle orderBy if provided
            order_by = request.data.get('orderBy', [])
            if order_by and isinstance(order_by, list):
                # Map orderBy fields to model fields
                valid_order_by = []
                for field in order_by:
                    if field and isinstance(field, str):
                        # Map common fields
                        mapped_field = None
                        if field.lower() in ['name', 'id', 'locale']:
                            mapped_field = field.lower()
                        elif field.lower() == 'description':
                            mapped_field = 'description'
                        
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-id')
            else:
                qs = qs.order_by('-id')
            
            # Calculate pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
            current_page = page_number
            has_previous_page = current_page > 1
            has_next_page = current_page < total_pages
            
            # Get paginated items
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]
            
            # Serialize with compatibility serializer
            serializer = WarrantyCompatibilitySerializer(items, many=True)
            
            # Return in old Swagger format with pagination
            response_data = {
                'messages': ['string'] if serializer.data else [],
                'succeeded': True,
                'data': serializer.data,
                'currentPage': current_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
                'hasPreviousPage': has_previous_page,
                'hasNextPage': has_next_page
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching warranties: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Warranties'],
    operation_id='warranties_dapper',
    summary='Get warranties (dapper)',
    description='Get warranties in dapper context. Accepts optional id parameter.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Optional warranty ID'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Warranties data',
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
                            "name": "one year waran",
                            "imageUrl": "string",
                            "thumbnail": "string",
                            "description": "string",
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
class WarrantiesDapperView(APIView):
    """GET /api/v1/warranties/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get warranties in dapper context matching old Swagger format."""
        try:
            warranty_id = request.query_params.get('id')
            
            if warranty_id:
                try:
                    warranty = Warranty.objects.get(id=warranty_id)
                    serializer = WarrantyDetailSerializer(warranty)
                    return create_success_response(data=serializer.data, messages=[])
                except Warranty.DoesNotExist:
                    return create_error_response(
                        error_message=f'Warranty with ID "{warranty_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Warranty with ID "{warranty_id}" not found.']}
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


@extend_schema(
    tags=['Warranties'],
    operation_id='warranties_all',
    summary='Get all warranties',
    description='Returns all warranties matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='List of all warranties',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "messages": [
                            "string"
                        ],
                        "succeeded": True,
                        "data": [
                            {
                                "id": 0,
                                "name": "string",
                                "thumbnail": "string",
                                "locale": "string"
                            }
                        ]
                    }
                ),
                OpenApiExample(
                    'Empty Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class WarrantiesAllView(APIView):
    """GET /api/v1/warranties/all"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all warranties matching old Swagger format."""
        try:
            warranties = Warranty.objects.all().order_by('-id')
            serializer = WarrantyCompatibilitySerializer(warranties, many=True)
            
            # Return in old Swagger format
            if serializer.data:
                return create_success_response(
                    data=serializer.data,
                    messages=["string"]  # Old Swagger shows messages array with "string"
                )
            else:
                return create_success_response(
                    data=[],
                    messages=[]
                )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(tags=['Warranties'])
class WarrantiesClientSearchWithDescriptionView(APIView):
    """POST /api/v1/warranties/client/searchwithdescription"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Client search warranties with description."""
        keyword = request.data.get('keyword', '').strip()
        
        qs = Warranty.objects.all()
        
        # Filter by description if keyword provided
        if keyword:
            qs = qs.filter(
                Q(description__icontains=keyword) |
                Q(name__icontains=keyword)
            )
        
        qs = qs.order_by('-id')
        
        return Response({
            'data': WarrantySerializer(qs, many=True).data,
        })

