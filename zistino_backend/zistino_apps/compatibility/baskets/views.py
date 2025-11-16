"""
Compatibility views for Baskets endpoints.
These views wrap the existing BasketViewSet and add Swagger tags for proper grouping.
All endpoints will appear under "Baskets" folder in Swagger UI.
"""
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from zistino_apps.baskets import views as baskets_views
from zistino_apps.orders.models import Basket, BasketItem
from zistino_apps.baskets.serializers import BasketSerializer
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.authentication.models import User
from .serializers import BasketCreateRequestSerializer, BasketCompatibilitySerializer, BasketClientRequestSerializer
import json


def add_custom_headers(response: Response) -> Response:
    """
    Add custom headers to match old Swagger API response format.
    """
    response['access-control-allow-origin'] = '*'
    response['access-control-expose-headers'] = 'Upload-Offset,Location,Upload-Length,Tus-Version,Tus-Resumable,Tus-Max-Size,Tus-Extension,Upload-Metadata,Upload-Defer-Length,Upload-Concat,Location,Upload-Offset,Upload-Length'
    response['api-supported-versions'] = '1.0'
    response['date'] = 'Wed,12 Nov 2025 05:59:11 GMT'
    response['server'] = 'Microsoft-IIS/10.0'
    response['x-powered-by'] = 'ASP.NET'
    return response


@extend_schema(tags=['Baskets'])
class BasketsViewSet(baskets_views.BasketViewSet):
    """
    Compatibility viewset for baskets endpoints.
    Inherits all functionality from BasketViewSet but with 'Baskets' tag for Swagger grouping.
    All endpoints will appear under "Baskets" folder in Swagger UI.
    """
    
    def retrieve(self, request, pk=None):
        """Get basket by ID - returns basket by ID or user's basket if pk not found"""
        # Try to get basket by pk if provided
        if pk:
            try:
                basket = Basket.objects.get(pk=pk, user=request.user)
            except Basket.DoesNotExist:
                # If not found, return user's active basket
                basket = self._get_or_create_active_basket(request.user)
        else:
            basket = self._get_or_create_active_basket(request.user)
        
        serializer = BasketCompatibilitySerializer(basket)
        # Return with messages as empty array (not null) matching old Swagger format
        return create_success_response(data=serializer.data, messages=[])
    
    def update(self, request, pk=None):
        """Update basket by ID - updates user's basket"""
        basket = self._get_or_create_active_basket(request.user)
        # Update basket if needed (for now, just return current basket)
        # You can add update logic here if needed
        return Response(BasketSerializer(basket).data)
    
    def destroy(self, request, pk=None):
        """Delete basket by ID - clears user's basket items"""
        basket = self._get_or_create_active_basket(request.user)
        # Clear all items from basket
        basket.items.all().delete()
        self._recalculate_basket(basket)
        return Response(BasketSerializer(basket).data)
    
    def create(self, request):
        """Create basket - same as list (gets or creates user's basket)"""
        return self.list(request)
    
    def client_post(self, request):
        """POST /api/v1/baskets/client - Set Basket for currently logged in user"""
        # This is similar to add_item but for the /client endpoint
        # For now, we'll use the same logic as create/add_item
        basket = self._get_or_create_active_basket(request.user)
        
        # If request has basket items data, add them
        if 'items' in request.data or 'product' in request.data:
            # Handle adding items to basket (similar to add_item action)
            product_id = request.data.get("product") or request.data.get("product_id")
            if product_id:
                quantity = int(request.data.get("quantity", 1))
                price = request.data.get("price") or request.data.get("unit_price")
                name = request.data.get("name", "")
                description = request.data.get("description", "")
                master_image = request.data.get("master_image", "")
                discount_percent = int(request.data.get("discount_percent", 0))
                
                if price is not None:
                    from zistino_apps.orders.models import BasketItem
                    item, created = BasketItem.objects.get_or_create(
                        basket=basket,
                        product_id=product_id,
                        defaults={
                            "name": name,
                            "description": description,
                            "master_image": master_image,
                            "discount_percent": discount_percent,
                            "quantity": quantity,
                            "price": price,
                            "item_total": int(quantity) * int(price),
                        },
                    )
                    if not created:
                        item.quantity = item.quantity + quantity
                        item.price = price
                        item.item_total = int(item.quantity) * int(item.price)
                        item.save(update_fields=["quantity", "price", "item_total"])
                    self._recalculate_basket(basket)
        
        return Response(BasketSerializer(basket).data)


# ============================================================================
# SEPARATE APIView CLASSES FOR CUSTOM ENDPOINTS
# These are needed so Swagger can properly document them
# ============================================================================

