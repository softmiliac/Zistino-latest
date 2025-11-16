"""
Views for DriverDelivery compatibility layer.
Provides all 5 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.db.models import Q
from django.contrib.auth import get_user_model

from zistino_apps.deliveries.models import Delivery
from zistino_apps.orders.models import Order
from zistino_apps.deliveries.serializers import DeliverySerializer, DeliverySearchRequestSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    DriverDeliveryCreateRequestSerializer,
    DriverDeliveryUpdateRequestSerializer,
    DriverDeliverySearchRequestSerializer,
)

User = get_user_model()


@extend_schema(tags=['DriverDelivery'])
class DriverDeliveryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DriverDelivery endpoints.
    Wraps the existing DeliveryViewSet functionality for driver-specific operations.
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        """Filter deliveries to only show those for the current driver."""
        if self.request.user.is_driver:
            return Delivery.objects.filter(driver=self.request.user)
        # Managers can see all deliveries
        elif self.request.user.is_staff:
            return Delivery.objects.all()
        return Delivery.objects.none()
    
    def get_object(self):
        """Override to handle both UUID and integer IDs for deliveries."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs.get(lookup_url_kwarg)
        
        if not pk:
            return None
        
        # Try to get delivery by UUID first
        try:
            # Try parsing as UUID
            import uuid
            uuid.UUID(str(pk))
            return Delivery.objects.get(id=pk)
        except (Delivery.DoesNotExist, ValueError, TypeError):
            # If UUID parsing fails, try to find by integer hash
            # This is for backward compatibility with integer IDs
            import hashlib
            for delivery in Delivery.objects.all():
                delivery_id_str = str(delivery.id).replace('-', '')
                delivery_id_int = int(hashlib.md5(delivery_id_str.encode()).hexdigest()[:8], 16) % 100000000
                if str(delivery_id_int) == str(pk):
                    return delivery
            
            # If not found, raise DoesNotExist
            raise Delivery.DoesNotExist(f'Delivery with ID "{pk}" not found.')

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_list',
        summary='List all deliveries',
        description='Get a list of all deliveries. Use the "id" field from the response as the "job-id" parameter for vehicle, locations, and trip endpoints.',
    )
    def list(self, request, *args, **kwargs):
        """List all deliveries - returns delivery IDs that can be used as job-id."""
        try:
            queryset = self.get_queryset()
            serializer = DeliverySerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_retrieve',
        summary='Retrieve a delivery by ID',
        description='Get a delivery by ID. The returned "id" can be used as "job-id" parameter for vehicle, locations, and trip endpoints.',
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a delivery by ID matching old Swagger format."""
        try:
            delivery = self.get_object()
            serializer = DeliverySerializer(delivery)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Delivery.DoesNotExist:
            pk = kwargs.get('id', 'unknown')
            return create_error_response(
                error_message=f'Delivery with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Delivery with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_create',
        summary='Create a new driver delivery',
        request=DriverDeliveryCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Driver Delivery (default)',
                value={
                    "userId": "string",
                    "deliveryUserId": "string",
                    "deliveryDate": "2025-11-10T19:27:57.824Z",
                    "setUserId": "string",
                    "addressId": 0,
                    "orderId": 0,
                    "examId": 0,
                    "requestId": 0,
                    "zoneId": 0,
                    "preOrderId": 0,
                    "status": 0,
                    "description": "string"
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Driver delivery created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 10012,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new driver delivery matching old Swagger format."""
        try:
            serializer = DriverDeliveryCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get driver (deliveryUserId or userId)
            driver_id = validated_data.get('deliveryUserId') or validated_data.get('userId')
            if not driver_id:
                return create_error_response(
                    error_message='deliveryUserId or userId is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'deliveryUserId': ['deliveryUserId or userId is required']}
                )
            
            try:
                driver = User.objects.get(id=driver_id)
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{driver_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'deliveryUserId': [f'User with ID "{driver_id}" not found.']}
                )
            
            # Get order (orderId is required for Delivery model)
            order_id = validated_data.get('orderId', 0)
            if order_id == 0:
                # Try to get the first available order or create a placeholder
                order = Order.objects.first()
                if not order:
                    return create_error_response(
                        error_message='No orders available. Please create an order first.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'orderId': ['No orders available. Please create an order first.']}
                    )
            else:
                try:
                    order = Order.objects.get(id=order_id)
                except Order.DoesNotExist:
                    return create_error_response(
                        error_message=f'Order with ID "{order_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'orderId': [f'Order with ID "{order_id}" not found.']}
                    )
            
            # Map status (0=assigned, 1=in_progress, 2=completed, 3=cancelled) to status
            status_map = {0: 'assigned', 1: 'in_progress', 2: 'completed', 3: 'cancelled'}
            delivery_status = status_map.get(validated_data.get('status', 0), 'assigned')
            
            # Create delivery
            delivery = Delivery.objects.create(
                driver=driver,
                order=order,
                status=delivery_status,
                delivery_date=validated_data.get('deliveryDate'),
                description=validated_data.get('description', ''),
                address=order.address1 if order else '',
                phone_number=order.phone1 if order else ''
            )
            
            # Return delivery ID (using integer hash for compatibility)
            import hashlib
            delivery_id_str = str(delivery.id).replace('-', '')
            delivery_id_int = int(hashlib.md5(delivery_id_str.encode()).hexdigest()[:8], 16) % 100000000
            
            return create_success_response(data=delivery_id_int, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating delivery: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_update',
        summary='Update a delivery',
        request=DriverDeliveryUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update Driver Delivery',
                value={
                    "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                    "deliveryUserId": None,
                    "deliveryDate": "2025-11-10T19:31:29.981Z",
                    "setUserId": None,
                    "addressId": 1,
                    "orderId": 1,
                    "examId": None,
                    "requestId": None,
                    "zoneId": None,
                    "preOrderId": None,
                    "status": 0,
                    "description": "string"
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Driver delivery updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 10012,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a delivery matching old Swagger format."""
        try:
            delivery = self.get_object()
            # Drivers can only update their own deliveries
            if not request.user.is_staff and delivery.driver != request.user:
                return create_error_response(
                    error_message='You can only update your own deliveries',
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'error': ['You can only update your own deliveries']}
                )
            
            # Validate input using old Swagger format serializer
            serializer = DriverDeliveryUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update driver if provided
            if validated_data.get('deliveryUserId'):
                try:
                    driver = User.objects.get(id=validated_data['deliveryUserId'])
                    delivery.driver = driver
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data["deliveryUserId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'deliveryUserId': [f'User with ID "{validated_data["deliveryUserId"]}" not found.']}
                    )
            elif validated_data.get('userId'):
                try:
                    driver = User.objects.get(id=validated_data['userId'])
                    delivery.driver = driver
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data["userId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{validated_data["userId"]}" not found.']}
                    )
            
            # Update order if provided
            if validated_data.get('orderId'):
                try:
                    order = Order.objects.get(id=validated_data['orderId'])
                    delivery.order = order
                except Order.DoesNotExist:
                    return create_error_response(
                        error_message=f'Order with ID "{validated_data["orderId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'orderId': [f'Order with ID "{validated_data["orderId"]}" not found.']}
                    )
            
            # Update status if provided
            if validated_data.get('status') is not None:
                status_map = {0: 'assigned', 1: 'in_progress', 2: 'completed', 3: 'cancelled'}
                delivery.status = status_map.get(validated_data['status'], 'assigned')
            
            # Update delivery date if provided
            if validated_data.get('deliveryDate'):
                delivery.delivery_date = validated_data['deliveryDate']
            
            # Update description if provided
            if validated_data.get('description') is not None:
                delivery.description = validated_data['description']
            
            delivery.save()
            
            # Return delivery ID (using integer hash for compatibility)
            import hashlib
            delivery_id_str = str(delivery.id).replace('-', '')
            delivery_id_int = int(hashlib.md5(delivery_id_str.encode()).hexdigest()[:8], 16) % 100000000
            
            return create_success_response(data=delivery_id_int, messages=[])
        except Delivery.DoesNotExist:
            pk = kwargs.get('id', 'unknown')
            return create_error_response(
                error_message=f'Delivery with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Delivery with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating delivery: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_partial_update',
        summary='Partially update a delivery',
        request=DeliverySerializer,
        responses={200: DeliverySerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a delivery matching old Swagger format."""
        try:
            delivery = self.get_object()
            # Drivers can only update their own deliveries
            if not request.user.is_staff and delivery.driver != request.user:
                return create_error_response(
                    error_message='You can only update your own deliveries',
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'error': ['You can only update your own deliveries']}
                )
            return super().partial_update(request, *args, **kwargs)
        except Delivery.DoesNotExist:
            pk = kwargs.get('id', 'unknown')
            return create_error_response(
                error_message=f'Delivery with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Delivery with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating delivery: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_destroy',
        summary='Delete a delivery',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Driver delivery deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": None,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            403: {'description': 'Only managers can delete deliveries'},
            404: {'description': 'Delivery not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a delivery matching old Swagger format."""
        try:
            # Only managers can delete deliveries
            if not request.user.is_staff:
                return create_error_response(
                    error_message='Only managers can delete deliveries',
                    status_code=status.HTTP_403_FORBIDDEN,
                    errors={'error': ['Only managers can delete deliveries']}
                )
            delivery = self.get_object()
            delivery.delete()
            return create_success_response(data=None, messages=[])
        except Delivery.DoesNotExist:
            pk = kwargs.get('id', 'unknown')
            return create_error_response(
                error_message=f'Delivery with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Delivery with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting delivery: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['DriverDelivery'],
        operation_id='driverdelivery_search',
        summary='Search driver deliveries using available filters',
        request=DriverDeliverySearchRequestSerializer,
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
                    ],
                    "status": 0,
                    "userid": "string",
                    "fromDate": "2025-11-10T19:30:40.785Z",
                    "toDate": "2025-11-10T19:30:40.785Z"
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results with nested pagination',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "data": [],
                                "currentPage": 0,
                                "totalPages": 0,
                                "totalCount": 0,
                                "pageSize": 1,
                                "hasPreviousPage": False,
                                "hasNextPage": False,
                                "messages": None,
                                "succeeded": True
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search driver deliveries with pagination and filters matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            serializer = DriverDeliverySearchRequestSerializer(data=request_data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            if page_number == 0:
                page_number = 1
            page_size = validated_data.get('pageSize', 0)
            if page_size == 0:
                page_size = 20
            
            # Build query
            if request.user.is_staff:
                qs = Delivery.objects.all().select_related('driver', 'order')
            else:
                qs = Delivery.objects.filter(driver=request.user).select_related('driver', 'order')
            
            # Filter by userid
            if validated_data.get('userid'):
                try:
                    user = User.objects.get(id=validated_data['userid'])
                    qs = qs.filter(driver=user)
                except User.DoesNotExist:
                    pass  # If user not found, return empty results
            
            # Filter by status
            if validated_data.get('status') is not None:
                status_map = {0: 'assigned', 1: 'in_progress', 2: 'completed', 3: 'cancelled'}
                status_value = status_map.get(validated_data['status'])
                if status_value:
                    qs = qs.filter(status=status_value)
            
            # Filter by date range
            if validated_data.get('fromDate'):
                qs = qs.filter(created_at__gte=validated_data['fromDate'])
            if validated_data.get('toDate'):
                qs = qs.filter(created_at__lte=validated_data['toDate'])
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '').strip()
            if keyword:
                qs = qs.filter(
                    Q(address__icontains=keyword) |
                    Q(phone_number__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Handle orderBy
            order_by = validated_data.get('orderBy', [])
            if order_by and isinstance(order_by, list):
                valid_order_by = []
                for field in order_by:
                    if field and isinstance(field, str):
                        # Map common fields
                        mapped_field = None
                        if field.lower() in ['created_at', 'createdat', 'createdon']:
                            mapped_field = 'created_at'
                        elif field.lower() in ['delivery_date', 'deliverydate']:
                            mapped_field = 'delivery_date'
                        elif field.lower() in ['status']:
                            mapped_field = 'status'
                        
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-created_at')
            else:
                qs = qs.order_by('-created_at')
            
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
            
            # Serialize
            serializer = DeliverySerializer(items, many=True)
            
            # Return in old Swagger format with nested pagination
            return create_success_response(
                data={
                    'data': serializer.data,
                    'currentPage': current_page,
                    'totalPages': total_pages,
                    'totalCount': total_count,
                    'pageSize': page_size,
                    'hasPreviousPage': has_previous_page,
                    'hasNextPage': has_next_page,
                    'messages': None,
                    'succeeded': True
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching deliveries: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['DriverDelivery'],
    operation_id='driverdelivery_myrequests',
    summary='Get my delivery requests',
    description='Get delivery requests for the currently logged-in driver with pagination.',
    request=DriverDeliverySearchRequestSerializer,
    examples=[
        OpenApiExample(
            'My Requests Request (default)',
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
                ],
                "status": 0,
                "userid": "string",
                "fromDate": "2025-11-10T19:29:26.462Z",
                "toDate": "2025-11-10T19:29:26.462Z"
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='My delivery requests with nested pagination',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": {
                            "data": [],
                            "currentPage": 0,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 1,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class DriverDeliveryMyRequestsView(APIView):
    """POST /api/v1/driverdelivery/myrequests"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Get delivery requests for the currently logged-in driver matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            serializer = DriverDeliverySearchRequestSerializer(data=request_data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            if page_number == 0:
                page_number = 1
            page_size = validated_data.get('pageSize', 0)
            if page_size == 0:
                page_size = 20
            
            # Get deliveries for current driver
            qs = Delivery.objects.filter(driver=request.user).select_related('driver', 'order')
            
            # Filter by status
            if validated_data.get('status') is not None:
                status_map = {0: 'assigned', 1: 'in_progress', 2: 'completed', 3: 'cancelled'}
                status_value = status_map.get(validated_data['status'])
                if status_value:
                    qs = qs.filter(status=status_value)
            
            # Filter by date range
            if validated_data.get('fromDate'):
                qs = qs.filter(created_at__gte=validated_data['fromDate'])
            if validated_data.get('toDate'):
                qs = qs.filter(created_at__lte=validated_data['toDate'])
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '').strip()
            if keyword:
                qs = qs.filter(
                    Q(address__icontains=keyword) |
                    Q(phone_number__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Handle orderBy
            order_by = validated_data.get('orderBy', [])
            if order_by and isinstance(order_by, list):
                valid_order_by = []
                for field in order_by:
                    if field and isinstance(field, str):
                        # Map common fields
                        mapped_field = None
                        if field.lower() in ['created_at', 'createdat', 'createdon']:
                            mapped_field = 'created_at'
                        elif field.lower() in ['delivery_date', 'deliverydate']:
                            mapped_field = 'delivery_date'
                        elif field.lower() in ['status']:
                            mapped_field = 'status'
                        
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-created_at')
            else:
                qs = qs.order_by('-created_at')
            
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
            
            # Serialize
            serializer = DeliverySerializer(items, many=True)
            
            # Return in old Swagger format with nested pagination
            return create_success_response(
                data={
                    'data': serializer.data,
                    'currentPage': current_page,
                    'totalPages': total_pages,
                    'totalCount': total_count,
                    'pageSize': page_size,
                    'hasPreviousPage': has_previous_page,
                    'hasNextPage': has_next_page,
                    'messages': None,
                    'succeeded': True
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while fetching delivery requests: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

