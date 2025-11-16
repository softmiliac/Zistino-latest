"""
Compatibility views for Orders endpoints.
All endpoints will appear under "Orders" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Orders

Note: These endpoints wrap existing order views from orders app and add missing functionality.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse, OpenApiTypes
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from zistino_apps.orders.models import Order, OrderItem, Basket, BasketItem
from zistino_apps.orders.serializers import OrderSerializer, OrderItemSerializer
from zistino_apps.products.models import Product
from zistino_apps.users.models import Address
from zistino_apps.users.permissions import IsManager
from zistino_apps.deliveries.utils import find_zone_for_location
from zistino_apps.users.models import Zone
from django.contrib.auth import get_user_model

from .serializers import (
    OrderSearchRequestSerializer,
    OrderSearchUserRequestSerializer,
    OrderCheckInStockRequestSerializer,
    OrderHandyOrderRequestSerializer,
    OrderByDateRequestSerializer,
    OrderStatusUpdateRequestSerializer,
    OrderItemStatusUpdateRequestSerializer,
    OrderSearchStaticsRequestSerializer,
    OrderAdminGetByUserIdRequestSerializer,
    OrderMappingRequestSerializer,
    OrderCreateRequestSerializer,
    OrderCompatibilitySerializer,
    OrderAllSerializer,
)
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from drf_spectacular.utils import OpenApiExample, OpenApiResponse

User = get_user_model()


@extend_schema(tags=['Orders'])
class OrdersViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    All endpoints will appear under "Orders" folder in Swagger UI.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Use 'id' as lookup field
    lookup_url_kwarg = 'id'  # URL parameter name

    def get_queryset(self):
        """Return all orders for admin, user-scoped for regular users."""
        if self.request.user.is_staff or self.request.user.is_manager:
            return Order.objects.all().select_related('user').order_by('-created_at')
        return Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        """Admin can access all, regular users only their own."""
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]

    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_object(self):
        """Override to support both UUID and integer ID lookups."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        
        # Try UUID first (normal Django behavior)
        try:
            from uuid import UUID
            uuid_obj = UUID(lookup_value)
            order = Order.objects.get(id=uuid_obj)
            # Check permissions: regular users can only access their own orders
            if not (self.request.user.is_staff or self.request.user.is_manager):
                if order.user != self.request.user:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied('You do not have permission to access this order.')
            return order
        except (ValueError, TypeError, Order.DoesNotExist):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(lookup_value)
                # Find order whose UUID hash matches the integer ID
                # Use same hash calculation as OrderAllSerializer: [:8] and 10**9
                import hashlib
                orders = Order.objects.all()
                order = None
                for ord in orders:
                    # Calculate hash the same way as serializer
                    uuid_str = str(ord.id)
                    order_id_hash = int(hashlib.md5(uuid_str.encode()).hexdigest()[:8], 16) % (10 ** 9)
                    if order_id_hash == integer_id:
                        order = ord
                        break
                if not order:
                    from django.http import Http404
                    raise Http404(f'No Order matches the given query with ID: {lookup_value}')
                # Check permissions: regular users can only access their own orders
                if not (self.request.user.is_staff or self.request.user.is_manager):
                    if order.user != self.request.user:
                        from rest_framework.exceptions import PermissionDenied
                        raise PermissionDenied('You do not have permission to access this order.')
                return order
            except (ValueError, TypeError):
                # Not a valid integer either
                from django.http import Http404
                raise Http404(f'Invalid ID format: {lookup_value}. Expected UUID or integer.')

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_list',
        summary='List Orders',
        description='List all orders matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of orders',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 1,
                                    'totalPrice': 0,
                                    'createOrderDate': '2024-03-13T08:22:26.523',
                                    'paymentTrackingCode': '-',
                                    'status': 2,
                                    'userId': '85edc2ba-81db-4648-b008-816aa2ad1dd2',
                                    'phone1': '',
                                    'userFullname': ' ',
                                    'latitude': None,
                                    'longitude': None,
                                    'addressid': None,
                                    'city': None,
                                    'country': None,
                                    'description': None,
                                    'rate': None,
                                    'storeId': None,
                                    'ressellerId': None
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    def list(self, request, *args, **kwargs):
        """List orders matching old Swagger format."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = OrderCompatibilitySerializer(queryset, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_retrieve',
        summary='Retrieve Order',
        description='Retrieve an order by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Order ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "1528181888"'
            )
        ],
        responses={
            200: OrderCompatibilitySerializer,
            404: {'description': 'Order not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve order matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = OrderCompatibilitySerializer(instance, context=self.get_serializer_context())
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Order matches' in error_detail or 'Http404' in error_type:
                lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, 'unknown')
                return create_error_response(
                    error_message=f'Order with ID "{lookup_value}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Order with ID "{lookup_value}" not found.']}
                )
            
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return create_error_response(
                    error_message=str(e),
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'permission': [str(e)]}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_update',
        summary='Update Order',
        description='Update an order by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Order ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "1528181888"'
            )
        ],
        request=OrderCreateRequestSerializer,
        responses={
            200: OrderCompatibilitySerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Order not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update order matching old Swagger format."""
        try:
            instance = self.get_object()
            # Handle request wrapper if present
            request_data = request.data
            if isinstance(request_data, dict) and 'request' in request_data:
                request_data = request_data['request']
            
            # Validate input using old Swagger format serializer
            input_serializer = OrderCreateRequestSerializer(data=request_data, partial=False)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            # Update order fields (similar to create logic)
            validated_data = input_serializer.validated_data
            
            # Map status from integer to string
            status_map = {
                0: 'pending',
                1: 'confirmed',
                2: 'in_progress',
                3: 'completed',
                4: 'cancelled',
            }
            order_status = status_map.get(validated_data.get('status', instance.status), instance.status)
            
            # Update order fields
            instance.total_price = validated_data.get('totalPrice', instance.total_price)
            instance.address1 = validated_data.get('address1', instance.address1)
            instance.address2 = validated_data.get('address2', instance.address2) or ''
            instance.phone1 = validated_data.get('phone1', instance.phone1)
            instance.phone2 = validated_data.get('phone2', instance.phone2) or ''
            instance.status = order_status
            instance.post_state_number = validated_data.get('postStateNumber', instance.post_state_number) or ''
            instance.payment_tracking_code = validated_data.get('paymentTrackingCode', instance.payment_tracking_code) or ''
            instance.user_full_name = validated_data.get('userFullname', instance.user_full_name) or ''
            
            # Update dates if provided
            from django.utils.dateparse import parse_datetime
            if validated_data.get('createOrderDate'):
                create_order_date = validated_data.get('createOrderDate')
                if isinstance(create_order_date, str):
                    create_order_date = parse_datetime(create_order_date)
                instance.create_order_date = create_order_date
            
            if validated_data.get('submitPriceDate'):
                submit_price_date = validated_data.get('submitPriceDate')
                if isinstance(submit_price_date, str):
                    submit_price_date = parse_datetime(submit_price_date)
                instance.submit_price_date = submit_price_date
            
            if validated_data.get('sendToPostDate'):
                send_to_post_date = validated_data.get('sendToPostDate')
                if isinstance(send_to_post_date, str):
                    send_to_post_date = parse_datetime(send_to_post_date)
                instance.send_to_post_date = send_to_post_date
            
            # Update location if provided
            if validated_data.get('latitude') is not None:
                instance.latitude = validated_data.get('latitude')
            if validated_data.get('longitude') is not None:
                instance.longitude = validated_data.get('longitude')
            
            instance.save()
            
            # Update order items if provided
            order_items_data = validated_data.get('orderItems', [])
            if order_items_data:
                # Clear existing items and add new ones
                instance.order_items.all().delete()
                for item_data in order_items_data:
                    product_id = item_data.get('productId')
                    try:
                        product = Product.objects.get(id=product_id)
                        product_name = product.name
                    except Product.DoesNotExist:
                        continue
                    
                    unit_price = item_data.get('unitPrice', 0)
                    item_count = item_data.get('itemCount', 1)
                    total_item_price = unit_price * item_count
                    
                    OrderItem.objects.create(
                        order=instance,
                        product_name=product_name,
                        quantity=item_count,
                        unit_price=unit_price,
                        total_price=total_item_price,
                    )
            
            serializer = OrderCompatibilitySerializer(instance, context=self.get_serializer_context())
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Order matches' in error_detail or 'Http404' in error_type:
                lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, 'unknown')
                return create_error_response(
                    error_message=f'Order with ID "{lookup_value}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Order with ID "{lookup_value}" not found.']}
                )
            
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return create_error_response(
                    error_message=str(e),
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'permission': [str(e)]}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_partial_update',
        summary='Partially Update Order',
        description='Partially update an order by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Order ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "1528181888"'
            )
        ],
        request=OrderCreateRequestSerializer,
        responses={
            200: OrderCompatibilitySerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Order not found'}
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update order matching old Swagger format."""
        try:
            instance = self.get_object()
            # Handle request wrapper if present
            request_data = request.data
            if isinstance(request_data, dict) and 'request' in request_data:
                request_data = request_data['request']
            
            # Validate input using old Swagger format serializer (partial=True)
            input_serializer = OrderCreateRequestSerializer(data=request_data, partial=True)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            # Update only provided fields
            validated_data = input_serializer.validated_data
            
            # Map status from integer to string if provided
            if 'status' in validated_data:
                status_map = {
                    0: 'pending',
                    1: 'confirmed',
                    2: 'in_progress',
                    3: 'completed',
                    4: 'cancelled',
                }
                instance.status = status_map.get(validated_data.get('status'), instance.status)
            
            # Update fields if provided
            if 'totalPrice' in validated_data:
                instance.total_price = validated_data.get('totalPrice')
            if 'address1' in validated_data:
                instance.address1 = validated_data.get('address1')
            if 'address2' in validated_data:
                instance.address2 = validated_data.get('address2') or ''
            if 'phone1' in validated_data:
                instance.phone1 = validated_data.get('phone1')
            if 'phone2' in validated_data:
                instance.phone2 = validated_data.get('phone2') or ''
            if 'postStateNumber' in validated_data:
                instance.post_state_number = validated_data.get('postStateNumber') or ''
            if 'paymentTrackingCode' in validated_data:
                instance.payment_tracking_code = validated_data.get('paymentTrackingCode') or ''
            if 'userFullname' in validated_data:
                instance.user_full_name = validated_data.get('userFullname') or ''
            
            # Update dates if provided
            from django.utils.dateparse import parse_datetime
            if validated_data.get('createOrderDate'):
                create_order_date = validated_data.get('createOrderDate')
                if isinstance(create_order_date, str):
                    create_order_date = parse_datetime(create_order_date)
                instance.create_order_date = create_order_date
            
            if validated_data.get('submitPriceDate'):
                submit_price_date = validated_data.get('submitPriceDate')
                if isinstance(submit_price_date, str):
                    submit_price_date = parse_datetime(submit_price_date)
                instance.submit_price_date = submit_price_date
            
            if validated_data.get('sendToPostDate'):
                send_to_post_date = validated_data.get('sendToPostDate')
                if isinstance(send_to_post_date, str):
                    send_to_post_date = parse_datetime(send_to_post_date)
                instance.send_to_post_date = send_to_post_date
            
            # Update location if provided
            if 'latitude' in validated_data:
                instance.latitude = validated_data.get('latitude')
            if 'longitude' in validated_data:
                instance.longitude = validated_data.get('longitude')
            
            instance.save()
            
            # Update order items if provided
            if 'orderItems' in validated_data:
                order_items_data = validated_data.get('orderItems', [])
                if order_items_data:
                    # Clear existing items and add new ones
                    instance.order_items.all().delete()
                    for item_data in order_items_data:
                        product_id = item_data.get('productId')
                        try:
                            product = Product.objects.get(id=product_id)
                            product_name = product.name
                        except Product.DoesNotExist:
                            continue
                        
                        unit_price = item_data.get('unitPrice', 0)
                        item_count = item_data.get('itemCount', 1)
                        total_item_price = unit_price * item_count
                        
                        OrderItem.objects.create(
                            order=instance,
                            product_name=product_name,
                            quantity=item_count,
                            unit_price=unit_price,
                            total_price=total_item_price,
                        )
            
            serializer = OrderCompatibilitySerializer(instance, context=self.get_serializer_context())
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Order matches' in error_detail or 'Http404' in error_type:
                lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, 'unknown')
                return create_error_response(
                    error_message=f'Order with ID "{lookup_value}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Order with ID "{lookup_value}" not found.']}
                )
            
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return create_error_response(
                    error_message=str(e),
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'permission': [str(e)]}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_destroy',
        summary='Delete Order',
        description='Delete an order by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Order ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "1528181888"'
            )
        ],
        responses={
            200: {'description': 'Order deleted successfully'},
            404: {'description': 'Order not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete order matching old Swagger format."""
        try:
            instance = self.get_object()
            instance.delete()
            return create_success_response(data={'message': 'Order deleted successfully'}, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Order matches' in error_detail or 'Http404' in error_type:
                lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, 'unknown')
                return create_error_response(
                    error_message=f'Order with ID "{lookup_value}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Order with ID "{lookup_value}" not found.']}
                )
            
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return create_error_response(
                    error_message=str(e),
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'permission': [str(e)]}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_create',
        summary='Create Order',
        description='Create a new order matching old Swagger format.',
        request=OrderCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create order',
                value={
                    'totalPrice': 120,
                    'address1': 'adasdf',
                    'address2': 'string',
                    'phone1': '123',
                    'phone2': 'string',
                    'createOrderDate': '2025-11-08T13:20:19.417Z',
                    'submitPriceDate': '2025-11-08T13:20:19.417Z',
                    'sendToPostDate': '2025-11-08T13:20:19.417Z',
                    'postStateNumber': 'string',
                    'paymentTrackingCode': 'string',
                    'status': 0,
                    'couponId': 0,
                    'couponKey': 'string',
                    'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'userFullname': 'nabi',
                    'latitude': 10,
                    'longitude': 20,
                    'addressid': 0,
                    'city': 'string',
                    'country': 'string',
                    'description': 'string',
                    'rate': 0,
                    'storeId': 0,
                    'ressellerId': '1',
                    'orderItems': [
                        {
                            'productId': '94860000-b419-c60d-2b41-08dc425c06b1',
                            'unitPrice': 0,
                            'unitDiscountPrice': 0,
                            'itemCount': 0,
                            'status': 0,
                            'description': 'string'
                        }
                    ]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Order created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 'order-uuid-here',
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'User or Product not found'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create order matching old Swagger format."""
        # Handle request wrapper if present (old Swagger might wrap data in "request" field)
        request_data = request.data
        if isinstance(request_data, dict) and 'request' in request_data:
            request_data = request_data['request']
        
        # Validate input using old Swagger format serializer
        input_serializer = OrderCreateRequestSerializer(data=request_data)
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
        user_id = validated_data.get('userId')
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{user_id}" does not exist.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{user_id}" not found.']}
            )
        
        # Map status from integer to string
        status_map = {
            0: 'pending',
            1: 'confirmed',
            2: 'in_progress',
            3: 'completed',
            4: 'cancelled',
        }
        order_status = status_map.get(validated_data.get('status', 0), 'pending')
        
        # Parse dates
        from django.utils.dateparse import parse_datetime
        create_order_date = validated_data.get('createOrderDate')
        if create_order_date:
            if isinstance(create_order_date, str):
                create_order_date = parse_datetime(create_order_date)
        
        submit_price_date = validated_data.get('submitPriceDate')
        if submit_price_date:
            if isinstance(submit_price_date, str):
                submit_price_date = parse_datetime(submit_price_date)
        
        send_to_post_date = validated_data.get('sendToPostDate')
        if send_to_post_date:
            if isinstance(send_to_post_date, str):
                send_to_post_date = parse_datetime(send_to_post_date)
        
        # Handle addressid - if provided and not 0, fetch address and use its fields
        addressid = validated_data.get('addressid', 0)
        address1 = validated_data.get('address1', '')
        address2 = validated_data.get('address2') or ''
        phone1 = validated_data.get('phone1', '')
        phone2 = validated_data.get('phone2') or ''
        latitude = validated_data.get('latitude')
        longitude = validated_data.get('longitude')
        city = validated_data.get('city') or ''
        country = validated_data.get('country') or ''
        
        # If addressid is provided and is not 0, try to fetch the address
        if addressid and addressid != 0:
            try:
                address = Address.objects.get(id=addressid, user=user)
                # Use address fields from saved address, but allow request fields to override
                address1 = address1 or address.address or ''
                address2 = address2 or ''
                phone1 = phone1 or address.phone_number or ''
                phone2 = phone2 or ''
                latitude = latitude if latitude is not None else address.latitude
                longitude = longitude if longitude is not None else address.longitude
                city = city or address.city or ''
                country = country or address.country or ''
            except Address.DoesNotExist:
                # If address not found, just use request fields (don't fail)
                pass
        
        # Create order
        order_data = {
            'user': user,
            'total_price': validated_data.get('totalPrice', 0),
            'status': order_status,
            'address1': address1,
            'address2': address2,
            'phone1': phone1,
            'phone2': phone2,
            'create_order_date': create_order_date or timezone.now(),
            'submit_price_date': submit_price_date,
            'send_to_post_date': send_to_post_date,
            'post_state_number': validated_data.get('postStateNumber') or '',
            'payment_tracking_code': validated_data.get('paymentTrackingCode') or '',
            'user_full_name': validated_data.get('userFullname') or '',
            'user_phone_number': phone1,
            'latitude': latitude,
            'longitude': longitude,
        }
        
        order = Order.objects.create(**order_data)
        
        # Create order items
        order_items_data = validated_data.get('orderItems', [])
        for item_data in order_items_data:
            product_id = item_data.get('productId')
            
            # Get product to get product name
            try:
                product = Product.objects.get(id=product_id)
                product_name = product.name
            except Product.DoesNotExist:
                return create_error_response(
                    error_message=f'Product with ID "{product_id}" does not exist.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'orderItems': [f'Product with ID "{product_id}" not found.']}
                )
            
            unit_price = item_data.get('unitPrice', 0)
            item_count = item_data.get('itemCount', 1)
            total_item_price = unit_price * item_count
            
            OrderItem.objects.create(
                order=order,
                product_name=product_name,
                quantity=item_count,
                unit_price=unit_price,
                total_price=total_item_price,
            )
        
        # Return order ID wrapped in standard response
        return create_success_response(data=str(order.id))  # 200 OK to match old Swagger

    # ============================================================================
    # SEARCH ENDPOINTS
    # ============================================================================

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_search',
        summary='Search Orders',
        description='Search orders using available filters (Admin).',
        request=OrderSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search orders',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'List of orders',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search orders with pagination and filters matching old Swagger format."""
        serializer = OrderSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        page_number = validated_data.get('pageNumber', 0) or 1
        page_size = validated_data.get('pageSize', 0) or 20
        keyword = (validated_data.get('keyword') or '').strip()
        status_filter = validated_data.get('status')
        user_id = validated_data.get('userId')
        product_id = validated_data.get('productId')
        category_id = validated_data.get('categoryId')
        resseller_id = validated_data.get('ressellerId')
        
        # Get keyword from advancedSearch if not in main keyword
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and not keyword:
            keyword = (advanced_search.get('keyword') or '').strip()

        qs = Order.objects.all().select_related('user').prefetch_related('order_items').order_by('-created_at')

        # Filter by status (integer to string mapping)
        if status_filter is not None:
            status_map = {0: 'pending', 1: 'confirmed', 2: 'in_progress', 3: 'completed', 4: 'cancelled'}
            status_str = status_map.get(status_filter)
            if status_str:
                qs = qs.filter(status=status_str)

        # Filter by user ID
        if user_id:
            try:
                from uuid import UUID
                UUID(user_id)
                qs = qs.filter(user_id=user_id)
            except (ValueError, TypeError):
                pass

        # Filter by category ID (through order items -> product -> category)
        if category_id and category_id.strip():
            try:
                from uuid import UUID
                from zistino_apps.products.models import Category
                # Try as UUID first
                try:
                    uuid_obj = UUID(category_id.strip())
                    category = Category.objects.filter(id=uuid_obj).first()
                    if category:
                        # Find products in this category
                        products = Product.objects.filter(category=category)
                        product_names = products.values_list('name', flat=True)
                        # Filter orders that have items with these product names
                        qs = qs.filter(order_items__product_name__in=product_names).distinct()
                except (ValueError, TypeError):
                    # Try as integer (hash lookup)
                    try:
                        integer_id = int(category_id.strip())
                        import hashlib
                        categories = Category.objects.all()
                        category = None
                        for cat in categories:
                            uuid_str = str(cat.id)
                            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                            hash_int = int(hash_obj.hexdigest(), 16)
                            hash_id = hash_int % 2147483647
                            if hash_id == integer_id:
                                category = cat
                                break
                        if category:
                            products = Product.objects.filter(category=category)
                            product_names = products.values_list('name', flat=True)
                            qs = qs.filter(order_items__product_name__in=product_names).distinct()
                    except (ValueError, TypeError):
                        pass
            except Exception:
                pass

        # Filter by product ID (through order items)
        if product_id:
            try:
                from uuid import UUID
                UUID(product_id)
                product = Product.objects.filter(id=product_id).first()
                if product:
                    qs = qs.filter(order_items__product_name=product.name).distinct()
            except (ValueError, TypeError):
                pass

        # Filter by reseller ID
        if resseller_id:
            try:
                from uuid import UUID
                UUID(resseller_id)
                qs = qs.filter(resseller_id=resseller_id)
            except (ValueError, TypeError):
                pass

        # Filter by keyword
        if keyword:
            qs = qs.filter(
                Q(user_full_name__icontains=keyword) |
                Q(user_phone_number__icontains=keyword) |
                Q(address1__icontains=keyword) |
                Q(address2__icontains=keyword) |
                Q(phone1__icontains=keyword) |
                Q(phone2__icontains=keyword) |
                Q(post_state_number__icontains=keyword) |
                Q(payment_tracking_code__icontains=keyword) |
                Q(order_items__product_name__icontains=keyword)
            ).distinct()

        # Handle orderBy
        order_by = validated_data.get('orderBy', [])
        if order_by:
            # Map orderBy strings to Django order_by
            order_fields = []
            for order_field in order_by:
                if order_field and order_field.strip():
                    # Handle common orderBy patterns
                    if 'date' in order_field.lower() or 'created' in order_field.lower():
                        order_fields.append('-created_at')
                    elif 'price' in order_field.lower() or 'total' in order_field.lower():
                        order_fields.append('-total_price')
                    elif 'status' in order_field.lower():
                        order_fields.append('status')
            if order_fields:
                qs = qs.order_by(*order_fields)
        else:
            qs = qs.order_by('-created_at')

        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end] if page_size > 0 else qs

        serializer = OrderCompatibilitySerializer(items, many=True, context=self.get_serializer_context())
        response_data = create_success_response(data=serializer.data)
        # Add pagination fields
        response_data.data['currentPage'] = page_number
        response_data.data['totalPages'] = (total + page_size - 1) // page_size if page_size > 0 else 0
        response_data.data['totalCount'] = total
        response_data.data['pageSize'] = page_size
        response_data.data['hasPreviousPage'] = page_number > 1
        response_data.data['hasNextPage'] = page_number < (total + page_size - 1) // page_size if page_size > 0 else 0
        # Ensure messages is an array
        if response_data.data.get('messages') is None:
            response_data.data['messages'] = []
        return response_data

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_searchsp',
        summary='Search Orders (SP)',
        description='Search orders using stored procedure-like filters (Admin).',
        request=OrderSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search orders SP',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'List of orders',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='searchsp')
    def searchsp(self, request):
        """Search orders with pagination and status filter (same as search)."""
        return self.search(request)

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_searchuser',
        summary='Search Orders by User',
        description='Search orders filtered by user ID (Admin).',
        request=OrderSearchUserRequestSerializer,
        examples=[
            OpenApiExample(
                'Search orders by user',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'List of orders',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='searchuser')
    def searchuser(self, request):
        """Search orders by user ID matching old Swagger format."""
        return self.search(request)

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_searchstatics',
        summary='Search Order Statistics',
        description='Search orders with statistics (Admin).',
        request=OrderSearchStaticsRequestSerializer,
        examples=[
            OpenApiExample(
                'Search order statistics',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'Order statistics',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False,
                        'stats': {
                            'totalOrders': 0,
                            'totalRevenue': 0,
                            'averageOrderValue': 0
                        }
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='searchstatics')
    def searchstatics(self, request):
        """Search orders with statistics matching old Swagger format."""
        serializer = OrderSearchStaticsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        page_number = validated_data.get('pageNumber', 0) or 1
        page_size = validated_data.get('pageSize', 0) or 20
        keyword = (validated_data.get('keyword') or '').strip()
        status_filter = validated_data.get('status')
        user_id = validated_data.get('userId')
        product_id = validated_data.get('productId')
        category_id = validated_data.get('categoryId')
        resseller_id = validated_data.get('ressellerId')
        
        # Get keyword from advancedSearch if not in main keyword
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and not keyword:
            keyword = (advanced_search.get('keyword') or '').strip()

        qs = Order.objects.all().select_related('user').prefetch_related('order_items').order_by('-created_at')

        # Filter by status (integer to string mapping)
        if status_filter is not None:
            status_map = {0: 'pending', 1: 'confirmed', 2: 'in_progress', 3: 'completed', 4: 'cancelled'}
            status_str = status_map.get(status_filter)
            if status_str:
                qs = qs.filter(status=status_str)

        # Filter by user ID
        if user_id:
            try:
                from uuid import UUID
                UUID(user_id)
                qs = qs.filter(user_id=user_id)
            except (ValueError, TypeError):
                pass

        # Filter by category ID (through order items -> product -> category)
        if category_id and category_id.strip():
            try:
                from uuid import UUID
                from zistino_apps.products.models import Category
                # Try as UUID first
                try:
                    uuid_obj = UUID(category_id.strip())
                    category = Category.objects.filter(id=uuid_obj).first()
                    if category:
                        # Find products in this category
                        products = Product.objects.filter(category=category)
                        product_names = products.values_list('name', flat=True)
                        # Filter orders that have items with these product names
                        qs = qs.filter(order_items__product_name__in=product_names).distinct()
                except (ValueError, TypeError):
                    # Try as integer (hash lookup)
                    try:
                        integer_id = int(category_id.strip())
                        import hashlib
                        categories = Category.objects.all()
                        category = None
                        for cat in categories:
                            uuid_str = str(cat.id)
                            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                            hash_int = int(hash_obj.hexdigest(), 16)
                            hash_id = hash_int % 2147483647
                            if hash_id == integer_id:
                                category = cat
                                break
                        if category:
                            products = Product.objects.filter(category=category)
                            product_names = products.values_list('name', flat=True)
                            qs = qs.filter(order_items__product_name__in=product_names).distinct()
                    except (ValueError, TypeError):
                        pass
            except Exception:
                pass

        # Filter by product ID (through order items)
        if product_id:
            try:
                from uuid import UUID
                UUID(product_id)
                product = Product.objects.filter(id=product_id).first()
                if product:
                    qs = qs.filter(order_items__product_name=product.name).distinct()
            except (ValueError, TypeError):
                pass

        # Filter by reseller ID
        if resseller_id:
            try:
                from uuid import UUID
                UUID(resseller_id)
                qs = qs.filter(resseller_id=resseller_id)
            except (ValueError, TypeError):
                pass

        # Filter by keyword
        if keyword:
            qs = qs.filter(
                Q(user_full_name__icontains=keyword) |
                Q(user_phone_number__icontains=keyword) |
                Q(address1__icontains=keyword) |
                Q(address2__icontains=keyword) |
                Q(phone1__icontains=keyword) |
                Q(phone2__icontains=keyword) |
                Q(post_state_number__icontains=keyword) |
                Q(payment_tracking_code__icontains=keyword) |
                Q(order_items__product_name__icontains=keyword)
            ).distinct()

        # Handle orderBy
        order_by = validated_data.get('orderBy', [])
        if order_by:
            order_fields = []
            for order_field in order_by:
                if order_field and order_field.strip():
                    if 'date' in order_field.lower() or 'created' in order_field.lower():
                        order_fields.append('-created_at')
                    elif 'price' in order_field.lower() or 'total' in order_field.lower():
                        order_fields.append('-total_price')
                    elif 'status' in order_field.lower():
                        order_fields.append('status')
            if order_fields:
                qs = qs.order_by(*order_fields)
        else:
            qs = qs.order_by('-created_at')

        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end] if page_size > 0 else qs

        # Calculate statistics
        stats = {
            'totalOrders': total,
            'totalRevenue': int(qs.aggregate(Sum('total_price'))['total_price__sum'] or 0),
            'averageOrderValue': int(qs.aggregate(Avg('total_price'))['total_price__avg'] or 0)
        }

        serializer = OrderCompatibilitySerializer(items, many=True, context=self.get_serializer_context())
        response_data = create_success_response(data=serializer.data)
        # Add pagination fields
        response_data.data['currentPage'] = page_number
        response_data.data['totalPages'] = (total + page_size - 1) // page_size if page_size > 0 else 0
        response_data.data['totalCount'] = total
        response_data.data['pageSize'] = page_size
        response_data.data['hasPreviousPage'] = page_number > 1
        response_data.data['hasNextPage'] = page_number < (total + page_size - 1) // page_size if page_size > 0 else 0
        response_data.data['stats'] = stats
        # Ensure messages is an array
        if response_data.data.get('messages') is None:
            response_data.data['messages'] = []
        return response_data

    # ============================================================================
    # CLIENT ENDPOINTS
    # ============================================================================

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_client_search',
        summary='Client Search Orders',
        description='Get Orders Of currently logged in user.',
        request=OrderSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Client search orders',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'List of user orders',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='client/search', permission_classes=[IsAuthenticated])
    def client_search(self, request):
        """Search orders for the authenticated user matching old Swagger format."""
        serializer = OrderSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        page_number = validated_data.get('pageNumber', 0) or 1
        page_size = validated_data.get('pageSize', 0) or 20
        keyword = (validated_data.get('keyword') or '').strip()
        status_filter = validated_data.get('status')
        product_id = validated_data.get('productId')
        category_id = validated_data.get('categoryId')
        
        # Get keyword from advancedSearch if not in main keyword
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and not keyword:
            keyword = (advanced_search.get('keyword') or '').strip()

        qs = Order.objects.filter(user=request.user).select_related('user').prefetch_related('order_items').order_by('-created_at')

        # Filter by status (integer to string mapping)
        if status_filter is not None:
            status_map = {0: 'pending', 1: 'confirmed', 2: 'in_progress', 3: 'completed', 4: 'cancelled'}
            status_str = status_map.get(status_filter)
            if status_str:
                qs = qs.filter(status=status_str)

        # Filter by category ID (through order items -> product -> category)
        if category_id and category_id.strip():
            try:
                from uuid import UUID
                from zistino_apps.products.models import Category
                # Try as UUID first
                try:
                    uuid_obj = UUID(category_id.strip())
                    category = Category.objects.filter(id=uuid_obj).first()
                    if category:
                        # Find products in this category
                        products = Product.objects.filter(category=category)
                        product_names = products.values_list('name', flat=True)
                        # Filter orders that have items with these product names
                        qs = qs.filter(order_items__product_name__in=product_names).distinct()
                except (ValueError, TypeError):
                    # Try as integer (hash lookup)
                    try:
                        integer_id = int(category_id.strip())
                        import hashlib
                        categories = Category.objects.all()
                        category = None
                        for cat in categories:
                            uuid_str = str(cat.id)
                            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                            hash_int = int(hash_obj.hexdigest(), 16)
                            hash_id = hash_int % 2147483647
                            if hash_id == integer_id:
                                category = cat
                                break
                        if category:
                            products = Product.objects.filter(category=category)
                            product_names = products.values_list('name', flat=True)
                            qs = qs.filter(order_items__product_name__in=product_names).distinct()
                    except (ValueError, TypeError):
                        pass
            except Exception:
                pass

        # Filter by product ID (through order items)
        if product_id:
            try:
                from uuid import UUID
                UUID(product_id)
                product = Product.objects.filter(id=product_id).first()
                if product:
                    qs = qs.filter(order_items__product_name=product.name).distinct()
            except (ValueError, TypeError):
                pass

        # Filter by keyword
        if keyword:
            qs = qs.filter(
                Q(user_full_name__icontains=keyword) |
                Q(user_phone_number__icontains=keyword) |
                Q(address1__icontains=keyword) |
                Q(address2__icontains=keyword) |
                Q(phone1__icontains=keyword) |
                Q(phone2__icontains=keyword) |
                Q(post_state_number__icontains=keyword) |
                Q(payment_tracking_code__icontains=keyword) |
                Q(order_items__product_name__icontains=keyword)
            ).distinct()

        # Handle orderBy
        order_by = validated_data.get('orderBy', [])
        if order_by:
            order_fields = []
            for order_field in order_by:
                if order_field and order_field.strip():
                    if 'date' in order_field.lower() or 'created' in order_field.lower():
                        order_fields.append('-created_at')
                    elif 'price' in order_field.lower() or 'total' in order_field.lower():
                        order_fields.append('-total_price')
                    elif 'status' in order_field.lower():
                        order_fields.append('status')
            if order_fields:
                qs = qs.order_by(*order_fields)
        else:
            qs = qs.order_by('-created_at')

        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end] if page_size > 0 else qs

        serializer = OrderCompatibilitySerializer(items, many=True, context=self.get_serializer_context())
        response_data = create_success_response(data=serializer.data)
        # Add pagination fields
        response_data.data['currentPage'] = page_number
        response_data.data['totalPages'] = (total + page_size - 1) // page_size if page_size > 0 else 0
        response_data.data['totalCount'] = total
        response_data.data['pageSize'] = page_size
        response_data.data['hasPreviousPage'] = page_number > 1
        response_data.data['hasNextPage'] = page_number < (total + page_size - 1) // page_size if page_size > 0 else 0
        # Ensure messages is an array
        if response_data.data.get('messages') is None:
            response_data.data['messages'] = []
        return response_data

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_client_searchsp',
        summary='Client Search Orders (SP)',
        description='Client search orders with stored procedure-like filters.',
        request=OrderSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Client search orders SP',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'List of user orders',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='client/searchsp', permission_classes=[IsAuthenticated])
    def client_searchsp(self, request):
        """Client search orders (same as client_search)."""
        return self.client_search(request)

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_client_customer_searchsp',
        summary='Client Customer Search Orders (SP)',
        description='Client customer search orders with stored procedure-like filters.',
        request=OrderSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Client customer search orders SP',
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
                    'userId': 'string',
                    'status': 0,
                    'categoryId': '9707d950-290b-4f14-94da-926b276eae68',
                    'ressellerId': 'string',
                    'isOrder': True,
                    'remainday': 0,
                    'productType': 0,
                    'productId': 'string'
                }
            )
        ],
        responses={200: {
            'description': 'List of user orders',
            'content': {
                'application/json': {
                    'example': {
                        'messages': [],
                        'succeeded': True,
                        'data': [],
                        'currentPage': 1,
                        'totalPages': 0,
                        'totalCount': 0,
                        'pageSize': 20,
                        'hasPreviousPage': False,
                        'hasNextPage': False
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='client/customer/searchsp', permission_classes=[IsAuthenticated])
    def client_customer_searchsp(self, request):
        """Client customer search orders (same as client_search)."""
        return self.client_search(request)

    # Note: client_retrieve, client_orderandproductdetails, and client_withcustomerinfo are implemented as separate APIView classes below
    # because they require path parameters which are better handled outside the ViewSet

    # ============================================================================
    # ADMIN ENDPOINTS
    # ============================================================================

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_admin_getbyuserid',
        summary='Get Orders by User ID',
        description='Get orders for a specific user ID (Admin). Supports status filtering and custom ordering.',
        request=OrderAdminGetByUserIdRequestSerializer,
        examples=[
            OpenApiExample(
                'Get orders by user ID with status filter',
                value={
                    'pageNumber': 1,
                    'pageSize': 1,
                    'orderBy': [''],
                    'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'status': 2
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Paginated list of orders',
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
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    @action(detail=False, methods=['post'], url_path='admin/getbyuserid', permission_classes=[IsAuthenticated, IsManager])
    def admin_getbyuserid(self, request):
        """Get orders by user ID (Admin)."""
        user_id = request.data.get('userId')
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        status_filter = request.data.get('status')
        order_by = request.data.get('orderBy', [])

        if not user_id:
            return create_error_response(
                error_message='userId is required',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['userId is required']}
            )

        qs = Order.objects.filter(user_id=user_id)

        # Filter by status if provided (convert integer to string)
        if status_filter is not None:
            status_map = {
                0: 'pending',
                1: 'confirmed',
                2: 'in_progress',
                3: 'completed',
                4: 'cancelled',
            }
            status_string = status_map.get(status_filter)
            if status_string:
                qs = qs.filter(status=status_string)

        # Apply ordering
        if order_by and any(order_by):  # Check if order_by has non-empty values
            # Filter out empty strings and apply ordering
            valid_order_by = [o for o in order_by if o and o.strip()]
            if valid_order_by:
                # Map common order by options
                order_mapping = {
                    'newest': '-created_at',
                    'oldest': 'created_at',
                    'price_asc': 'total_price',
                    'price_desc': '-total_price',
                    'status': 'status',
                }
                order_fields = []
                for order_option in valid_order_by:
                    mapped = order_mapping.get(order_option.lower(), order_option)
                    order_fields.append(mapped)
                if order_fields:
                    qs = qs.order_by(*order_fields)
                else:
                    qs = qs.order_by('-created_at')
            else:
                qs = qs.order_by('-created_at')
        else:
            qs = qs.order_by('-created_at')

        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        serializer = OrderCompatibilitySerializer(items, many=True, context=self.get_serializer_context())
        response_data = create_success_response(data=serializer.data)
        # Add pagination fields
        response_data.data['currentPage'] = page_number
        response_data.data['totalPages'] = (total + page_size - 1) // page_size if page_size > 0 else 0
        response_data.data['totalCount'] = total
        response_data.data['pageSize'] = page_size
        response_data.data['hasPreviousPage'] = page_number > 1
        response_data.data['hasNextPage'] = page_number < (total + page_size - 1) // page_size if page_size > 0 else 0
        # Ensure messages is an array, not null
        if response_data.data.get('messages') is None:
            response_data.data['messages'] = []
        return response_data

    # ============================================================================
    # STATUS UPDATE ENDPOINTS
    # ============================================================================

    # Note: order_status_update and order_item_status_update are implemented as separate APIView classes below
    # because they require path parameters which are better handled outside the ViewSet

    # ============================================================================
    # STATISTICS ENDPOINTS
    # ============================================================================

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_stats',
        summary='Get Order Statistics',
        description='Get overall order statistics by status (Admin).',
        responses={200: {
            'description': 'Order statistics by status',
            'content': {
                'application/json': {
                    'example': {
                        'data': [
                            {'status': 0, 'counter': 1},
                            {'status': 2, 'counter': 22}
                        ],
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAuthenticated, IsManager])
    def stats(self, request):
        """Get overall order statistics by status matching old Swagger format."""
        # Status mapping: 0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled
        status_map = {
            'pending': 0,
            'confirmed': 1,
            'in_progress': 2,
            'completed': 3,
            'cancelled': 4,
        }
        
        # Get counts for each status
        stats_data = []
        for status_str, status_int in status_map.items():
            count = Order.objects.filter(status=status_str).count()
            if count > 0:  # Only include statuses with orders
                stats_data.append({
                    'status': status_int,
                    'counter': count
                })
        
        return create_success_response(data=stats_data)

    # Note: stats_by_reseller and stats_by_user are implemented as separate APIView classes below
    # because they require path parameters which are better handled outside the ViewSet

    # ============================================================================
    # UTILITY ENDPOINTS
    # ============================================================================

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_all',
        summary='Get All Orders',
        description='Get all orders matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all orders',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 1,
                                    'totalPrice': 0,
                                    'createOrderDate': '2024-03-13T08:22:26.523',
                                    'paymentTrackingCode': '-',
                                    'status': 2,
                                    'userId': '85edc2ba-81db-4648-b008-816aa2ad1dd2',
                                    'phone1': '',
                                    'userFullname': ' ',
                                    'latitude': None,
                                    'longitude': None,
                                    'addressid': None,
                                    'city': None,
                                    'country': None,
                                    'description': None,
                                    'rate': None,
                                    'storeId': None,
                                    'ressellerId': None
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    @extend_schema(
        tags=['Orders'],
        operation_id='orders_all',
        summary='Get all orders',
        description='Get all orders matching old Swagger format (simplified, no orderItems).',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of orders',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [{
                                'id': 10014,
                                'totalPrice': 0,
                                'createOrderDate': '2025-11-10T10:51:40.943',
                                'paymentTrackingCode': '-',
                                'status': 0,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'phone1': '1234',
                                'userFullname': ' ',
                                'latitude': 10,
                                'longitude': 20,
                                'addressid': None,
                                'city': 'string',
                                'country': 'string',
                                'description': 'asd',
                                'rate': 2,
                                'storeId': None,
                                'ressellerId': None
                            }],
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='all', permission_classes=[IsAuthenticated, IsManager])
    def all(self, request):
        """Get all orders matching old Swagger format (simplified, no orderItems)."""
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return create_error_response(
                    error_message='Authentication required. Please provide a valid token.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    errors={'authentication': ['Authentication required. Please provide a valid token.']}
                )
            
            # Check if user has manager permissions
            if not (request.user.is_staff or getattr(request.user, 'is_manager', False)):
                return create_error_response(
                    error_message='You do not have permission to access this endpoint. Manager role required.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'permission': ['You do not have permission to access this endpoint. Manager role required.']}
                )
            
            orders = Order.objects.all().select_related('user').order_by('-created_at')
            serializer = OrderAllSerializer(orders, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            # Handle authentication errors
            from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
            if isinstance(e, (AuthenticationFailed, NotAuthenticated)):
                return create_error_response(
                    error_message='Authentication failed. Please provide a valid token.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    errors={'authentication': ['Authentication failed. Please provide a valid token.']}
                )
            
            # Handle permission errors
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return create_error_response(
                    error_message='You do not have permission to access this endpoint.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'permission': [str(e)]}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_by_date',
        summary='Get Orders by Date',
        description='Get orders filtered by date range (Admin).',
        request=OrderByDateRequestSerializer,
        responses={200: {
            'description': 'List of orders',
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
    @action(detail=False, methods=['post'], url_path='by-date', permission_classes=[IsAuthenticated, IsManager])
    def by_date(self, request):
        """Get orders by date range."""
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)

        # Parse dates if they are strings
        from django.utils.dateparse import parse_datetime
        if start_date and isinstance(start_date, str):
            start_date = parse_datetime(start_date)
        if end_date and isinstance(end_date, str):
            end_date = parse_datetime(end_date)

        qs = Order.objects.all().select_related('user').order_by('-created_at')

        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)

        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        serializer = OrderCompatibilitySerializer(items, many=True, context=self.get_serializer_context())
        response_data = create_success_response(data=serializer.data)
        # Add pagination fields
        response_data.data['currentPage'] = page_number
        response_data.data['totalPages'] = (total + page_size - 1) // page_size if page_size > 0 else 0
        response_data.data['totalCount'] = total
        response_data.data['pageSize'] = page_size
        response_data.data['hasPreviousPage'] = page_number > 1
        response_data.data['hasNextPage'] = page_number < (total + page_size - 1) // page_size if page_size > 0 else 0
        # Ensure messages is an array, not null
        if response_data.data.get('messages') is None:
            response_data.data['messages'] = []
        return response_data

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_checkinstock',
        summary='Check Products In Stock',
        description='return product not in stocked or deleted',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'request': {
                        'type': 'object',
                        'properties': {
                            'productIds': {
                                'type': 'array',
                                'items': {'type': 'string', 'format': 'uuid'},
                                'description': 'List of product UUIDs to check'
                            }
                        },
                        'required': ['productIds']
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Check products in stock',
                value={
                    'request': {
                        'productIds': ['94860000-b419-c60d-2b41-08dc425c06b1']
                    }
                }
            ),
            OpenApiExample(
                'Direct array format (also supported)',
                value=['94860000-b419-c60d-2b41-08dc425c06b1']
            )
        ],
        responses={200: {
            'description': 'Products not in stock or deleted',
            'content': {
                'application/json': {
                    'example': {
                        'notInStock': [],
                        'deleted': []
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='checkinstock', permission_classes=[IsAuthenticated])
    def checkinstock(self, request):
        """Check if products are in stock or deleted."""
        # Handle multiple input formats:
        # 1. Old Swagger format: {"request": {"productIds": ["uuid1", "uuid2"]}}
        # 2. Direct array format: ["uuid1", "uuid2"]
        # 3. Direct object format: {"productIds": ["uuid1", "uuid2"]}
        
        request_data = request.data
        product_ids = []
        
        # Check if it's wrapped in "request" field (old Swagger format)
        if isinstance(request_data, dict) and 'request' in request_data:
            inner_request = request_data['request']
            if isinstance(inner_request, dict) and 'productIds' in inner_request:
                product_ids = inner_request['productIds']
            elif isinstance(inner_request, list):
                # Sometimes request might be a direct array
                product_ids = inner_request
        # Check if it's a direct array
        elif isinstance(request_data, list):
            product_ids = request_data
        # Check if it's a direct object with productIds
        elif isinstance(request_data, dict) and 'productIds' in request_data:
            product_ids = request_data['productIds']
        else:
            # Try to get productIds directly
            product_ids = request_data.get('productIds', [])

        # Ensure product_ids is a list
        if not isinstance(product_ids, list):
            return create_error_response(
                error_message='Invalid input format. Expected array of product IDs or object with productIds field.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'productIds': ['productIds must be an array']}
            )

        if not product_ids:
            # Return direct response matching old Swagger format (not wrapped)
            return Response({
                'notInStock': [],
                'deleted': []
            })

        # Convert all IDs to strings for comparison
        product_ids = [str(pid) for pid in product_ids if pid]
        
        # Try to convert to UUIDs for database lookup
        from uuid import UUID
        valid_uuids = []
        invalid_ids = []
        for pid in product_ids:
            try:
                UUID(pid)
                valid_uuids.append(pid)
            except (ValueError, TypeError):
                # Track invalid UUIDs as deleted
                invalid_ids.append(pid)
                continue

        # Query products
        products = []
        if valid_uuids:
            products = Product.objects.filter(id__in=valid_uuids)
        
        found_ids = set(str(p.id) for p in products)
        all_ids = set(valid_uuids)

        not_in_stock = []
        deleted = list(all_ids - found_ids) + invalid_ids  # Include invalid UUIDs as deleted

        for product in products:
            if not product.is_active or (hasattr(product, 'stock') and product.stock <= 0):
                not_in_stock.append(str(product.id))

        # Return direct response matching old Swagger format (not wrapped)
        return Response({
            'notInStock': not_in_stock,
            'deleted': deleted
        })

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_handyorder',
        summary='Create Handy Order',
        description='Create a handy order matching old Swagger format.',
        request=OrderCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create handy order',
                value={
                    'totalPrice': 0,
                    'address1': 'string',
                    'address2': 'string',
                    'phone1': 'string',
                    'phone2': 'string',
                    'createOrderDate': '2025-11-09T05:49:22.237Z',
                    'submitPriceDate': '2025-11-09T05:49:22.237Z',
                    'sendToPostDate': '2025-11-09T05:49:22.237Z',
                    'postStateNumber': 'string',
                    'paymentTrackingCode': 'string',
                    'status': 0,
                    'couponId': 0,
                    'couponKey': 'string',
                    'userId': 'string',
                    'userFullname': 'string',
                    'latitude': 0,
                    'longitude': 0,
                    'addressid': 0,
                    'city': 'string',
                    'country': 'string',
                    'description': 'string',
                    'rate': 0,
                    'storeId': 0,
                    'ressellerId': 'string',
                    'orderItems': [
                        {
                            'productId': 'string',
                            'unitPrice': 0,
                            'unitDiscountPrice': 0,
                            'itemCount': 0,
                            'status': 0,
                            'description': 'string'
                        }
                    ]
                }
            )
        ],
        responses={
            201: OpenApiResponse(
                response=serializers.Serializer,
                description='Handy order created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 'order-uuid-here',
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'User or Product not found'}
        }
    )
    @action(detail=False, methods=['post'], url_path='handyorder', permission_classes=[IsAuthenticated])
    def handyorder(self, request):
        """Create handy order matching old Swagger format."""
        # Handle request wrapper if present (old Swagger might wrap data in "request" field)
        request_data = request.data
        if isinstance(request_data, dict) and 'request' in request_data:
            request_data = request_data['request']
        
        # Validate input using old Swagger format serializer
        input_serializer = OrderCreateRequestSerializer(data=request_data)
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
        user_id = validated_data.get('userId')
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{user_id}" does not exist.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{user_id}" not found.']}
            )
        
        # Map status from integer to string
        status_map = {
            0: 'pending',
            1: 'confirmed',
            2: 'in_progress',
            3: 'completed',
            4: 'cancelled',
        }
        order_status = status_map.get(validated_data.get('status', 0), 'pending')
        
        # Parse dates
        from django.utils.dateparse import parse_datetime
        create_order_date = validated_data.get('createOrderDate')
        if create_order_date:
            if isinstance(create_order_date, str):
                create_order_date = parse_datetime(create_order_date)
        
        submit_price_date = validated_data.get('submitPriceDate')
        if submit_price_date:
            if isinstance(submit_price_date, str):
                submit_price_date = parse_datetime(submit_price_date)
        
        send_to_post_date = validated_data.get('sendToPostDate')
        if send_to_post_date:
            if isinstance(send_to_post_date, str):
                send_to_post_date = parse_datetime(send_to_post_date)
        
        # Get address fields
        address1 = validated_data.get('address1', '')
        address2 = validated_data.get('address2') or ''
        phone1 = validated_data.get('phone1', '')
        phone2 = validated_data.get('phone2') or ''
        
        # Get location
        latitude = validated_data.get('latitude')
        longitude = validated_data.get('longitude')
        
        # Create order
        order_data = {
            'user': user,
            'total_price': validated_data.get('totalPrice', 0),
            'status': order_status,
            'address1': address1,
            'address2': address2,
            'phone1': phone1,
            'phone2': phone2,
            'create_order_date': create_order_date or timezone.now(),
            'submit_price_date': submit_price_date,
            'send_to_post_date': send_to_post_date,
            'post_state_number': validated_data.get('postStateNumber') or '',
            'payment_tracking_code': validated_data.get('paymentTrackingCode') or '',
            'user_full_name': validated_data.get('userFullname') or '',
            'user_phone_number': phone1,
            'latitude': latitude,
            'longitude': longitude,
        }
        
        order = Order.objects.create(**order_data)
        
        # Create order items
        order_items_data = validated_data.get('orderItems', [])
        for item_data in order_items_data:
            product_id = item_data.get('productId')
            
            # Get product to get product name
            try:
                product = Product.objects.get(id=product_id)
                product_name = product.name
            except Product.DoesNotExist:
                return create_error_response(
                    error_message=f'Product with ID "{product_id}" does not exist.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'orderItems': [f'Product with ID "{product_id}" not found.']}
                )
            
            unit_price = item_data.get('unitPrice', 0)
            item_count = item_data.get('itemCount', 1)
            total_item_price = unit_price * item_count
            
            OrderItem.objects.create(
                order=order,
                product_name=product_name,
                quantity=item_count,
                unit_price=unit_price,
                total_price=total_item_price,
            )
        
        # Return order ID wrapped in standard response
        return create_success_response(data=str(order.id))  # 200 OK to match old Swagger

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_ordermapping',
        summary='Order Mapping',
        description='Get Order Of currently logged in user by id (mapping endpoint).',
        request=OrderMappingRequestSerializer,
        examples=[
            OpenApiExample(
                'Order mapping request',
                value={
                    'orderId': 1,
                    'orderPersonId': 'string',
                    'basketId': 1,
                    'basketUserId': 'string',
                    'procced': 0
                }
            ),
            OpenApiExample(
                'Order mapping with UUID',
                value={
                    'orderId': 'da9548fc-fc57-43c2-979b-039060edc60e',
                    'orderPersonId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'basketId': 'basket-uuid-here',
                    'basketUserId': 'user-uuid-here',
                    'procced': 1
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Order data',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': {
                                'id': 1,
                                'totalPrice': 0,
                                'createOrderDate': '2024-03-13T08:22:26.523',
                                'paymentTrackingCode': '-',
                                'status': 2,
                                'userId': '85edc2ba-81db-4648-b008-816aa2ad1dd2',
                                'phone1': '',
                                'userFullname': ' ',
                                'latitude': None,
                                'longitude': None,
                                'addressid': None,
                                'city': None,
                                'country': None,
                                'description': None,
                                'rate': None,
                                'storeId': None,
                                'ressellerId': None,
                                'orderItems': []
                            }
                        }
                    )
                ]
            ),
            404: {'description': 'Order not found'}
        }
    )
    @action(detail=False, methods=['post'], url_path='ordermapping', permission_classes=[IsAuthenticated])
    def ordermapping(self, request):
        """Order mapping endpoint matching old Swagger format."""
        serializer = OrderMappingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        order_id = validated_data.get('orderId')
        order_person_id = validated_data.get('orderPersonId')
        basket_id = validated_data.get('basketId')
        basket_user_id = validated_data.get('basketUserId')
        procced = validated_data.get('procced', 0)
        
        # Handle orderId - can be UUID or integer
        order = None
        if order_id:
            try:
                # Try as UUID first
                from uuid import UUID
                try:
                    uuid_obj = UUID(order_id)
                    order = Order.objects.get(id=uuid_obj)
                except (ValueError, TypeError, Order.DoesNotExist):
                    # Try as integer (hash lookup)
                    try:
                        integer_id = int(order_id)
                        # Find order whose UUID hash matches the integer ID
                        import hashlib
                        orders = Order.objects.all()
                        for ord in orders:
                            uuid_str = str(ord.id)
                            hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                            hash_int = int(hash_obj.hexdigest(), 16)
                            hash_id = hash_int % 2147483647
                            if hash_id == integer_id:
                                order = ord
                                break
                    except (ValueError, TypeError):
                        pass
            except Exception:
                pass
        
        # If order not found by orderId, try to find by orderPersonId or basketUserId
        if not order:
            if order_person_id:
                try:
                    from uuid import UUID
                    uuid_obj = UUID(order_person_id)
                    order = Order.objects.filter(user_id=uuid_obj).order_by('-created_at').first()
                except (ValueError, TypeError):
                    pass
            
            if not order and basket_user_id:
                try:
                    from uuid import UUID
                    uuid_obj = UUID(basket_user_id)
                    order = Order.objects.filter(user_id=uuid_obj).order_by('-created_at').first()
                except (ValueError, TypeError):
                    pass
            
            # If still not found and basketId is provided, try to find order from basket
            if not order and basket_id:
                try:
                    from uuid import UUID
                    try:
                        uuid_obj = UUID(basket_id)
                        basket = Basket.objects.filter(id=uuid_obj).first()
                    except (ValueError, TypeError):
                        try:
                            integer_id = int(basket_id)
                            basket = Basket.objects.filter(id=integer_id).first()
                        except (ValueError, TypeError):
                            basket = None
                    
                    if basket and basket.user:
                        order = Order.objects.filter(user=basket.user).order_by('-created_at').first()
                except Exception:
                    pass
        
        # If still not found, try to get the most recent order for the current user
        if not order:
            order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        
        if not order:
            return create_error_response(
                error_message='Order not found',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'orderId': ['Order not found with the provided criteria.']}
            )
        
        # If procced is 1, you might want to perform some processing here
        # For now, just return the order
        
        # Return order in old Swagger format
        order_serializer = OrderCompatibilitySerializer(order, context=self.get_serializer_context())
        return create_success_response(data=order_serializer.data)

    @extend_schema(
        tags=['Orders'],
        operation_id='orders_test_send_sms',
        summary='Test Send SMS',
        description='Test SMS sending functionality for an order (Admin).',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Order ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "6"'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='SMS test result',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': {
                                'success': True,
                                'message': 'SMS sent successfully',
                                'orderId': 'da9548fc-fc57-43c2-979b-039060edc60e',
                                'phoneNumber': '09123456789',
                                'sentMessage': 'Test SMS for order #6'
                            }
                        }
                    ),
                    OpenApiExample(
                        'Error response',
                        value={
                            'messages': ['Order not found'],
                            'succeeded': False,
                            'data': None
                        }
                    )
                ]
            ),
            400: {'description': 'Missing order ID'},
            404: {'description': 'Order not found'}
        }
    )
    @action(detail=False, methods=['get'], url_path='test-send-sms', permission_classes=[IsAuthenticated, IsManager])
    def test_send_sms(self, request):
        """Test SMS sending for an order matching old Swagger format."""
        order_id = request.query_params.get('id')
        
        if not order_id:
            return create_error_response(
                error_message='Order ID is required. Provide ?id=<order_id> in query parameters.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'id': ['Order ID query parameter is required']}
            )
        
        # Find order by ID (UUID or integer)
        order = None
        try:
            # Try as UUID first
            from uuid import UUID
            try:
                uuid_obj = UUID(order_id)
                order = Order.objects.get(id=uuid_obj)
            except (ValueError, TypeError, Order.DoesNotExist):
                # Try as integer (hash lookup)
                try:
                    integer_id = int(order_id)
                    import hashlib
                    orders = Order.objects.all()
                    for ord in orders:
                        uuid_str = str(ord.id)
                        hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                        hash_int = int(hash_obj.hexdigest(), 16)
                        hash_id = hash_int % 2147483647
                        if hash_id == integer_id:
                            order = ord
                            break
                except (ValueError, TypeError):
                    pass
        except Exception:
            pass
        
        if not order:
            return create_error_response(
                error_message=f'Order with ID "{order_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Order with ID "{order_id}" not found']}
            )
        
        # Get phone number from order
        phone_number = order.user_phone_number or (order.user.phone_number if order.user else None)
        
        if not phone_number:
            return create_error_response(
                error_message='Order does not have a phone number associated.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'phoneNumber': ['Order user does not have a phone number']}
            )
        
        # Send test SMS
        from zistino_apps.payments.sms_service import send_sms
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Create test message
        test_message = f'Test SMS for order #{order_id}. Order status: {order.status}. Total: {order.total_price:,} Rials.'
        
        try:
            success, error_message = send_sms(phone_number, test_message)
            
            if success:
                logger.info(f'Test SMS sent successfully to {phone_number} for order {order_id}')
                return create_success_response(data={
                    'success': True,
                    'message': 'SMS sent successfully',
                    'orderId': str(order.id),
                    'phoneNumber': phone_number,
                    'sentMessage': test_message
                })
            else:
                logger.warning(f'Failed to send test SMS to {phone_number} for order {order_id}: {error_message}')
                return create_error_response(
                    error_message=f'Failed to send SMS: {error_message}',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    errors={'sms': [error_message or 'SMS sending failed']}
                )
        except Exception as e:
            logger.error(f'Error sending test SMS for order {order_id}: {str(e)}')
            return create_error_response(
                error_message=f'Error sending SMS: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'sms': [str(e)]}
            )


