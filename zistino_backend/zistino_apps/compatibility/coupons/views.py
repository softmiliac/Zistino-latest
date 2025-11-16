"""
Compatibility views for Coupons endpoints.
All endpoints will appear under "Coupons" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Coupons
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
import secrets
import string
from zistino_apps.users.permissions import IsManager

from zistino_apps.payments.models import Coupon
from zistino_apps.payments.serializers import CouponSerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    CouponSearchRequestSerializer,
    CouponCreateRequestSerializer,
    CouponCompatibilitySerializer,
    CouponDetailSerializer
)


@extend_schema(tags=['Coupons'])
class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing coupons.
    All endpoints will appear under "Coupons" folder in Swagger UI.
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all coupons."""
        return Coupon.objects.all()

    def get_permissions(self):
        """Admin-only for create/update/delete/search, IsAuthenticated for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'generate_key']:
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_create',
        summary='Create a new coupon',
        description='Creates a new coupon matching old Swagger format.',
        request=CouponCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create coupon',
                value={
                    'key': 'string',
                    'startDateTime': '2025-11-09T17:14:12.717Z',
                    'endDateTime': '2025-11-09T17:14:12.717Z',
                    'maxUseCount': 0,
                    'percent': 0,
                    'price': 0,
                    'userId': 'string',
                    'roleId': 'string',
                    'type': 0,
                    'limitationType': 0,
                    'userLimitationType': 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 1,
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
        """Create coupon matching old Swagger format. Returns coupon ID."""
        try:
            # Validate input using old Swagger format serializer
            input_serializer = CouponCreateRequestSerializer(data=request.data)
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
            # Calculate amount: if percent > 0, use percent; otherwise use price
            percent = validated_data.get('percent', 0)
            price = validated_data.get('price', 0)
            amount = percent if percent > 0 else price
            
            # Map type to status (0=inactive, 1=active)
            coupon_type = validated_data.get('type', 0)
            status_value = 1 if coupon_type == 1 else 0
            
            try:
                coupon = Coupon.objects.create(
                    key=validated_data.get('key'),
                    amount=amount,
                    status=status_value,
                    valid_from=validated_data.get('startDateTime'),
                    valid_to=validated_data.get('endDateTime'),
                    usage_limit=validated_data.get('maxUseCount') if validated_data.get('maxUseCount', 0) > 0 else None,
                    used_count=0
                )
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    if 'UNIQUE constraint' in error_detail or 'unique constraint' in error_detail.lower() or 'key' in error_detail.lower():
                        return create_error_response(
                            error_message=f'A coupon with key "{validated_data.get("key")}" already exists.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'key': [f'A coupon with key "{validated_data.get("key")}" already exists.']}
                        )
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'coupon': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while creating the coupon: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return just the coupon ID wrapped in standard response
            return create_success_response(data=coupon.id)  # 200 OK to match old Swagger
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_search',
        summary='Search Coupons using available Filters',
        description='Search Coupons using available Filters matching old Swagger format.',
        request=CouponSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search coupons',
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
                            'messages': ['string'],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 0,
                                    'key': 'string',
                                    'type': 0
                                }
                            ],
                            'currentPage': 0,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 0,
                            'hasPreviousPage': True,
                            'hasNextPage': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search coupons with pagination (admin) matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = CouponSearchRequestSerializer(data=request_data)
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
            
            # Build query
            qs = Coupon.objects.all()
            
            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(key__icontains=keyword.strip())
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by and any(order_by):  # If orderBy has non-empty values
                # Validate fields exist in Coupon model
                valid_fields = ['id', 'key', 'amount', 'status', 'valid_from', 'valid_to', 'usage_limit', 'used_count', 'created_at']
                order_fields = []
                invalid_fields = []
                
                for field in order_by:
                    if field and field.strip():
                        # Remove leading minus for validation
                        field_name = field.strip().lstrip('-')
                        # Map old Swagger field names to Django field names
                        field_mapping = {
                            'startDateTime': 'valid_from',
                            'endDateTime': 'valid_to',
                            'maxUseCount': 'usage_limit',
                            'createdAt': 'created_at',
                        }
                        django_field = field_mapping.get(field_name, field_name)
                        if django_field in valid_fields:
                            # Add minus back if it was there
                            if field.strip().startswith('-'):
                                order_fields.append(f'-{django_field}')
                            else:
                                order_fields.append(django_field)
                        else:
                            invalid_fields.append(field.strip())
                
                if invalid_fields:
                    return create_error_response(
                        error_message=f'Invalid orderBy fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'orderBy': [f'Invalid fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}']}
                    )
                
                if order_fields:
                    try:
                        qs = qs.order_by(*order_fields)
                    except Exception:
                        # If ordering fails, use default
                        qs = qs.order_by('-created_at')
                else:
                    qs = qs.order_by('-created_at')
            else:
                # Default ordering
                qs = qs.order_by('-created_at')
            
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
            
            # Serialize results using compatibility serializer (simplified format)
            item_serializer = CouponCompatibilitySerializer(items, many=True, context={'request': request})
            items_data = item_serializer.data
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 0 if empty, as per old Swagger example)
            response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 0)
            
            response_data = {
                'messages': [],  # Empty array for messages
                'succeeded': True,
                'data': items_data,
                'currentPage': effective_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': response_page_size,
                'hasPreviousPage': has_previous,
                'hasNextPage': has_next
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_retrieve',
        summary='Retrieve a coupon by ID',
        description='Retrieves a coupon by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Coupon ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'key': 'string',
                                'startDateTime': '2025-11-09T17:12:45.062',
                                'endDateTime': '2025-11-09T17:12:45.062',
                                'maxUseCount': 0,
                                'percent': 0,
                                'price': 0,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'roleId': None,
                                'type': 0,
                                'limitationType': 0,
                                'userLimitationType': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Coupon not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a coupon by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = CouponDetailSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data)
        except Coupon.DoesNotExist:
            return create_error_response(
                error_message=f'Coupon with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Coupon with ID "{kwargs.get("pk")}" not found.']}
            )

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_update',
        summary='Update a coupon by ID',
        description='Updates an existing coupon by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Coupon ID'
            )
        ],
        request=CouponCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'key': 'string',
                                'startDateTime': '2025-11-09T17:12:45.062',
                                'endDateTime': '2025-11-09T17:12:45.062',
                                'maxUseCount': 0,
                                'percent': 0,
                                'price': 0,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'roleId': None,
                                'type': 0,
                                'limitationType': 0,
                                'userLimitationType': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Coupon not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a coupon by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input using old Swagger format serializer
            input_serializer = CouponCreateRequestSerializer(data=request.data)
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
            # Calculate amount: if percent > 0, use percent; otherwise use price
            percent = validated_data.get('percent', 0)
            price = validated_data.get('price', 0)
            amount = percent if percent > 0 else price
            
            # Map type to status (0=inactive, 1=active)
            coupon_type = validated_data.get('type', 0)
            status_value = 1 if coupon_type == 1 else 0
            
            try:
                instance.key = validated_data.get('key', instance.key)
                instance.amount = amount
                instance.status = status_value
                instance.valid_from = validated_data.get('startDateTime', instance.valid_from)
                instance.valid_to = validated_data.get('endDateTime', instance.valid_to)
                instance.usage_limit = validated_data.get('maxUseCount') if validated_data.get('maxUseCount', 0) > 0 else None
                instance.save()
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    if 'UNIQUE constraint' in error_detail or 'unique constraint' in error_detail.lower() or 'key' in error_detail.lower():
                        return create_error_response(
                            error_message=f'A coupon with key "{validated_data.get("key")}" already exists.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'key': [f'A coupon with key "{validated_data.get("key")}" already exists.']}
                        )
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'coupon': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while updating the coupon: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return updated coupon in old Swagger format
            serializer = CouponDetailSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data)
        
        except Coupon.DoesNotExist:
            return create_error_response(
                error_message=f'Coupon with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Coupon with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_destroy',
        summary='Delete a coupon by ID',
        description='Deletes a coupon by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Coupon ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Coupon not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a coupon by ID matching old Swagger format. Returns coupon ID."""
        try:
            instance = self.get_object()
            coupon_id = instance.id
            instance.delete()  # Hard delete
            return create_success_response(data=coupon_id)
        except Coupon.DoesNotExist:
            return create_error_response(
                error_message=f'Coupon with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Coupon with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_dapper',
        summary='Get coupon (dapper context)',
        description='Get coupon in dapper context matching old Swagger format. Returns null if no id provided, or coupon data if id provided.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Coupon ID (optional)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Dapper context response',
                examples=[
                    OpenApiExample(
                        'Success response (no id)',
                        value={
                            'data': None,
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
        """Get coupon in dapper context matching old Swagger format. Returns null if no id provided, or coupon data if id provided."""
        coupon_id = request.query_params.get('id')
        
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                serializer = CouponDetailSerializer(coupon, context={'request': request})
                return create_success_response(data=serializer.data)
            except Coupon.DoesNotExist:
                return create_success_response(data=None)
        
        # If no id provided, return null as per old Swagger
        return create_success_response(data=None)

    @extend_schema(
        tags=['Coupons'],
        operation_id='coupons_generate_key',
        summary='Generate coupon key',
        description='Generates a new unique coupon key matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Generated coupon key',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': None,
                            'messages': ['XNNJWBBI'],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='generate-key', permission_classes=[IsAuthenticated, IsManager])
    def generate_key(self, request):
        """Generate a unique coupon key matching old Swagger format. Returns key in messages array."""
        # Generate a random alphanumeric key (8 characters)
        alphabet = string.ascii_uppercase + string.digits
        while True:
            key = ''.join(secrets.choice(alphabet) for _ in range(8))
            if not Coupon.objects.filter(key=key).exists():
                break
        
        return create_success_response(data=None, messages=[key])


# ============================================================================
# SEPARATE APIView CLASSES FOR CLIENT ENDPOINTS WITH PATH PARAMETERS
# ============================================================================

@extend_schema(
    tags=['Coupons'],
    operation_id='coupons_client_apply_on_basket',
    summary='Apply coupon on basket for client',
    description='Apply a coupon (identified by key) to the client\'s basket matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='key',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='Coupon key'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Coupon applied successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': {
                            'status': 1,
                            'amount': 0
                        },
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        ),
        400: {'description': 'Invalid coupon, expired, or usage limit reached'}
    }
)
class CouponClientApplyOnBasketView(APIView):
    """GET /api/v1/coupons/client/apply-on-basket/{key} - Apply coupon on basket for client"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, key):
        """Apply coupon on basket matching old Swagger format. Accepts any key and returns default response."""
        try:
            coupon = Coupon.objects.get(key=key, status=1)  # Active coupon only
            
            # Check if coupon is expired
            from django.utils import timezone
            if coupon.valid_to and coupon.valid_to < timezone.now():
                # Return default response even if expired (old Swagger behavior)
                return create_success_response(data={
                    'status': 1,
                    'amount': 0
                })
            
            # Check usage limit
            if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                # Return default response even if usage limit reached (old Swagger behavior)
                return create_success_response(data={
                    'status': 1,
                    'amount': 0
                })
            
            # Return coupon info in old Swagger format (actual basket application handled in baskets app)
            return create_success_response(data={
                'status': coupon.status,
                'amount': coupon.amount
            })
        except Coupon.DoesNotExist:
            # Return default response even if coupon doesn't exist (old Swagger behavior)
            return create_success_response(data={
                'status': 1,
                'amount': 0
            })

