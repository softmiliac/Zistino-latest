"""
Compatibility views for CouponUses endpoints.
CouponUses are represented by BasketDiscount model (tracks coupon usage).
All endpoints will appear under "CouponUses" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/CouponUses
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from zistino_apps.payments.models import BasketDiscount, Coupon
from zistino_apps.orders.models import Basket
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    CouponUseSerializer,
    CouponUseSearchRequestSerializer,
    CouponUseCreateRequestSerializer,
    CouponUseDetailSerializer
)


@extend_schema(tags=['CouponUses'])
class CouponUseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing coupon uses (BasketDiscount records).
    All endpoints will appear under "CouponUses" folder in Swagger UI.
    """
    queryset = BasketDiscount.objects.all()
    serializer_class = CouponUseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all coupon uses (BasketDiscount records)."""
        return BasketDiscount.objects.all().select_related('coupon', 'basket', 'basket__user').order_by('-created_at')

    def get_permissions(self):
        """Admin-only for all operations."""
        return [IsAuthenticated(), IsManager()]

    @extend_schema(
        tags=['CouponUses'],
        operation_id='couponuses_create',
        summary='Create a new coupon use',
        description='Creates a new coupon use matching old Swagger format.',
        request=CouponUseCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create coupon use',
                value={
                    'couponId': 0,
                    'userId': 'string',
                    'productId': 'string',
                    'orderId': 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon use created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 3,
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
        """Create coupon use matching old Swagger format. Returns coupon use ID."""
        try:
            # Validate input using old Swagger format serializer
            input_serializer = CouponUseCreateRequestSerializer(data=request.data)
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
            
            # Get coupon
            coupon_id = validated_data.get('couponId')
            try:
                coupon = Coupon.objects.get(id=coupon_id)
            except Coupon.DoesNotExist:
                return create_error_response(
                    error_message=f'Coupon with ID "{coupon_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'couponId': [f'Coupon with ID "{coupon_id}" not found.']}
                )
            
            # Get or create basket for user
            user_id = validated_data.get('userId')
            basket = None
            if user_id and user_id.strip() and user_id != 'string':
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    import uuid
                    user_uuid = uuid.UUID(user_id)
                    user = User.objects.get(id=user_uuid)
                    # Get or create basket for user
                    basket, created = Basket.objects.get_or_create(
                        user=user,
                        defaults={'is_empty': True}
                    )
                except (ValueError, TypeError, User.DoesNotExist):
                    # If user not found or invalid UUID, create without basket
                    pass
            
            # If no basket, we need to create one or return error
            # For now, if no valid user/basket, we'll create a placeholder
            if not basket:
                # Try to get authenticated user's basket
                if request.user.is_authenticated:
                    basket, created = Basket.objects.get_or_create(
                        user=request.user,
                        defaults={'is_empty': True}
                    )
                else:
                    return create_error_response(
                        error_message='User ID is required or user must be authenticated.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'userId': ['User ID is required or user must be authenticated.']}
                    )
            
            # Check if basket already has a discount
            if BasketDiscount.objects.filter(basket=basket).exists():
                return create_error_response(
                    error_message='Basket already has a coupon discount applied.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'basket': ['Basket already has a coupon discount applied.']}
                )
            
            try:
                # Create coupon use (BasketDiscount)
                coupon_use = BasketDiscount.objects.create(
                    coupon=coupon,
                    basket=basket,
                    amount=coupon.amount
                )
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    if 'UNIQUE constraint' in error_detail or 'unique constraint' in error_detail.lower():
                        return create_error_response(
                            error_message='This basket already has a coupon discount applied.',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'basket': ['This basket already has a coupon discount applied.']}
                        )
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'couponUse': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while creating the coupon use: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return just the coupon use ID wrapped in standard response
            return create_success_response(data=coupon_use.id)  # 200 OK to match old Swagger
        
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
        tags=['CouponUses'],
        operation_id='couponuses_search',
        summary='Search CouponUses using available Filters',
        description='Search CouponUses using available Filters matching old Swagger format.',
        request=CouponUseSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search coupon uses',
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
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search coupon uses with pagination matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = CouponUseSearchRequestSerializer(data=request_data)
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
            qs = BasketDiscount.objects.all().select_related('coupon', 'basket', 'basket__user').order_by('-created_at')

            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(coupon__key__icontains=keyword.strip()) |
                    Q(basket__user__phone_number__icontains=keyword.strip()) |
                    Q(basket__user__username__icontains=keyword.strip())
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by and any(order_by):  # If orderBy has non-empty values
                # Validate fields exist in BasketDiscount model
                valid_fields = ['id', 'amount', 'created_at', 'coupon__id', 'coupon__key', 'basket__id']
                order_fields = []
                invalid_fields = []
                
                for field in order_by:
                    if field and field.strip():
                        # Remove leading minus for validation
                        field_name = field.strip().lstrip('-')
                        # Map old Swagger field names to Django field names
                        field_mapping = {
                            'createdAt': 'created_at',
                            'couponId': 'coupon__id',
                            'userId': 'basket__user__id',
                        }
                        django_field = field_mapping.get(field_name, field_name)
                        if django_field in valid_fields or django_field.startswith('coupon__') or django_field.startswith('basket__'):
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
            
            # Serialize results
            item_serializer = CouponUseSerializer(items, many=True, context={'request': request})
            items_data = item_serializer.data
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 1 if empty, as per old Swagger example)
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
        tags=['CouponUses'],
        operation_id='couponuses_retrieve',
        summary='Retrieve a coupon use by ID',
        description='Retrieves a coupon use by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Coupon use ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon use details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 3,
                                'couponId': 1,
                                'couponKey': 'string',
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'userFullname': ' ',
                                'userEmail': None,
                                'userPhoneNumber': '09056761466',
                                'order': {
                                    'id': 3,
                                    'totalPrice': 0,
                                    'createOrderDate': '2024-03-13T10:16:42.55',
                                    'submitPriceDate': '2024-03-13T10:16:42.55',
                                    'sendToPostDate': None,
                                    'paymentTrackingCode': '-',
                                    'status': 2,
                                    'orderItems': [
                                        {
                                            'id': 6,
                                            'productId': '94860000-b419-c60d-7c6b-08dc431b3c4c',
                                            'productName': '1 تا 5 کیلوگرم',
                                            'productImage': '',
                                            'unitPrice': 45000,
                                            'unitDiscountPrice': 0,
                                            'itemCount': 1,
                                            'status': 0,
                                            'description': '15',
                                            'latitude': None,
                                            'longitude': None,
                                            'addressid': None,
                                            'city': None,
                                            'country': None,
                                            'rate': None,
                                            'storeId': None,
                                            'ressellerId': None
                                        }
                                    ]
                                }
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Coupon use not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a coupon use by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = CouponUseDetailSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data)
        except BasketDiscount.DoesNotExist:
            return create_error_response(
                error_message=f'Coupon use with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Coupon use with ID "{kwargs.get("pk")}" not found.']}
            )

    @extend_schema(
        tags=['CouponUses'],
        operation_id='couponuses_update',
        summary='Update a coupon use by ID',
        description='Updates an existing coupon use by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Coupon use ID'
            )
        ],
        request=CouponUseCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon use updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 3,
                                'couponId': 1,
                                'couponKey': 'string',
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'userFullname': ' ',
                                'userEmail': None,
                                'userPhoneNumber': '09056761466',
                                'order': {
                                    'id': 3,
                                    'totalPrice': 0,
                                    'createOrderDate': '2024-03-13T10:16:42.55',
                                    'submitPriceDate': '2024-03-13T10:16:42.55',
                                    'sendToPostDate': None,
                                    'paymentTrackingCode': '-',
                                    'status': 2,
                                    'orderItems': []
                                }
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Coupon use not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a coupon use by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input using old Swagger format serializer
            input_serializer = CouponUseCreateRequestSerializer(data=request.data)
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
            
            # Get coupon
            coupon_id = validated_data.get('couponId')
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    instance.coupon = coupon
                    instance.amount = coupon.amount
                except Coupon.DoesNotExist:
                    return create_error_response(
                        error_message=f'Coupon with ID "{coupon_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'couponId': [f'Coupon with ID "{coupon_id}" not found.']}
                    )
            
            # Get or update basket for user
            user_id = validated_data.get('userId')
            if user_id and user_id.strip() and user_id != 'string':
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    import uuid
                    user_uuid = uuid.UUID(user_id)
                    user = User.objects.get(id=user_uuid)
                    # Get or create basket for user
                    basket, created = Basket.objects.get_or_create(
                        user=user,
                        defaults={'is_empty': True}
                    )
                    instance.basket = basket
                except (ValueError, TypeError, User.DoesNotExist):
                    # If user not found or invalid UUID, keep existing basket
                    pass
            
            try:
                instance.save()
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'couponUse': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while updating the coupon use: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return updated coupon use in old Swagger format
            serializer = CouponUseDetailSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data)
        
        except BasketDiscount.DoesNotExist:
            return create_error_response(
                error_message=f'Coupon use with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Coupon use with ID "{kwargs.get("pk")}" not found.']}
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
        tags=['CouponUses'],
        operation_id='couponuses_destroy',
        summary='Delete a coupon use by ID',
        description='Deletes a coupon use by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Coupon use ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Coupon use deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 3,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Coupon use not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a coupon use by ID matching old Swagger format. Returns coupon use ID."""
        try:
            instance = self.get_object()
            coupon_use_id = instance.id
            instance.delete()  # Hard delete
            return create_success_response(data=coupon_use_id)
        except BasketDiscount.DoesNotExist:
            return create_error_response(
                error_message=f'Coupon use with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Coupon use with ID "{kwargs.get("pk")}" not found.']}
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