@extend_schema(
    tags=['Baskets'],
    operation_id='baskets_client_check',
    summary='Check Basket of currently logged in user',
    description='Check Basket of currently logged in user matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Basket data',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': {
                            'id': 1,
                            'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                            'items': 'string',
                            'isEmpty': True,
                            'totalItems': 0,
                            'totalUniqueItems': 0,
                            'cartTotal': 0
                        },
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class BasketsClientCheckView(APIView):
    """GET /api/v1/baskets/client/check - Check Basket of currently logged in user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get basket matching old Swagger format."""
        viewset = BasketsViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        basket = viewset._get_or_create_active_basket(request.user)
        serializer = BasketCompatibilitySerializer(basket)
        return create_success_response(data=serializer.data)


class BasketsClientView(APIView):
    """GET/POST /api/v1/baskets/client - Get/Set Basket of currently logged in user"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_client_get',
        summary='Get Basket of currently logged in user',
        description='Get Basket of currently logged in user matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Basket data',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 2,
                                'userId': '7b84eae6-aadf-43ca-895f-d47680ea0c51',
                                'items': 'rwert',
                                'isEmpty': True,
                                'totalItems': 10,
                                'totalUniqueItems': 0,
                                'cartTotal': 10
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        """Get basket matching old Swagger format."""
        viewset = BasketsViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        basket = viewset._get_or_create_active_basket(request.user)
        serializer = BasketCompatibilitySerializer(basket)
        # Return with messages as empty array (not null) matching old Swagger format
        return create_success_response(data=serializer.data, messages=[])
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_client_post',
        summary='Set Basket for currently logged in user',
        description='Set Basket for currently logged in user matching old Swagger format.',
        request=BasketClientRequestSerializer,
        examples=[
            OpenApiExample(
                'Set basket',
                value={
                    'items': 'string',
                    'isEmpty': True,
                    'totalItems': 0,
                    'totalUniqueItems': 0,
                    'cartTotal': 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Basket set successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'items': 'string',
                                'isEmpty': True,
                                'totalItems': 0,
                                'totalUniqueItems': 0,
                                'cartTotal': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def post(self, request):
        """Set basket matching old Swagger format. Returns response with custom headers."""
        # Validate input using old Swagger format serializer
        input_serializer = BasketClientRequestSerializer(data=request.data)
        if not input_serializer.is_valid():
            errors = {}
            for field, error_list in input_serializer.errors.items():
                errors[field] = [str(error) for error in error_list]
            error_response = create_error_response(
                error_message='Validation failed',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=errors
            )
            return add_custom_headers(error_response)
        
        validated_data = input_serializer.validated_data
        
        viewset = BasketsViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        basket = viewset._get_or_create_active_basket(request.user)
        
        # Update basket fields if provided
        if 'isEmpty' in validated_data:
            basket.is_empty = validated_data.get('isEmpty')
        if 'totalItems' in validated_data:
            basket.total_items = validated_data.get('totalItems')
        if 'totalUniqueItems' in validated_data:
            basket.total_unique_items = validated_data.get('totalUniqueItems')
        if 'cartTotal' in validated_data:
            basket.cart_total = validated_data.get('cartTotal')
        basket.save()
        
        # Parse items if provided (items is a JSON string in old Swagger)
        items_str = validated_data.get('items')
        if items_str and items_str.strip() and items_str != 'string':
            try:
                items_data = json.loads(items_str)
                if isinstance(items_data, list):
                    # Clear existing items and add new ones
                    basket.items.all().delete()
                    for item_data in items_data:
                        if isinstance(item_data, dict):
                            product_id = item_data.get('product') or item_data.get('product_id') or item_data.get('productId')
                            quantity = int(item_data.get('quantity', 1))
                            price = item_data.get('price') or item_data.get('unit_price') or item_data.get('unitPrice', 0)
                            name = item_data.get('name', '')
                            description = item_data.get('description', '')
                            master_image = item_data.get('master_image') or item_data.get('masterImage', '')
                            discount_percent = int(item_data.get('discount_percent') or item_data.get('discountPercent', 0))
                            
                            if product_id and price is not None:
                                BasketItem.objects.create(
                                    basket=basket,
                                    product_id=str(product_id),
                                    name=name,
                                    description=description,
                                    master_image=master_image,
                                    discount_percent=discount_percent,
                                    quantity=quantity,
                                    price=int(price),
                                    item_total=int(quantity) * int(price),
                                )
                    # Recalculate basket
                    viewset._recalculate_basket(basket)
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                # If items parsing fails, continue without items
                pass
        
        # Return basket in old Swagger format with custom headers
        serializer = BasketCompatibilitySerializer(basket)
        response = create_success_response(data=serializer.data)
        return add_custom_headers(response)


@extend_schema(
    tags=['Baskets'],
    operation_id='baskets_dapper',
    summary='Get baskets (dapper context)',
    description='Get baskets in dapper context. If id query parameter is provided, returns single basket.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Basket ID. If provided, returns single basket.'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Basket data',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': {
                            'id': 1,
                            'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                            'items': 'string',
                            'isEmpty': True,
                            'totalItems': 0,
                            'totalUniqueItems': 0,
                            'cartTotal': 0
                        },
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class BasketsDapperView(APIView):
    """GET /api/v1/baskets/dapper - Get baskets (dapper context)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get basket(s) in dapper context matching old Swagger format."""
        basket_id = request.query_params.get('id')
        
        if basket_id:
            # Return single basket by ID
            try:
                basket = Basket.objects.get(id=int(basket_id), user=request.user)
                serializer = BasketCompatibilitySerializer(basket)
                return create_success_response(data=serializer.data)
            except (Basket.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Basket with ID "{basket_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return current user's basket
            viewset = BasketsViewSet()
            viewset.request = request
            viewset.format_kwarg = None
            basket = viewset._get_or_create_active_basket(request.user)
            serializer = BasketCompatibilitySerializer(basket)
            return create_success_response(data=serializer.data)


# ============================================================================
# STANDARD REST ENDPOINTS - Separate APIView classes for Swagger documentation
# ============================================================================

class BasketsListView(APIView):
    """GET/POST /api/v1/baskets - List/Create basket"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_list',
        summary='Get basket',
        description='Get the current user\'s shopping basket with all items.',
        responses={200: BasketSerializer}
    )
    def get(self, request):
        viewset = BasketsViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        return viewset.list(request)
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_create',
        summary='Create basket',
        description='Creates a new basket matching old Swagger format.',
        request=BasketCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create basket',
                value={
                    'id': 0,
                    'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'items': 'string',
                    'isEmpty': True,
                    'totalItems': 0,
                    'totalUniqueItems': 0,
                    'cartTotal': 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Basket created successfully',
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
            400: {'description': 'Validation error'},
            404: {'description': 'User not found'}
        }
    )
    def post(self, request):
        """Create basket matching old Swagger format. Returns basket ID."""
        # Validate input using old Swagger format serializer
        input_serializer = BasketCreateRequestSerializer(data=request.data)
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
        
        # Get or create user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{user_id}" does not exist.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{user_id}" not found.']}
            )
        
        # Get or create basket for user
        basket = Basket.objects.filter(user=user).order_by('-id').first()
        if not basket:
            basket = Basket.objects.create(
                user=user,
                is_empty=validated_data.get('isEmpty', True),
                total_items=validated_data.get('totalItems', 0),
                total_unique_items=validated_data.get('totalUniqueItems', 0),
                cart_total=validated_data.get('cartTotal', 0)
            )
        else:
            # Update existing basket if values are provided
            if 'isEmpty' in validated_data:
                basket.is_empty = validated_data.get('isEmpty')
            if 'totalItems' in validated_data:
                basket.total_items = validated_data.get('totalItems')
            if 'totalUniqueItems' in validated_data:
                basket.total_unique_items = validated_data.get('totalUniqueItems')
            if 'cartTotal' in validated_data:
                basket.cart_total = validated_data.get('cartTotal')
            basket.save()
        
        # Parse items if provided (items is a JSON string in old Swagger)
        items_str = validated_data.get('items')
        if items_str and items_str.strip() and items_str != 'string':
            try:
                items_data = json.loads(items_str)
                if isinstance(items_data, list):
                    # Add items to basket
                    for item_data in items_data:
                        if isinstance(item_data, dict):
                            product_id = item_data.get('product') or item_data.get('product_id') or item_data.get('productId')
                            quantity = int(item_data.get('quantity', 1))
                            price = item_data.get('price') or item_data.get('unit_price') or item_data.get('unitPrice', 0)
                            name = item_data.get('name', '')
                            description = item_data.get('description', '')
                            master_image = item_data.get('master_image') or item_data.get('masterImage', '')
                            discount_percent = int(item_data.get('discount_percent') or item_data.get('discountPercent', 0))
                            
                            if product_id and price is not None:
                                BasketItem.objects.get_or_create(
                                    basket=basket,
                                    product_id=str(product_id),
                                    defaults={
                                        'name': name,
                                        'description': description,
                                        'master_image': master_image,
                                        'discount_percent': discount_percent,
                                        'quantity': quantity,
                                        'price': int(price),
                                        'item_total': int(quantity) * int(price),
                                    }
                                )
                    # Recalculate basket
                    viewset = BasketsViewSet()
                    viewset._recalculate_basket(basket)
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                # If items parsing fails, continue without items
                pass
        
        # Return just the basket ID wrapped in standard response
        return create_success_response(data=basket.id)


