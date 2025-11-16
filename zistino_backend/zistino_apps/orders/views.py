from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db import models

from .models import Order, OrderItem
from zistino_apps.payments.models import BasketDiscount, Coupon
from zistino_apps.orders.models import Basket, BasketItem
from zistino_apps.products.models import Product, Category
from zistino_apps.deliveries.models import Delivery


@extend_schema(tags=['Customer'])
class CustomerOrdersViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Customer'],
        operation_id='orders_list',
        summary='List customer orders',
        description='Get list of customer orders. Returns last 20 orders.',
        responses={
            200: {
                'description': 'List of customer orders',
                'content': {
                    'application/json': {
                        'example': {
                            'items': [
                                {
                                    'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'status': 'pending',
                                    'total_price': '125.50',
                                    'created_at': '2024-01-15T10:30:00Z'
                                }
                            ],
                            'total': 5
                        }
                    }
                }
            }
        }
    )
    def list(self, request):
        """List customer orders (simple list)."""
        qs = Order.objects.filter(user=request.user).order_by('-created_at')[:20]
        data = [{
            'id': str(o.id),
            'status': o.status,
            'total_price': o.total_price,
            'created_at': o.created_at,
        } for o in qs]
        return Response({'items': data, 'total': Order.objects.filter(user=request.user).count()})

    @extend_schema(
        tags=['Customer'],
        operation_id='orders_client_search',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'pageNumber': {'type': 'integer', 'default': 1},
                    'pageSize': {'type': 'integer', 'default': 20},
                    'keyword': {'type': 'string', 'default': ''},
                }
            }
        },
        examples=[
            OpenApiExample(
                'Search orders',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': ''
                }
            )
        ]
    )
    def client_search(self, request):
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        qs = Order.objects.filter(user=request.user).order_by('-created_at')
        if keyword:
            qs = qs.filter(user_full_name__icontains=keyword)
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        data = [{
            'id': str(o.id),
            'status': o.status,
            'total_price': o.total_price,
            'created_at': o.created_at,
        } for o in items]
        return Response({'items': data, 'pageNumber': page_number, 'pageSize': page_size, 'total': qs.count()})

    @extend_schema(
        tags=['Customer'],
        operation_id='orders_create',
        summary='Create order from basket',
        description='Convert customer basket to order. If latitude/longitude provided, automatically assigns a driver from matching zone and sets delivery date to nearest available time slot. Basket must have items. If payment_method=1 (wallet), includes confirmation message.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'latitude': {'type': 'number', 'description': 'Customer location latitude (optional - triggers auto driver assignment)'},
                    'longitude': {'type': 'number', 'description': 'Customer location longitude (optional - triggers auto driver assignment)'},
                    'address1': {'type': 'string', 'description': 'Delivery address line 1 (optional)'},
                    'address2': {'type': 'string', 'description': 'Delivery address line 2 (optional)'},
                    'phone1': {'type': 'string', 'description': 'Phone number 1 (optional)'},
                    'phone2': {'type': 'string', 'description': 'Phone number 2 (optional)'},
                    'user_full_name': {'type': 'string', 'description': 'Customer full name (optional)'},
                    'user_phone_number': {'type': 'string', 'description': 'Customer phone number (optional)'},
                    'payment_method': {'type': 'integer', 'description': 'Payment method: 1 = wallet credit, 0 or null = other methods (optional)'},
                    'estimated_weight_range': {'type': 'string', 'description': 'Estimated weight range selected by customer (e.g., "2-5", "5-10", "10-20" in kg). Optional. Get available ranges from /api/v1/orders/waste/weight-ranges/'},
                    'preferred_delivery_date': {'type': 'string', 'format': 'date-time', 'description': 'Preferred delivery date and time selected by customer (ISO 8601 format). Optional. If not provided, system will auto-select nearest available time slot.'},
                }
            }
        },
        examples=[
            OpenApiExample(
                'Create order with wallet payment',
                description='Creates order with wallet payment (payment_method=1). Returns confirmation message about next waste delivery.',
                value={
                    'latitude': 35.6892,
                    'longitude': 51.3890,
                    'address1': 'No. 10, Example Street, Tehran',
                    'phone1': '+989121234567',
                    'user_full_name': 'John Doe',
                    'payment_method': 1
                }
            ),
            OpenApiExample(
                'Create order with location (auto-assigns driver)',
                description='Creates order and automatically assigns driver from zone containing this location. Automatically selects nearest available time slot (e.g., if current time is 10 AM in 8-12 slot, selects 12-4 PM slot).',
                value={
                    'latitude': 35.6892,
                    'longitude': 51.3890,
                    'address1': 'No. 10, Example Street, Tehran',
                    'phone1': '+989121234567',
                    'user_full_name': 'John Doe'
                }
            ),
            OpenApiExample(
                'Create order without location',
                description='Creates order without driver assignment. Driver can be assigned manually later.',
                value={
                    'address1': 'No. 10, Example Street',
                    'phone1': '+989121234567'
                }
            ),
            OpenApiExample(
                'Minimal order creation',
                description='Creates order with minimal data. Basket items will be used.',
                value={}
            ),
            OpenApiExample(
                'Create order with waste delivery request details',
                description='Creates order with estimated weight range and preferred delivery date/time. Get available weight ranges from /api/v1/orders/waste/weight-ranges/ and time slots from /api/v1/orders/waste/time-slots/.',
                value={
                    'latitude': 35.6892,
                    'longitude': 51.3890,
                    'address1': 'No. 10, Example Street, Tehran',
                    'phone1': '+989121234567',
                    'user_full_name': 'John Doe',
                    'estimated_weight_range': '5-10',
                    'preferred_delivery_date': '2024-01-16T14:00:00Z'
                }
            )
        ],
        responses={
            201: {
                'description': 'Order created successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'wallet_payment_with_location': {
                                'summary': 'Order with wallet payment and location (driver assigned, time slot selected)',
                                'value': {
                                    'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'message': 'کالاهای سفارش داده شده در تحویل بعدی زباله به شما ارسال خواهد شد',
                                    'message_en': 'Ordered goods will be sent to you in the next waste delivery',
                                    'payment_method': 'wallet',
                                    'delivery_time_slot': '12 PM to 4 PM',
                                    'delivery_date': '2024-01-15T12:00:00Z'
                                }
                            },
                            'wallet_payment': {
                                'summary': 'Order with wallet payment (no location)',
                                'value': {
                                    'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'message': 'کالاهای سفارش داده شده در تحویل بعدی زباله به شما ارسال خواهد شد',
                                    'message_en': 'Ordered goods will be sent to you in the next waste delivery',
                                    'payment_method': 'wallet'
                                }
                            },
                            'with_location_time_slot': {
                                'summary': 'Order with location (driver assigned, nearest time slot selected)',
                                'value': {
                                    'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'delivery_time_slot': '12 PM to 4 PM',
                                    'delivery_date': '2024-01-15T12:00:00Z'
                                }
                            },
                            'other_payment': {
                                'summary': 'Order with other payment method (no location)',
                                'value': {
                                    'id': '46e818ce-0518-4c64-8438-27bc7163a706'
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'basket is empty'
                        }
                    }
                }
            }
        }
    )
    def create(self, request):
        # Convert current user's basket into an order
        basket = Basket.objects.filter(user=request.user).first()
        if not basket or basket.is_empty:
            return Response({'detail': 'basket is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get latitude/longitude from request (optional - from Flutter location button)
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        # Create order with location if provided
        order_data = {
            'user': request.user,
            'total_price': basket.cart_total,
            'status': 'pending',
        }
        if latitude:
            order_data['latitude'] = latitude
        if longitude:
            order_data['longitude'] = longitude
        
        # Copy address fields from request if provided
        if request.data.get('address1'):
            order_data['address1'] = request.data.get('address1')
        if request.data.get('address2'):
            order_data['address2'] = request.data.get('address2')
        if request.data.get('phone1'):
            order_data['phone1'] = request.data.get('phone1')
        if request.data.get('phone2'):
            order_data['phone2'] = request.data.get('phone2')
        if request.data.get('user_full_name'):
            order_data['user_full_name'] = request.data.get('user_full_name')
        if request.data.get('user_phone_number'):
            order_data['user_phone_number'] = request.data.get('user_phone_number')
        # Add estimated weight range if provided
        if request.data.get('estimated_weight_range'):
            order_data['estimated_weight_range'] = request.data.get('estimated_weight_range')
        # Add preferred delivery date if provided
        if request.data.get('preferred_delivery_date'):
            from django.utils.dateparse import parse_datetime
            preferred_date = parse_datetime(request.data.get('preferred_delivery_date'))
            if preferred_date:
                order_data['preferred_delivery_date'] = preferred_date
        
        order = Order.objects.create(**order_data)
        
        items = list(basket.items.all())
        bulk_items = []
        for it in items:
            bulk_items.append(OrderItem(
                order=order,
                product_name=it.name,
                quantity=it.quantity,
                unit_price=it.price,
                total_price=it.item_total,
            ))
        OrderItem.objects.bulk_create(bulk_items)
        
        # mark coupon usage and clear discount if present
        bd = getattr(basket, 'discount', None)
        if bd:
            Coupon.objects.filter(pk=bd.coupon_id).update(used_count=models.F('used_count') + 1)
            bd.delete()
        
        # clear basket
        basket.items.all().delete()
        Basket.objects.filter(pk=basket.pk).update(is_empty=True, total_items=0, total_unique_items=0, cart_total=0)
        
        # Initialize response data
        response_data = {'id': str(order.id)}
        
        # Automatic driver assignment based on location
        if latitude and longitude:
            from zistino_apps.deliveries.utils import find_zone_for_location, assign_driver_to_order, find_nearest_time_slot
            zone = find_zone_for_location(latitude, longitude)
            if zone:
                delivery = assign_driver_to_order(order, zone)
                if delivery:
                    # Use preferred_delivery_date if provided, otherwise auto-select nearest time slot
                    if order.preferred_delivery_date:
                        delivery.delivery_date = order.preferred_delivery_date
                        delivery.save(update_fields=['delivery_date'])
                        # Format time slot for response
                        preferred_hour = order.preferred_delivery_date.hour
                        # Find which slot this hour falls into and format it
                        from zistino_apps.configurations.models import Configuration
                        try:
                            config = Configuration.objects.filter(name__icontains='delivery_time', is_active=True).first()
                            if config and config.value:
                                start_hour = int(config.value.get('start', 8))
                                end_hour = int(config.value.get('end', 20))
                                split = int(config.value.get('split', 4))
                            else:
                                start_hour, end_hour, split = 8, 20, 4
                        except:
                            start_hour, end_hour, split = 8, 20, 4
                        
                        # Find slot containing preferred hour
                        slot_start = ((preferred_hour - start_hour) // split) * split + start_hour
                        slot_end = min(slot_start + split, end_hour)
                        
                        def format_hour(h):
                            if h == 0: return "12 AM"
                            elif h < 12: return f"{h} AM"
                            elif h == 12: return "12 PM"
                            else: return f"{h - 12} PM"
                        
                        response_data['delivery_time_slot'] = f"{format_hour(slot_start)} to {format_hour(slot_end)}"
                        response_data['delivery_date'] = order.preferred_delivery_date.isoformat()
                    else:
                        # Automatically set delivery date to nearest available time slot
                        delivery_datetime, time_slot_info = find_nearest_time_slot()
                        if delivery_datetime:
                            delivery.delivery_date = delivery_datetime
                            delivery.save(update_fields=['delivery_date'])
                            # Include time slot info in response
                            response_data['delivery_time_slot'] = time_slot_info.get('formatted')
                            response_data['delivery_date'] = delivery_datetime.isoformat()
        
        # Check if payment was via wallet and include confirmation message
        payment_method = request.data.get('payment_method')
        
        # If payment method is wallet (1), add confirmation message
        if payment_method == 1:
            response_data['message'] = 'کالاهای سفارش داده شده در تحویل بعدی زباله به شما ارسال خواهد شد'
            response_data['message_en'] = 'Ordered goods will be sent to you in the next waste delivery'
            response_data['payment_method'] = 'wallet'
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Customer'],
        operation_id='orders_get',
        summary='Get order details',
        description='Retrieve details of a specific order by ID. User can only access their own orders.',
        responses={
            200: {
                'description': 'Order details',
                'content': {
                    'application/json': {
                        'example':                         {
                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                            'status': 'pending',
                            'total_price': '125.50',
                            'created_at': '2024-01-15T10:30:00Z'
                        }
                    }
                }
            },
            404: {
                'description': 'Order not found',
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
    def retrieve(self, request, pk=None):
        try:
            o = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'id': str(o.id), 'status': o.status, 'total_price': o.total_price, 'created_at': o.created_at})

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiExample
from zistino_apps.users.permissions import IsManager

from .models import Order, OrderItem, Basket, BasketItem
from .serializers import OrderSerializer, OrderItemSerializer, BasketSerializer, BasketItemSerializer


@extend_schema(tags=['Orders'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Orders" folder instead
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all orders for admin, user-scoped for regular users."""
        if self.request.user.is_staff:
            return Order.objects.all().select_related('user').order_by('-created_at')
        return Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        """Admin can access all, regular users only their own."""
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=['Admin'],
        operation_id='orders_searchsp',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'pageNumber': {'type': 'integer', 'default': 1},
                    'pageSize': {'type': 'integer', 'default': 20},
                    'keyword': {'type': 'string', 'default': ''},
                    'status': {'type': 'string', 'default': 'all', 'description': 'Order status filter: "all", "pending", "confirmed", "in_progress", "completed", "cancelled" (or -1 for backward compatibility)'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Search all orders',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': '',
                    'status': 'all'
                }
            ),
            OpenApiExample(
                'Search pending orders',
                value={
                    'pageNumber': 1,
                    'pageSize': 20,
                    'keyword': 'John',
                    'status': 'pending'
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='searchsp', permission_classes=[IsAuthenticated, IsManager])
    def searchsp(self, request):
        """Admin search endpoint for orders with pagination and status filter."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        status_filter = request.data.get('status', 'all')
        
        qs = Order.objects.all().select_related('user').order_by('-created_at')
        
        # Filter by status ('all' means all statuses, or use status string directly)
        # Also support backward compatibility with integer status values
        if status_filter and status_filter != 'all':
            # Map old integer status to new string status if needed for backward compatibility
            status_map = {
                -1: None,  # All statuses
                0: 'pending',
                1: 'confirmed',
                2: 'in_progress',
                3: 'completed',
                4: 'cancelled'
            }
            if isinstance(status_filter, int) and status_filter in status_map:
                status_filter = status_map[status_filter]
            if status_filter:
                qs = qs.filter(status=status_filter)
        
        # Filter by keyword (search in user name, phone, order fields)
        if keyword:
            qs = qs.filter(
                Q(user_full_name__icontains=keyword) |
                Q(user_phone_number__icontains=keyword) |
                Q(id__icontains=keyword)
            )
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': OrderSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Orders'])
class BasketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BasketSerializer

    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Orders'])
class BasketItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BasketItemSerializer

    def get_queryset(self):
        return BasketItem.objects.filter(basket__user=self.request.user)

    def perform_create(self, serializer):
        # Expect 'basket' in payload referencing user's basket id
        return super().perform_create(serializer)


# ============================================
# WASTE WEIGHT MANAGEMENT ENDPOINTS
# ============================================

@extend_schema(tags=['Waste Weight'])
class WasteWeightSummaryView(APIView):
    """View waste weight summary per category/waste type for logged-in customer."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Waste Weight'],
        operation_id='waste_weight_summary',
        summary='Get waste weight summary by type',
        description='Get total weight of each waste type/category from completed orders and deliveries. Groups by product category.',
        responses={
            200: {
                'description': 'Weight summary per waste type',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Customer with waste weight data',
                                'value': {
                                    'summary': [
                                        {
                                            'categoryId': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'categoryName': 'Plastic',
                                            'totalWeight': 150.50,
                                            'unit': 'kg',
                                            'orderCount': 5,
                                            'deliveryCount': 5
                                        },
                                        {
                                            'categoryId': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'categoryName': 'Paper',
                                            'totalWeight': 80.25,
                                            'unit': 'kg',
                                            'orderCount': 3,
                                            'deliveryCount': 3
                                        },
                                        {
                                            'categoryId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                            'categoryName': 'Glass',
                                            'totalWeight': 45.75,
                                            'unit': 'kg',
                                            'orderCount': 2,
                                            'deliveryCount': 2
                                        }
                                    ],
                                    'totalWeight': 276.50,
                                    'totalOrders': 10,
                                    'totalDeliveries': 10
                                }
                            },
                            'example2': {
                                'summary': 'New customer with no waste data',
                                'value': {
                                    'summary': [],
                                    'totalWeight': 0.0,
                                    'totalOrders': 0,
                                    'totalDeliveries': 0
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Get weight summary grouped by waste type/category."""
        user = request.user
        
        # Get orders - try multiple status values or all completed orders
        # Status values: 'pending', 'confirmed', 'in_progress', 'completed', 'cancelled'
        # Get all orders first, then filter by weight data (more flexible)
        user_orders = Order.objects.filter(user=user)
        
        # Get order items with weight data (weight > 0)
        # If no weight data, this will return empty - which is correct
        order_items = OrderItem.objects.filter(
            order__in=user_orders,
            weight__gt=0
        ).select_related('order')
        
        # Try to match product_name with Product model to get categories
        # Group by product name first, then try to find category
        weight_by_product = {}
        for item in order_items:
            product_name = item.product_name
            if product_name not in weight_by_product:
                weight_by_product[product_name] = {
                    'weight': 0.0,
                    'order_count': set(),
                    'delivery_count': set()
                }
            weight_by_product[product_name]['weight'] += float(item.weight or 0)
            weight_by_product[product_name]['order_count'].add(item.order.id)
        
        # Get deliveries with delivered_weight for the same orders (that have weight data)
        # Only include confirmed deliveries - unconfirmed deliveries don't count in customer statistics
        orders_with_weight = order_items.values_list('order_id', flat=True).distinct()
        deliveries = Delivery.objects.filter(
            order_id__in=orders_with_weight,
            delivered_weight__gt=0,
            customer_confirmation_status='confirmed'  # Only count confirmed deliveries
        ).select_related('order')
        
        for delivery in deliveries:
            # Try to match order items to get product names
            order_items_for_delivery = OrderItem.objects.filter(order=delivery.order)
            for item in order_items_for_delivery:
                product_name = item.product_name
                if product_name in weight_by_product:
                    weight_by_product[product_name]['delivery_count'].add(delivery.id)
        
        # Try to match products to get categories
        summary = []
        category_weights = {}
        
        for product_name, data in weight_by_product.items():
            try:
                # Try to find product by name
                product = Product.objects.filter(name__icontains=product_name).first()
                if product and product.category:
                    category_id = str(product.category.id)
                    category_name = product.category.name
                    
                    if category_id not in category_weights:
                        category_weights[category_id] = {
                            'categoryId': category_id,
                            'categoryName': category_name,
                            'totalWeight': 0.0,
                            'orderCount': set(),
                            'deliveryCount': set()
                        }
                    
                    category_weights[category_id]['totalWeight'] += data['weight']
                    category_weights[category_id]['orderCount'].update(data['order_count'])
                    category_weights[category_id]['deliveryCount'].update(data['delivery_count'])
                else:
                    # If product not found, use product name as category
                    category_weights[product_name] = {
                        'categoryId': None,
                        'categoryName': product_name,
                        'totalWeight': data['weight'],
                        'orderCount': len(data['order_count']),
                        'deliveryCount': len(data['delivery_count'])
                    }
            except Exception:
                # If error, use product name as category
                category_weights[product_name] = {
                    'categoryId': None,
                    'categoryName': product_name,
                    'totalWeight': data['weight'],
                    'orderCount': len(data['order_count']),
                    'deliveryCount': len(data['delivery_count'])
                }
        
        # Convert to list format
        for cat_data in category_weights.values():
            summary.append({
                'categoryId': cat_data['categoryId'],
                'categoryName': cat_data['categoryName'],
                'totalWeight': round(float(cat_data['totalWeight']), 2),
                'unit': 'kg',
                'orderCount': len(cat_data['orderCount']) if isinstance(cat_data['orderCount'], set) else cat_data['orderCount'],
                'deliveryCount': len(cat_data['deliveryCount']) if isinstance(cat_data['deliveryCount'], set) else cat_data['deliveryCount']
            })
        
        # Calculate totals
        total_weight = sum(item['totalWeight'] for item in summary)
        # Count unique orders and deliveries that have weight data
        unique_order_ids = set()
        unique_delivery_ids = set()
        for cat_data in category_weights.values():
            if isinstance(cat_data.get('orderCount'), set):
                unique_order_ids.update(cat_data['orderCount'])
            if isinstance(cat_data.get('deliveryCount'), set):
                unique_delivery_ids.update(cat_data['deliveryCount'])
        
        total_orders = len(unique_order_ids) if unique_order_ids else 0
        total_deliveries = len(unique_delivery_ids) if unique_delivery_ids else len(deliveries)
        
        return Response({
            'summary': summary,
            'totalWeight': round(total_weight, 2),
            'totalOrders': total_orders,
            'totalDeliveries': total_deliveries
        })


@extend_schema(tags=['Waste Weight'])
class WasteWeightHistoryView(APIView):
    """View customer's waste weight history (paginated list of orders with weights)."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Waste Weight'],
        operation_id='waste_weight_history',
        summary='Get my waste weight history',
        description='Get paginated history of orders with weight data. Shows weight per order and per item.',
        responses={
            200: {
                'description': 'Weight history list',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Customer with weight history',
                                'value': {
                                    'items': [
                                        {
                                            'orderId': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'orderDate': '2024-01-15T10:30:00Z',
                                            'orderStatus': 'completed',
                                            'totalWeight': 25.50,
                                            'deliveredWeight': 25.50,
                                            'items': [
                                                {
                                                    'productName': 'Plastic Bottles',
                                                    'quantity': 10,
                                                    'weight': 15.50,
                                                    'categoryName': 'Plastic'
                                                },
                                                {
                                                    'productName': 'Paper',
                                                    'quantity': 5,
                                                    'weight': 10.00,
                                                    'categoryName': 'Paper'
                                                }
                                            ]
                                        },
                                        {
                                            'orderId': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'orderDate': '2024-01-14T09:00:00Z',
                                            'orderStatus': 'completed',
                                            'totalWeight': 30.75,
                                            'deliveredWeight': 30.75,
                                            'items': [
                                                {
                                                    'productName': 'Glass Containers',
                                                    'quantity': 8,
                                                    'weight': 30.75,
                                                    'categoryName': 'Glass'
                                                }
                                            ]
                                        }
                                    ],
                                    'total': 10,
                                    'pageNumber': 1,
                                    'pageSize': 20
                                }
                            },
                            'example2': {
                                'summary': 'No weight history',
                                'value': {
                                    'items': [],
                                    'total': 0,
                                    'pageNumber': 1,
                                    'pageSize': 20
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Get weight history with pagination."""
        user = request.user
        page_number = int(request.query_params.get('pageNumber', 1))
        page_size = int(request.query_params.get('pageSize', 20))
        
        # Get all user orders with weight data (not filtering by status for flexibility)
        user_orders = Order.objects.filter(
            user=user
        ).prefetch_related('order_items', 'deliveries').order_by('-created_at')
        
        # Filter orders that have weight data
        orders_with_weight = []
        for order in user_orders:
            order_items = order.order_items.filter(weight__gt=0)
            if order_items.exists():
                # Get delivery weight if available - only count confirmed deliveries
                delivery = order.deliveries.filter(customer_confirmation_status='confirmed').first()
                delivered_weight = float(delivery.delivered_weight or 0) if delivery else 0.0
                
                # Calculate total weight for order
                total_weight = sum(float(item.weight or 0) for item in order_items)
                
                # Get items with category names
                items_data = []
                for item in order_items:
                    # Try to find product to get category
                    category_name = None
                    try:
                        product = Product.objects.filter(name__icontains=item.product_name).first()
                        if product and product.category:
                            category_name = product.category.name
                    except Exception:
                        pass
                    
                    items_data.append({
                        'productName': item.product_name,
                        'quantity': item.quantity,
                        'weight': float(item.weight or 0),
                        'categoryName': category_name
                    })
                
                orders_with_weight.append({
                    'orderId': str(order.id),
                    'orderDate': order.created_at.isoformat(),
                    'orderStatus': order.status,
                    'totalWeight': round(total_weight, 2),
                    'deliveredWeight': round(delivered_weight, 2),
                    'items': items_data
                })
        
        # Pagination
        total = len(orders_with_weight)
        start = (page_number - 1) * page_size
        end = start + page_size
        paginated_items = orders_with_weight[start:end]
        
        return Response({
            'items': paginated_items,
            'total': total,
            'pageNumber': page_number,
            'pageSize': page_size
        })


@extend_schema(tags=['Waste Weight'])
class OrderWeightDetailView(APIView):
    """View weight breakdown for a specific order."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Waste Weight'],
        operation_id='order_weight_detail',
        summary='Get order weight breakdown',
        description='Get detailed weight breakdown for a specific order, showing weight per item and category.',
        responses={
            200: {
                'description': 'Order weight details',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Order with weight data',
                                'value': {
                                    'orderId': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'orderDate': '2024-01-15T10:30:00Z',
                                    'orderStatus': 'completed',
                                    'totalWeight': 25.50,
                                    'deliveredWeight': 25.50,
                                    'items': [
                                        {
                                            'itemId': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'productName': 'Plastic Bottles',
                                            'quantity': 10,
                                            'weight': 15.50,
                                            'unit': 'kg',
                                            'categoryId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                            'categoryName': 'Plastic'
                                        },
                                        {
                                            'itemId': 'xyz98765-4321-fedc-ba09-876543210fed',
                                            'productName': 'Paper',
                                            'quantity': 5,
                                            'weight': 10.00,
                                            'unit': 'kg',
                                            'categoryId': 'pqr45678-9012-3456-7890-abcdefghijkl',
                                            'categoryName': 'Paper'
                                        }
                                    ],
                                    'summaryByCategory': [
                                        {
                                            'categoryId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                            'categoryName': 'Plastic',
                                            'totalWeight': 15.50
                                        },
                                        {
                                            'categoryId': 'pqr45678-9012-3456-7890-abcdefghijkl',
                                            'categoryName': 'Paper',
                                            'totalWeight': 10.00
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Order not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Order not found'
                        }
                    }
                }
            }
        }
    )
    def get(self, request, order_id):
        """Get weight breakdown for a specific order."""
        user = request.user
        
        try:
            order = Order.objects.prefetch_related('order_items', 'deliveries').get(
                id=order_id,
                user=user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get order items with weight
        order_items = order.order_items.filter(weight__gt=0)
        
        # Get delivery weight - only count confirmed deliveries
        delivery = order.deliveries.filter(customer_confirmation_status='confirmed').first()
        delivered_weight = float(delivery.delivered_weight or 0) if delivery else 0.0
        
        # Calculate total weight
        total_weight = sum(float(item.weight or 0) for item in order_items)
        
        # Build items data with categories
        items_data = []
        category_weights = {}
        
        for item in order_items:
            category_id = None
            category_name = None
            
            # Try to find product to get category
            try:
                product = Product.objects.filter(name__icontains=item.product_name).first()
                if product and product.category:
                    category_id = str(product.category.id)
                    category_name = product.category.name
                    
                    # Accumulate category weights
                    if category_id not in category_weights:
                        category_weights[category_id] = {
                            'categoryId': category_id,
                            'categoryName': category_name,
                            'totalWeight': 0.0
                        }
                    category_weights[category_id]['totalWeight'] += float(item.weight or 0)
            except Exception:
                pass
            
            items_data.append({
                'itemId': str(item.id),
                'productName': item.product_name,
                'quantity': item.quantity,
                'weight': round(float(item.weight or 0), 2),
                'unit': 'kg',
                'categoryId': category_id,
                'categoryName': category_name
            })
        
        # Build summary by category
        summary_by_category = [
            {
                'categoryId': data['categoryId'],
                'categoryName': data['categoryName'],
                'totalWeight': round(data['totalWeight'], 2)
            }
            for data in category_weights.values()
        ]
        
        return Response({
            'orderId': str(order.id),
            'orderDate': order.created_at.isoformat(),
            'orderStatus': order.status,
            'totalWeight': round(total_weight, 2),
            'deliveredWeight': round(delivered_weight, 2),
            'items': items_data,
            'summaryByCategory': summary_by_category
        })


# ============================================
# WASTE DELIVERY REQUEST CONFIGURATION ENDPOINTS
# ============================================

@extend_schema(tags=['Customer'])
class WeightRangesView(APIView):
    """Get available weight ranges for waste delivery requests."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Customer'],
        operation_id='get_weight_ranges',
        summary='Get available weight ranges',
        description='Get list of predefined weight ranges (e.g., 2-5 kg, 5-10 kg) configured on the server. Customers select from these ranges when creating waste delivery requests.',
        responses={
            200: {
                'description': 'List of available weight ranges',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Weight ranges from configuration',
                                'value': {
                                    'ranges': [
                                        {'id': '1', 'label': '2-5 kg', 'value': '2-5', 'min': 2, 'max': 5},
                                        {'id': '2', 'label': '5-10 kg', 'value': '5-10', 'min': 5, 'max': 10},
                                        {'id': '3', 'label': '10-20 kg', 'value': '10-20', 'min': 10, 'max': 20},
                                        {'id': '4', 'label': '20-50 kg', 'value': '20-50', 'min': 20, 'max': 50},
                                        {'id': '5', 'label': '50+ kg', 'value': '50+', 'min': 50, 'max': None}
                                    ]
                                }
                            },
                            'example2': {
                                'summary': 'Default weight ranges (no configuration)',
                                'value': {
                                    'ranges': [
                                        {'id': '1', 'label': '2-5 kg', 'value': '2-5', 'min': 2, 'max': 5},
                                        {'id': '2', 'label': '5-10 kg', 'value': '5-10', 'min': 5, 'max': 10},
                                        {'id': '3', 'label': '10-20 kg', 'value': '10-20', 'min': 10, 'max': 20}
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Get available weight ranges from Configuration or return defaults."""
        try:
            from zistino_apps.configurations.models import Configuration
            
            # Get weight ranges configuration
            config = Configuration.objects.filter(
                name__icontains='weight_range',
                is_active=True
            ).first()
            
            if config and config.value and isinstance(config.value, list):
                # Configuration provides list of ranges
                ranges = []
                for idx, range_item in enumerate(config.value, start=1):
                    ranges.append({
                        'id': str(idx),
                        'label': range_item.get('label', range_item.get('value', '')),
                        'value': range_item.get('value', ''),
                        'min': range_item.get('min'),
                        'max': range_item.get('max')
                    })
                return Response({'ranges': ranges})
        except Exception:
            pass
        
        # Default weight ranges if no configuration found
        default_ranges = [
            {'id': '1', 'label': '2-5 kg', 'value': '2-5', 'min': 2, 'max': 5},
            {'id': '2', 'label': '5-10 kg', 'value': '5-10', 'min': 5, 'max': 10},
            {'id': '3', 'label': '10-20 kg', 'value': '10-20', 'min': 10, 'max': 20},
            {'id': '4', 'label': '20-50 kg', 'value': '20-50', 'min': 20, 'max': 50},
            {'id': '5', 'label': '50+ kg', 'value': '50+', 'min': 50, 'max': None}
        ]
        return Response({'ranges': default_ranges})


@extend_schema(tags=['Customer'])
class TimeSlotsView(APIView):
    """Get available time slots for delivery date/time selection."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Customer'],
        operation_id='get_time_slots',
        summary='Get available time slots',
        description='Get list of available time slots for delivery (e.g., 8 AM - 12 PM, 12 PM - 4 PM). Time slots are configured on the server. Customers can select their preferred time slot when creating waste delivery requests.',
        responses={
            200: {
                'description': 'List of available time slots',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Time slots from configuration',
                                'value': {
                                    'slots': [
                                        {'id': '1', 'label': '8 AM - 12 PM', 'startHour': 8, 'endHour': 12, 'startFormatted': '8 AM', 'endFormatted': '12 PM'},
                                        {'id': '2', 'label': '12 PM - 4 PM', 'startHour': 12, 'endHour': 16, 'startFormatted': '12 PM', 'endFormatted': '4 PM'},
                                        {'id': '3', 'label': '4 PM - 8 PM', 'startHour': 16, 'endHour': 20, 'startFormatted': '4 PM', 'endFormatted': '8 PM'}
                                    ],
                                    'startHour': 8,
                                    'endHour': 20,
                                    'split': 4
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Get available time slots from Configuration or return defaults."""
        try:
            from zistino_apps.configurations.models import Configuration
            
            # Get delivery time configuration
            config = Configuration.objects.filter(
                name__icontains='delivery_time',
                is_active=True
            ).first()
            
            if config and config.value:
                start_hour = int(config.value.get('start', 8))
                end_hour = int(config.value.get('end', 20))
                split = int(config.value.get('split', 4))
            else:
                # Defaults
                start_hour = 8
                end_hour = 20
                split = 4
        except Exception:
            # Defaults if any error
            start_hour = 8
            end_hour = 20
            split = 4
        
        # Generate time slots
        slots = []
        slot_id = 1
        current = start_hour
        while current < end_hour:
            slot_end = min(current + split, end_hour)
            
            # Format hours
            def format_hour(h):
                if h == 0:
                    return "12 AM"
                elif h < 12:
                    return f"{h} AM"
                elif h == 12:
                    return "12 PM"
                else:
                    return f"{h - 12} PM"
            
            slots.append({
                'id': str(slot_id),
                'label': f'{format_hour(current)} - {format_hour(slot_end)}',
                'startHour': current,
                'endHour': slot_end,
                'startFormatted': format_hour(current),
                'endFormatted': format_hour(slot_end)
            })
            
            slot_id += 1
            current = slot_end
        
        return Response({
            'slots': slots,
            'startHour': start_hour,
            'endHour': end_hour,
            'split': split
        })