# ============================================================================
# SEPARATE API VIEWS FOR PATH PARAMETER ENDPOINTS
# ============================================================================

@extend_schema(
    tags=['Orders'],
    operation_id='orders_stats_by_reseller',
    summary='Get Order Statistics by Reseller',
    description='Get order statistics for a specific reseller (Admin). Accepts "null" as valid value.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description='Reseller ID (UUID or "null" for orders without reseller)',
            required=True
        )
    ],
    responses={200: {
        'description': 'Reseller order statistics by status',
        'content': {
            'application/json': {
                'example': {
                    'data': [
                        {'status': 0, 'counter': 1},
                        {'status': 2, 'counter': 22}
                    ],
                    'messages': [],
                    'succeeded': True
                }
            }
        }
    }}
)
class OrdersStatsByResellerView(APIView):
    """GET /api/v1/orders/stats-by-resseller/{id} - Get order statistics by reseller"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, id):
        """Get order statistics by reseller matching old Swagger format."""
        # Handle "null" as a valid value (for orders without reseller)
        if id.lower() == 'null' or id == 'null':
            # Get orders without reseller (where resseller_id is None)
            qs = Order.objects.filter(resseller_id__isnull=True)
        else:
            # Try to find orders by reseller ID (UUID)
            try:
                from uuid import UUID
                uuid_obj = UUID(id)
                qs = Order.objects.filter(resseller_id=uuid_obj)
            except (ValueError, TypeError):
                # If not a valid UUID, return empty stats
                return create_success_response(data=[])
        
        # Status mapping: 0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled
        status_map = {
            'pending': 0,
            'confirmed': 1,
            'in_progress': 2,
            'completed': 3,
            'cancelled': 4,
        }
        
        # Get counts for each status
        stats_data = []
        for status_str, status_int in status_map.items():
            count = qs.filter(status=status_str).count()
            if count > 0:  # Only include statuses with orders
                stats_data.append({
                    'status': status_int,
                    'counter': count
                })
        
        return create_success_response(data=stats_data)


@extend_schema(
    tags=['Orders'],
    operation_id='orders_stats_by_user',
    summary='Get Order Statistics by User',
    description='Get order statistics for a specific user (Admin).',
    parameters=[
        OpenApiParameter(
            name='id',
            type=str,
            location=OpenApiParameter.PATH,
            description='User ID (UUID)',
            required=True
        )
    ],
    responses={200: {
        'description': 'User order statistics by status',
        'content': {
            'application/json': {
                'example': {
                    'data': [
                        {'status': 0, 'counter': 1},
                        {'status': 2, 'counter': 22}
                    ],
                    'messages': [],
                    'succeeded': True
                }
            }
        }
    }}
)
class OrdersStatsByUserView(APIView):
    """GET /api/v1/orders/stats-by-user/{id} - Get order statistics by user"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, id):
        """Get order statistics by user matching old Swagger format."""
        # Try to find user by UUID
        try:
            from uuid import UUID
            uuid_obj = UUID(id)
            user = User.objects.get(id=uuid_obj)
        except (ValueError, TypeError, User.DoesNotExist):
            # If user not found, return empty stats
            return create_success_response(data=[])
        
        # Get orders for this user
        qs = Order.objects.filter(user=user)
        
        # Status mapping: 0=pending, 1=confirmed, 2=in_progress, 3=completed, 4=cancelled
        status_map = {
            'pending': 0,
            'confirmed': 1,
            'in_progress': 2,
            'completed': 3,
            'cancelled': 4,
        }
        
        # Get counts for each status
        stats_data = []
        for status_str, status_int in status_map.items():
            count = qs.filter(status=status_str).count()
            if count > 0:  # Only include statuses with orders
                stats_data.append({
                    'status': status_int,
                    'counter': count
                })
        
        return create_success_response(data=stats_data)