class BasketsDetailView(APIView):
    """GET/PUT/DELETE /api/v1/baskets/{id} - Retrieve/Update/Delete basket"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_retrieve',
        summary='Retrieves a basket by its ID',
        description='Retrieves a basket by its ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Basket data',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'items': 'string',
                                'isEmpty': True,
                                'totalItems': 0,
                                'totalUniqueItems': 0,
                                'cartTotal': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Basket not found'}
        }
    )
    def get(self, request, pk):
        """Get basket by ID matching old Swagger format."""
        try:
            basket = Basket.objects.get(id=int(pk), user=request.user)
            serializer = BasketCompatibilitySerializer(basket)
            return create_success_response(data=serializer.data)
        except (Basket.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Basket with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_update',
        summary='Updates an existing basket by its ID',
        description='Updates an existing basket by its ID matching old Swagger format.',
        request=BasketCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update basket',
                value={
                    'id': 0,
                    'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'items': 'string',
                    'isEmpty': True,
                    'totalItems': 0,
                    'totalUniqueItems': 0,
                    'cartTotal': 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Basket updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'items': 'string',
                                'isEmpty': True,
                                'totalItems': 0,
                                'totalUniqueItems': 0,
                                'cartTotal': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Basket not found'}
        }
    )
    def put(self, request, pk):
        """Update basket by ID matching old Swagger format."""
        try:
            basket = Basket.objects.get(id=int(pk), user=request.user)
        except (Basket.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Basket with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input using old Swagger format serializer
        input_serializer = BasketCreateRequestSerializer(data=request.data)
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
        
        # Update basket fields
        if 'isEmpty' in validated_data:
            basket.is_empty = validated_data.get('isEmpty')
        if 'totalItems' in validated_data:
            basket.total_items = validated_data.get('totalItems')
        if 'totalUniqueItems' in validated_data:
            basket.total_unique_items = validated_data.get('totalUniqueItems')
        if 'cartTotal' in validated_data:
            basket.cart_total = validated_data.get('cartTotal')
        basket.save()
        
        # Parse items if provided
        items_str = validated_data.get('items')
        if items_str and items_str.strip() and items_str != 'string':
            try:
                items_data = json.loads(items_str)
                if isinstance(items_data, list):
                    # Clear existing items and add new ones
                    basket.items.all().delete()
                    for item_data in items_data:
                        if isinstance(item_data, dict):
                            product_id = item_data.get('product') or item_data.get('product_id') or item_data.get('productId')
                            quantity = int(item_data.get('quantity', 1))
                            price = item_data.get('price') or item_data.get('unit_price') or item_data.get('unitPrice', 0)
                            name = item_data.get('name', '')
                            description = item_data.get('description', '')
                            master_image = item_data.get('master_image') or item_data.get('masterImage', '')
                            discount_percent = int(item_data.get('discount_percent') or item_data.get('discountPercent', 0))
                            
                            if product_id and price is not None:
                                BasketItem.objects.create(
                                    basket=basket,
                                    product_id=str(product_id),
                                    name=name,
                                    description=description,
                                    master_image=master_image,
                                    discount_percent=discount_percent,
                                    quantity=quantity,
                                    price=int(price),
                                    item_total=int(quantity) * int(price),
                                )
                    # Recalculate basket
                    viewset = BasketsViewSet()
                    viewset._recalculate_basket(basket)
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                # If items parsing fails, continue without items
                pass
        
        # Return updated basket in old Swagger format
        serializer = BasketCompatibilitySerializer(basket)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Baskets'],
        operation_id='baskets_delete',
        summary='Deletes a basket by its ID',
        description='Deletes a basket by its ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Basket deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'items': 'string',
                                'isEmpty': True,
                                'totalItems': 0,
                                'totalUniqueItems': 0,
                                'cartTotal': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Basket not found'}
        }
    )
    def delete(self, request, pk):
        """Delete basket by ID matching old Swagger format."""
        try:
            basket = Basket.objects.get(id=int(pk), user=request.user)
            # Clear all items from basket
            basket.items.all().delete()
            # Recalculate basket
            viewset = BasketsViewSet()
            viewset._recalculate_basket(basket)
            # Return basket in old Swagger format
            serializer = BasketCompatibilitySerializer(basket)
            return create_success_response(data=serializer.data)
        except (Basket.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Basket with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

