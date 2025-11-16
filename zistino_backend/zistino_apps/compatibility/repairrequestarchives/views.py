"""
Views for RepairRequestArchives compatibility layer.
Provides all 5 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.compatibility.repairrequests.models import RepairRequest
from zistino_apps.compatibility.products.serializers import ProductCompatibilitySerializer

from .serializers import (
    RepairRequestArchiveSerializer,
    RepairRequestArchiveSearchRequestSerializer,
)


def serialize_repair_request_archive_response(repair_request, request=None):
    """Serialize repair request archive to match old Swagger response format with full product details."""
    # Serialize product with full details using ProductCompatibilitySerializer
    product_data = None
    if repair_request.product:
        serializer = ProductCompatibilitySerializer(repair_request.product, context={'request': request})
        product_data = serializer.data
    
    # Serialize repair request archive details (note: uses repairRequestArchiveDetails, not repairRequestDetails)
    details_data = []
    for detail in repair_request.repair_request_details.all():
        problem_data = None
        if detail.problem:
            problem_data = {
                'id': detail.problem.id,
                'title': detail.problem.title,
            }
        
        details_data.append({
            'price': float(detail.price),
            'startRepairDate': detail.start_repair_date.isoformat() if detail.start_repair_date else None,
            'endRepairDate': detail.end_repair_date.isoformat() if detail.end_repair_date else None,
            'repairRequestId': repair_request.id,
            'problem': problem_data,
            'isCanceled': detail.is_canceled,
            'cancelationDescription': detail.cancelation_description or None,
        })
    
    return {
        'id': repair_request.id,
        'duration': repair_request.duration,
        'totalPrice': float(repair_request.total_price),
        'trackingCode': repair_request.tracking_code or None,
        'steps': repair_request.steps,
        'deliveryInformation': repair_request.delivery_information or None,
        'note': repair_request.note or None,
        'createRequestDate': repair_request.created_at.isoformat(),
        'userId': str(repair_request.user.id) if repair_request.user else None,
        'product': product_data,
        'repairRequestArchiveDetails': details_data,  # Note: different field name
    }


@extend_schema(tags=['RepairRequestArchives'])
class RepairRequestArchivesViewSet(viewsets.ViewSet):
    """
    ViewSet for RepairRequestArchives endpoints.
    """
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_permissions(self):
        """Admin-only for all actions."""
        return [IsAuthenticated(), IsManager()]

    @extend_schema(
        tags=['RepairRequestArchives'],
        operation_id='repairrequestarchives_retrieve',
        summary='Retrieve a repair request archive by ID',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request archive details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "duration": 0,
                                "totalPrice": 0,
                                "trackingCode": "86437489",
                                "steps": 1,
                                "deliveryInformation": "string",
                                "note": "string",
                                "createRequestDate": "2025-11-11T09:40:39.6189029",
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "product": {
                                    "id": "94860000-b419-c60d-2b41-08dc425c06b1",
                                    "name": "شامپو کلیر",
                                    "categories": "[{\"id\":\"6\"}]",
                                    "isMaster": False,
                                    "masterImage": "/uploads/app/4012b8b383fc43bd808880d292d1deae.webp",
                                    "brandName": "recycle",
                                    "inStock": -1000,
                                    "isActive": True,
                                    "masterPrice": 530000,
                                    "locale": "en",
                                    "r1": 0,
                                    "r2": 0,
                                    "r3": 1,
                                    "r4": 1,
                                    "r5": 0
                                },
                                "repairRequestArchiveDetails": []
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, pk=None):
        """Retrieve a repair request archive by ID matching old Swagger format."""
        try:
            repair_request = RepairRequest.objects.filter(is_archived=True).prefetch_related(
                'repair_request_details__problem',
                'repair_request_statuses',
                'repair_request_documents'
            ).select_related('product', 'user').get(id=pk)
            
            response_data = serialize_repair_request_archive_response(repair_request, request)
            return create_success_response(data=response_data, messages=[])
        except RepairRequest.DoesNotExist:
            return create_error_response(
                error_message=f'Repair request archive with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Repair request archive with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair request archive: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequestArchives'],
        operation_id='repairrequestarchives_update',
        summary='Update a repair request archive',
        request=RepairRequestArchiveSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request archive updated successfully',
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
    def update(self, request, pk=None):
        """Update a repair request archive matching old Swagger format."""
        try:
            # Get archived repair request
            try:
                repair_request = RepairRequest.objects.filter(is_archived=True).get(id=pk)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request archive with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request archive with ID "{pk}" not found.']}
                )
            
            # Validate request data
            serializer = RepairRequestArchiveSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update fields if provided
            if 'userId' in validated_data and validated_data['userId']:
                try:
                    from uuid import UUID
                    user_id = UUID(validated_data['userId'])
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    repair_request.user = user
                except (ValueError, TypeError, User.DoesNotExist):
                    return create_error_response(
                        error_message='Invalid userId.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'userId': ['Invalid userId.']}
                    )
            
            if 'productId' in validated_data and validated_data['productId']:
                try:
                    from uuid import UUID
                    product_id = UUID(validated_data['productId'])
                    from zistino_apps.products.models import Product
                    product = Product.objects.get(id=product_id)
                    repair_request.product = product
                except (ValueError, TypeError, Product.DoesNotExist):
                    return create_error_response(
                        error_message='Invalid productId.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'productId': ['Invalid productId.']}
                    )
            
            if 'description' in validated_data and validated_data['description']:
                repair_request.note = validated_data['description']
            
            repair_request.save()
            
            return create_success_response(data=repair_request.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating repair request archive: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequestArchives'],
        operation_id='repairrequestarchives_destroy',
        summary='Delete a repair request archive',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request archive deleted successfully',
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
    def destroy(self, request, pk=None):
        """Delete a repair request archive matching old Swagger format."""
        try:
            # Get archived repair request
            try:
                repair_request = RepairRequest.objects.filter(is_archived=True).get(id=pk)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request archive with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request archive with ID "{pk}" not found.']}
                )
            
            repair_request_id = repair_request.id
            repair_request.delete()
            
            return create_success_response(data=repair_request_id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting repair request archive: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequestArchives'],
        operation_id='repairrequestarchives_search',
        summary='Search repair request archives using available filters',
        request=RepairRequestArchiveSearchRequestSerializer,
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
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search repair request archives matching old Swagger format."""
        try:
            serializer = RepairRequestArchiveSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Default pagination if not provided
            if page_number == 0:
                page_number = 1
            if page_size == 0:
                page_size = 20
            
            # Get keyword from request or advancedSearch
            keyword = validated_data.get('keyword', '').strip()
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and not keyword:
                keyword = (advanced_search.get('keyword') or '').strip()
            
            # Start with base queryset - only archived repair requests
            qs = RepairRequest.objects.filter(is_archived=True).prefetch_related(
                'repair_request_details__problem',
                'repair_request_statuses',
                'repair_request_documents'
            ).select_related('product', 'user')
            
            # Filter by userId
            user_id = validated_data.get('userId')
            if user_id and user_id.strip():
                try:
                    from uuid import UUID
                    UUID(user_id.strip())
                    qs = qs.filter(user_id=user_id.strip())
                except (ValueError, TypeError):
                    pass
            
            # Filter by productId
            product_id = validated_data.get('productId')
            if product_id and product_id.strip():
                try:
                    from uuid import UUID
                    UUID(product_id.strip())
                    qs = qs.filter(product_id=product_id.strip())
                except (ValueError, TypeError):
                    pass
            
            # Keyword search (search in multiple fields)
            if keyword:
                from django.db.models import Q
                qs = qs.filter(
                    Q(tracking_code__icontains=keyword) |
                    Q(full_name__icontains=keyword) |
                    Q(email__icontains=keyword) |
                    Q(phone_number__icontains=keyword) |
                    Q(note__icontains=keyword) |
                    Q(delivery_information__icontains=keyword) |
                    Q(address__icontains=keyword) |
                    Q(city__icontains=keyword) |
                    Q(zip_code__icontains=keyword) |
                    Q(company_name__icontains=keyword)
                )
            
            # Order by
            order_by = validated_data.get('orderBy', [])
            if order_by:
                order_fields = []
                for order_field in order_by:
                    if order_field and order_field.strip():
                        field_lower = order_field.lower().strip()
                        # Map common orderBy patterns
                        if 'date' in field_lower or 'created' in field_lower:
                            order_fields.append('-created_at')
                        elif 'price' in field_lower or 'total' in field_lower:
                            order_fields.append('-total_price')
                        elif 'status' in field_lower:
                            order_fields.append('status')
                        elif 'tracking' in field_lower or 'code' in field_lower:
                            order_fields.append('tracking_code')
                        elif 'name' in field_lower:
                            order_fields.append('full_name')
                if order_fields:
                    qs = qs.order_by(*order_fields)
            else:
                qs = qs.order_by('-created_at')
            
            # Get total count before pagination
            total = qs.count()
            
            # Apply pagination
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end] if page_size > 0 else qs
            
            # Serialize results using archive-specific serializer
            results = []
            for repair_request in items:
                data = serialize_repair_request_archive_response(repair_request, request)
                results.append(data)
            
            # Calculate pagination metadata
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            has_previous_page = page_number > 1
            has_next_page = page_number < total_pages if total_pages > 0 else False
            
            # Create response with pagination (messages should be null for search endpoint)
            response = create_success_response(
                data=results,
                pagination={
                    'currentPage': page_number,
                    'totalPages': total_pages,
                    'totalCount': total,
                    'pageSize': page_size,
                    'hasPreviousPage': has_previous_page,
                    'hasNextPage': has_next_page
                }
            )
            
            return response
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching repair request archives: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['RepairRequestArchives'],
    operation_id='repairrequestarchives_dapper',
    summary='Get repair request archives in dapper context',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.QUERY, required=False, description='Repair Request Archive ID (optional)')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Dapper response',
            examples=[
                OpenApiExample(
                    'Success Response (no id)',
                    value={
                        "data": None,
                        "messages": [],
                        "succeeded": True
                    }
                ),
                OpenApiExample(
                    'Success Response (with id)',
                    value={
                        "data": {
                            "id": 1,
                            "duration": 0,
                            "totalPrice": 0,
                            "trackingCode": "86437489",
                            "steps": 1,
                            "deliveryInformation": "string",
                            "note": "string",
                            "createRequestDate": "2025-11-11T09:40:39.6189029",
                            "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                            "product": {},
                            "repairRequestArchiveDetails": []
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RepairRequestArchivesDapperView(APIView):
    """GET /api/v1/repairrequestarchives/dapper"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get repair request archives in dapper context. Accepts optional id parameter."""
        try:
            archive_id = request.query_params.get('id')
            
            if archive_id:
                # Return specific archived repair request
                try:
                    repair_request = RepairRequest.objects.filter(is_archived=True).prefetch_related(
                        'repair_request_details__problem',
                        'repair_request_statuses',
                        'repair_request_documents'
                    ).select_related('product', 'user').get(id=archive_id)
                    
                    response_data = serialize_repair_request_archive_response(repair_request, request)
                    return create_success_response(data=response_data, messages=[])
                except RepairRequest.DoesNotExist:
                    return create_error_response(
                        error_message=f'Repair request archive with ID "{archive_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Repair request archive with ID "{archive_id}" not found.']}
                    )
            else:
                # Return null data as per old Swagger format
                return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['RepairRequestArchives'],
    operation_id='repairrequestarchives_getbyuserid',
    summary='Get repair request archives by user ID',
    parameters=[
        OpenApiParameter('userId', str, location=OpenApiParameter.QUERY, required=True, description='User ID to filter archives'),
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Repair request archives for user',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "id": 1,
                                "duration": 0,
                                "totalPrice": 0,
                                "trackingCode": "86437489",
                                "steps": 1,
                                "deliveryInformation": "string",
                                "note": "string",
                                "createRequestDate": "2025-11-11T09:40:39.6189029",
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "product": {
                                    "id": "94860000-b419-c60d-2b41-08dc425c06b1",
                                    "name": "شامپو کلیر",
                                    "categories": "[{\"id\":\"6\"}]",
                                    "isMaster": False,
                                    "masterImage": "/uploads/app/4012b8b383fc43bd808880d292d1deae.webp",
                                    "brandName": "recycle",
                                    "inStock": -1000,
                                    "isActive": True,
                                    "masterPrice": 530000,
                                    "locale": "en",
                                    "r1": 0,
                                    "r2": 0,
                                    "r3": 1,
                                    "r4": 1,
                                    "r5": 0
                                },
                                "repairRequestArchiveDetails": []
                            }
                        ],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RepairRequestArchivesGetByUserIdView(APIView):
    """GET /api/v1/repairrequestarchives/getbyuserid?userId={id}"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get repair request archives by user ID matching old Swagger format."""
        try:
            user_id = request.query_params.get('userId', '').strip()
            
            if not user_id:
                return create_error_response(
                    error_message='userId parameter is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userId': ['userId parameter is required.']}
                )
            
            # Validate UUID
            try:
                from uuid import UUID
                UUID(user_id)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message='Invalid userId format.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userId': ['Invalid userId format.']}
                )
            
            # Get archived repair requests for this user
            repair_requests = RepairRequest.objects.filter(
                is_archived=True,
                user_id=user_id
            ).prefetch_related(
                'repair_request_details__problem',
                'repair_request_statuses',
                'repair_request_documents'
            ).select_related('product', 'user').order_by('-created_at')
            
            # Serialize results
            results = []
            for repair_request in repair_requests:
                data = serialize_repair_request_archive_response(repair_request, request)
                results.append(data)
            
            return create_success_response(data=results, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair request archives: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