@extend_schema(
    tags=['Orders'],
    operation_id='orders_client_retrieve',
    summary='Get Order Of currently logged in user by id',
    description='Get Order Of currently logged in user by id.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Order ID')
    ],
    responses={200: OrderSerializer, 404: {'description': 'Order not found'}}
)
class OrdersClientRetrieveView(APIView):
    """GET /api/v1/orders/client/{id} - Get order for authenticated user"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get order for authenticated user by ID matching old Swagger format."""
        # Try UUID first
        try:
            from uuid import UUID
            uuid_obj = UUID(id)
            try:
                order = Order.objects.get(pk=uuid_obj, user=request.user)
                serializer = OrderCompatibilitySerializer(order)
                return create_success_response(data=serializer.data)
            except Order.DoesNotExist:
                return create_error_response(
                    error_message='Order not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except (ValueError, TypeError):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(id)
                # Find order whose UUID hash matches the integer ID
                import hashlib
                orders = Order.objects.filter(user=request.user)
                order = None
                for ord in orders:
                    # Calculate hash the same way as serializer
                    uuid_str = str(ord.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        order = ord
                        break
                if not order:
                    return create_error_response(
                        error_message='Order not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                serializer = OrderCompatibilitySerializer(order)
                return create_success_response(data=serializer.data)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid ID format: {id}. Expected UUID or integer.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )


@extend_schema(
    tags=['Orders'],
    operation_id='orders_client_orderandproductdetails',
    summary='Get Order and Product Details',
    description='Get order details with product information.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Order ID')
    ],
    responses={200: OrderSerializer, 404: {'description': 'Order not found'}}
)
class OrdersClientOrderAndProductDetailsView(APIView):
    """GET /api/v1/orders/client/orderandproductdetails/{id} - Get order with product details"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get order with product details matching old Swagger format."""
        # Try UUID first
        try:
            from uuid import UUID
            uuid_obj = UUID(id)
            try:
                order = Order.objects.get(pk=uuid_obj, user=request.user)
                serializer = OrderCompatibilitySerializer(order, context={'request': request})
                return create_success_response(data=serializer.data)
            except Order.DoesNotExist:
                return create_error_response(
                    error_message='Order not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except (ValueError, TypeError):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(id)
                # Find order whose UUID hash matches the integer ID
                import hashlib
                orders = Order.objects.filter(user=request.user)
                order = None
                for ord in orders:
                    # Calculate hash the same way as serializer
                    uuid_str = str(ord.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        order = ord
                        break
                if not order:
                    return create_error_response(
                        error_message='Order not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                serializer = OrderCompatibilitySerializer(order, context={'request': request})
                return create_success_response(data=serializer.data)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid ID format: {id}. Expected UUID or integer.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )


@extend_schema(
    tags=['Orders'],
    operation_id='orders_client_withcustomerinfo',
    summary='Get Order Of currently logged in user by id',
    description='Get Order Of currently logged in user by id with customer info.',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Order ID')
    ],
    responses={200: OrderSerializer, 404: {'description': 'Order not found'}}
)
class OrdersClientWithCustomerInfoView(APIView):
    """GET /api/v1/orders/client/withcutomerinfo/{id} - Get order with customer info"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get order with customer info matching old Swagger format."""
        # Try UUID first
        try:
            from uuid import UUID
            uuid_obj = UUID(id)
            try:
                order = Order.objects.get(pk=uuid_obj, user=request.user)
                serializer = OrderCompatibilitySerializer(order)
                return create_success_response(data=serializer.data)
            except Order.DoesNotExist:
                return create_error_response(
                    error_message='Order not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except (ValueError, TypeError):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(id)
                # Find order whose UUID hash matches the integer ID
                import hashlib
                orders = Order.objects.filter(user=request.user)
                order = None
                for ord in orders:
                    # Calculate hash the same way as serializer
                    uuid_str = str(ord.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        order = ord
                        break
                if not order:
                    return create_error_response(
                        error_message='Order not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                serializer = OrderCompatibilitySerializer(order)
                return create_success_response(data=serializer.data)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid ID format: {id}. Expected UUID or integer.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )


@extend_schema(
    tags=['Orders'],
    operation_id='orders_order_status_update',
    summary='Update Order Status',
    description='Update order status by ID (Admin).',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='Order ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "1528181888"'
        )
    ],
    request=OrderStatusUpdateRequestSerializer,
    responses={
        200: OrderCompatibilitySerializer,
        400: {'description': 'Validation error'},
        404: {'description': 'Order not found'}
    }
)
class OrdersOrderStatusUpdateView(APIView):
    """PUT /api/v1/orders/order-status/{id} - Update order status"""
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, id):
        """Update order status matching old Swagger format."""
        # Try UUID first
        try:
            from uuid import UUID
            uuid_obj = UUID(id)
            try:
                order = Order.objects.get(pk=uuid_obj)
            except Order.DoesNotExist:
                return create_error_response(
                    error_message='Order not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except (ValueError, TypeError):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(id)
                # Find order whose UUID hash matches the integer ID
                import hashlib
                orders = Order.objects.all()
                order = None
                for ord in orders:
                    # Calculate hash the same way as serializer
                    uuid_str = str(ord.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        order = ord
                        break
                if not order:
                    return create_error_response(
                        error_message='Order not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid ID format: {id}. Expected UUID or integer.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        new_status = request.data.get('status')
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return create_error_response(
                error_message='Invalid status',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'status': ['Invalid status value']}
            )
        order.status = new_status
        order.save()
        serializer = OrderCompatibilitySerializer(order)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Orders'],
    operation_id='orders_order_item_status_update',
    summary='Update Order Item Status',
    description='Update order item status by ID (Admin).',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='Order Item ID (UUID or integer hash). Example: "da9548fc-fc57-43c2-979b-039060edc60e" or "1528181888"'
        )
    ],
    request=OrderItemStatusUpdateRequestSerializer,
    responses={
        200: OrderItemSerializer,
        400: {'description': 'Validation error'},
        404: {'description': 'Order item not found'}
    }
)
class OrdersOrderItemStatusUpdateView(APIView):
    """PUT /api/v1/orders/order-item-status/{id} - Update order item status"""
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, id):
        """Update order item status matching old Swagger format."""
        # Try UUID first (OrderItem uses UUID)
        try:
            from uuid import UUID
            uuid_obj = UUID(id)
            try:
                order_item = OrderItem.objects.get(pk=uuid_obj)
            except OrderItem.DoesNotExist:
                return create_error_response(
                    error_message='Order item not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except (ValueError, TypeError):
            # If not a valid UUID, try as integer ID (old Swagger format)
            try:
                integer_id = int(id)
                # Find order item whose UUID hash matches the integer ID
                import hashlib
                order_items = OrderItem.objects.all()
                order_item = None
                for item in order_items:
                    # Calculate hash the same way as serializer
                    uuid_str = str(item.id)
                    hash_obj = hashlib.md5(uuid_str.encode('utf-8'))
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hash_id = hash_int % 2147483647
                    if hash_id == integer_id:
                        order_item = item
                        break
                if not order_item:
                    return create_error_response(
                        error_message='Order item not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid ID format: {id}. Expected UUID or integer.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # TODO: Add status field to OrderItem model if needed
        # For now, just return the order item
        serializer = OrderItemSerializer(order_item)
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Orders'],
    operation_id='orders_orderzone',
    summary='Get Order zone',
    description='Get Order zone based on latitude and longitude.',
    parameters=[
        OpenApiParameter(name='lat', type=float, location=OpenApiParameter.PATH, description='Latitude'),
        OpenApiParameter(name='latlong', type=float, location=OpenApiParameter.PATH, description='Longitude')
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Zone information',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': [],
                        'succeeded': True,
                        'data': {
                            'zoneId': 1,
                            'zoneName': 'north-mashhad',
                            'zonePath': 'wakil abad road'
                        }
                    }
                ),
                OpenApiExample(
                    'No zone found',
                    value={
                        'messages': ['No zone found for the given coordinates'],
                        'succeeded': False,
                        'data': {
                            'zoneId': None,
                            'zoneName': None,
                            'zonePath': None
                        }
                    }
                )
            ]
        ),
        400: {'description': 'Invalid latitude or longitude'}
    }
)
class OrdersOrderZoneView(APIView):
    """GET /api/v1/orders/orderzone/{lat}/{latlong} - Get Order zone"""
    permission_classes = [AllowAny]  # Public endpoint for zone detection

    def get(self, request, lat, latlong):
        """Get zone for given latitude and longitude matching old Swagger format."""
        try:
            lat = float(lat)
            lng = float(latlong)
        except (ValueError, TypeError):
            return create_error_response(
                error_message='Invalid latitude or longitude',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'lat': ['Invalid latitude format'], 'latlong': ['Invalid longitude format']}
            )

        zone = find_zone_for_location(lat, lng)

        if zone:
            return create_success_response(data={
                'zoneId': zone.id,
                'zoneName': zone.zone,
                'zonePath': zone.zonepath or ''
            })
        else:
            # Return 200 with succeeded: false when no zone found
            return Response({
                'messages': ['No zone found for the given coordinates'],
                'succeeded': False,
                'data': {
                    'zoneId': None,
                    'zoneName': None,
                    'zonePath': None
                }
            }, status=status.HTTP_200_OK)

