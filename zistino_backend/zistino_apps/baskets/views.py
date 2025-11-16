from django.db import transaction
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from zistino_apps.orders.models import Basket, BasketItem
from .serializers import BasketSerializer, BasketItemSerializer, ApplyCouponRequestSerializer
from zistino_apps.payments.models import Coupon, BasketDiscount


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET",):
            return True
        return request.user and request.user.is_authenticated


@extend_schema(tags=['basket'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Baskets" folder instead
class BasketViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_or_create_active_basket(self, user):
        basket = Basket.objects.filter(user=user).order_by('-id').first()
        if basket:
            return basket
        return Basket.objects.create(user=user)

    @extend_schema(
        tags=['Customer'],
        operation_id='basket_list',
        summary='Get user basket',
        description='Get the current user\'s shopping basket with all items.',
        responses={
            200: {
                'description': 'Basket retrieved successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'basket_with_items': {
                                'summary': 'Basket with items',
                                'value': {
                                    'id': 1,
                                    'user': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                    'total_items': 5,
                                    'total_unique_items': 3,
                                    'cart_total': 150000,
                                    'is_empty': False,
                                    'items': [
                                        {
                                            'id': 1,
                                            'product': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'name': 'Product Name',
                                            'quantity': 2,
                                            'price': 50000,
                                            'item_total': 100000,
                                            'discount_percent': 10
                                        }
                                    ]
                                }
                            },
                            'empty_basket': {
                                'summary': 'Empty basket',
                                'value': {
                                    'id': 1,
                                    'user': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                    'total_items': 0,
                                    'total_unique_items': 0,
                                    'cart_total': 0,
                                    'is_empty': True,
                                    'items': []
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def list(self, request):
        basket = Basket.objects.filter(user=request.user).first()
        if not basket:
            basket = self._get_or_create_active_basket(request.user)
        data = BasketSerializer(basket).data
        return Response(data)

    @extend_schema(
        tags=['Customer'],
        operation_id='basket_add_item',
        summary='Add item to basket',
        description='Add a product to the user\'s shopping basket. If the product already exists, the quantity will be increased.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product': {'type': 'string', 'format': 'uuid', 'description': 'Product UUID'},
                    'product_id': {'type': 'string', 'format': 'uuid', 'description': 'Alternative field name for product UUID'},
                    'quantity': {'type': 'integer', 'description': 'Quantity to add (default: 1)'},
                    'price': {'type': 'integer', 'description': 'Product price in Rials'},
                    'unit_price': {'type': 'integer', 'description': 'Alternative field name for price'},
                    'name': {'type': 'string', 'description': 'Product name (optional)'},
                    'description': {'type': 'string', 'description': 'Product description (optional)'},
                    'master_image': {'type': 'string', 'description': 'Product image URL (optional)'},
                    'discount_percent': {'type': 'integer', 'description': 'Discount percentage (default: 0)'}
                },
                'required': ['product', 'price']
            }
        },
        examples=[
            OpenApiExample(
                'Add product to basket',
                value={
                    'product': '46e818ce-0518-4c64-8438-27bc7163a706',
                    'quantity': 2,
                    'price': 50000,
                    'name': 'Recyclable Plastic Bottles',
                    'discount_percent': 10
                }
            ),
            OpenApiExample(
                'Add product with all fields',
                value={
                    'product_id': '46e818ce-0518-4c64-8438-27bc7163a706',
                    'quantity': 1,
                    'unit_price': 75000,
                    'name': 'Paper Waste',
                    'description': 'Clean paper waste',
                    'master_image': 'https://example.com/image.jpg',
                    'discount_percent': 5
                }
            )
        ],
        responses={
            201: {
                'description': 'Item added successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'id': 1,
                            'user': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                            'total_items': 3,
                            'cart_total': 150000,
                            'items': [
                                {
                                    'id': 1,
                                    'product': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'quantity': 2,
                                    'price': 50000,
                                    'item_total': 100000
                                }
                            ]
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'product_id and price are required'
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=["post"], url_path="items")
    @transaction.atomic
    def add_item(self, request):
        basket = self._get_or_create_active_basket(request.user)
        product_id = request.data.get("product") or request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        price = request.data.get("price") or request.data.get("unit_price")
        name = request.data.get("name", "")
        description = request.data.get("description", "")
        master_image = request.data.get("master_image", "")
        discount_percent = int(request.data.get("discount_percent", 0))
        if not product_id or price is None:
            return Response({"detail": "product_id and price are required"}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response(BasketSerializer(basket).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Customer'],
        operation_id='basket_update_item',
        summary='Update basket item quantity',
        description='Update the quantity or price of an item in the basket. If quantity is set to 0 or less, the item will be removed.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'quantity': {'type': 'integer', 'description': 'New quantity (if 0 or less, item is removed)'},
                    'price': {'type': 'integer', 'description': 'New price in Rials (optional)'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Update quantity',
                value={
                    'quantity': 5,
                    'price': 50000
                }
            ),
            OpenApiExample(
                'Remove item (set quantity to 0)',
                value={
                    'quantity': 0
                }
            )
        ],
        responses={
            200: {
                'description': 'Item updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'id': 1,
                            'user': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                            'total_items': 5,
                            'cart_total': 250000,
                            'items': []
                        }
                    }
                }
            },
            404: {
                'description': 'Item not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Item not found'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=["put"], url_path="items")
    @transaction.atomic
    def update_item(self, request, pk=None):
        basket = self._get_or_create_active_basket(request.user)
        try:
            item = basket.items.get(pk=pk)
        except BasketItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(request.data.get("quantity", item.quantity))
        price = request.data.get("price", item.price)
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.price = price
            item.item_total = int(item.quantity) * int(item.price)
            item.save(update_fields=["quantity", "price", "item_total"])
        self._recalculate_basket(basket)
        return Response(BasketSerializer(basket).data)

    @extend_schema(
        tags=['Customer'],
        operation_id='basket_remove_item',
        summary='Remove item from basket',
        description='Remove an item from the shopping basket by item ID.',
        responses={
            200: {
                'description': 'Item removed successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'id': 1,
                            'user': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                            'total_items': 2,
                            'cart_total': 100000,
                            'items': []
                        }
                    }
                }
            },
            404: {
                'description': 'Item not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Item not found'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=["delete"], url_path="items")
    @transaction.atomic
    def remove_item(self, request, pk=None):
        basket = self._get_or_create_active_basket(request.user)
        deleted, _ = basket.items.filter(pk=pk).delete()
        if not deleted:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        self._recalculate_basket(basket)
        return Response(BasketSerializer(basket).data)

    @extend_schema(
        request=ApplyCouponRequestSerializer,
        examples=[
            OpenApiExample('Apply coupon', value={"code": "SUMMER25"}),
            OpenApiExample('Remove coupon', value={"code": ""}),
        ],
        tags=['Customer']
    )
    @action(detail=False, methods=["post"], url_path="apply-coupon")
    @transaction.atomic
    def apply_coupon(self, request):
        basket = self._get_or_create_active_basket(request.user)
        code = (request.data.get("code") or request.data.get("key") or "").strip()
        if not code:
            # clear coupon
            BasketDiscount.objects.filter(basket=basket).delete()
            self._recalculate_basket(basket)
            return Response(BasketSerializer(basket).data)
        try:
            coupon = Coupon.objects.get(key=code, status=1)
        except Coupon.DoesNotExist:
            return Response({"detail": "invalid coupon"}, status=status.HTTP_400_BAD_REQUEST)
        # set/update discount
        items_total = sum([int(i.item_total) for i in basket.items.all()])
        discount_amount = min(int(coupon.amount), items_total)
        BasketDiscount.objects.update_or_create(basket=basket, defaults={"coupon": coupon, "amount": discount_amount})
        self._recalculate_basket(basket)
        data = BasketSerializer(basket).data
        data.update({"applied_coupon": {"key": coupon.key, "amount": discount_amount}})
        return Response(data)

    def _recalculate_basket(self, basket: Basket) -> None:
        items = list(basket.items.all())
        total_items = sum([i.quantity for i in items])
        total_unique = len(items)
        cart_total = sum([int(i.item_total) for i in items])
        # subtract discount if exists
        bd = getattr(basket, 'discount', None)
        if bd:
            cart_total = max(0, cart_total - int(bd.amount))
        Basket.objects.filter(pk=basket.pk).update(
            total_items=total_items,
            total_unique_items=total_unique,
            cart_total=cart_total,
            is_empty=(total_items == 0),
        )


