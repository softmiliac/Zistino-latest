"""
Compatibility views for Likes endpoints.
All endpoints will appear under "Likes" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Likes
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import uuid

from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .models import Like
from .serializers import LikeSerializer, LikeCreateSerializer, LikeStatusSerializer


@extend_schema(
    tags=['Likes'],
    operation_id='likes_client_create',
    summary='Like an item',
    description='Like a product or other item matching old Swagger format.',
    request=LikeCreateSerializer,
    examples=[
        OpenApiExample(
            'Like item',
            value={
                'id': 0,
                'productId': 'string',
                'itemId': 0,
                'type': 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Item liked successfully',
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
class LikesClientView(APIView):
    """POST /api/v1/likes/client - Like an item"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Like an item (product, blog post, etc.) matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input using old Swagger format serializer
            serializer = LikeCreateSerializer(data=request_data)
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
            
            # Get productId and map to item_id
            product_id_str = validated_data.get('productId', '')
            if not product_id_str or product_id_str == 'string':
                return create_error_response(
                    error_message='productId is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'productId': ['productId is required.']}
                )
            
            try:
                item_id = uuid.UUID(product_id_str)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message='productId must be a valid UUID.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'productId': ['productId must be a valid UUID.']}
                )
            
            # Map integer type to string item_type
            type_mapping = {
                0: 'product',
                1: 'item',
                2: 'blog',
                3: 'comment'
            }
            type_value = validated_data.get('type', 0)
            item_type = type_mapping.get(type_value, 'product')
            
            # Check if like already exists
            like, created = Like.objects.get_or_create(
                user=request.user,
                item_id=item_id,
                item_type=item_type,
                defaults={}
            )
            
            # Convert UUID to integer for response (using hash for consistent mapping)
            import hashlib
            like_id_hash = int(hashlib.md5(str(like.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            
            # Return response matching old Swagger format
            return create_success_response(data=like_id_hash, messages=[], status_code=status.HTTP_200_OK)
        
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
    tags=['Likes'],
    operation_id='likes_client_unlike',
    summary='Unlike an item',
    description='Remove like from a product or other item matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='productId',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Product ID (UUID)'
        ),
        OpenApiParameter(
            name='Type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            default=0,
            description='Type: 0=product, 1=item, 2=blog, 3=comment'
        ),
        OpenApiParameter(
            name='ItemId',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            default=0,
            description='Item ID (not used, for compatibility only)'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Item unliked successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': 0,
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        ),
        400: {'description': 'Validation error'}
    }
)
class LikesClientUnlikeView(APIView):
    """DELETE /api/v1/likes/client/unlike - Unlike an item"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Unlike an item matching old Swagger format."""
        try:
            # Get parameters from query string
            product_id_str = request.query_params.get('productId') or request.query_params.get('product_id')
            type_value = int(request.query_params.get('Type', 0))
            item_id = request.query_params.get('ItemId', 0)  # Not used, for compatibility only
            
            if not product_id_str:
                return create_error_response(
                    error_message='productId is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'productId': ['productId is required.']}
                )
            
            try:
                item_id_uuid = uuid.UUID(product_id_str)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message='productId must be a valid UUID.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'productId': ['productId must be a valid UUID.']}
                )
            
            # Map integer type to string item_type
            type_mapping = {
                0: 'product',
                1: 'item',
                2: 'blog',
                3: 'comment'
            }
            item_type = type_mapping.get(type_value, 'product')
            
            try:
                like = Like.objects.get(
                    user=request.user,
                    item_id=item_id_uuid,
                    item_type=item_type
                )
                like.delete()
                return create_success_response(data=0, messages=[], status_code=status.HTTP_200_OK)
            except Like.DoesNotExist:
                # Return success even if not liked (matching old Swagger behavior)
                return create_success_response(data=0, messages=[], status_code=status.HTTP_200_OK)
        
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
    tags=['Likes'],
    operation_id='likes_client_item_status',
    summary='Get like status for item',
    description='Get like status for a specific item matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='ItemId',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='Item ID (can be 0 or UUID)'
        ),
        OpenApiParameter(
            name='Type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            default=0,
            description='Type: 0=product, 1=item, 2=blog, 3=comment'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Like status',
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
        )
    }
)
class LikesClientItemStatusView(APIView):
    """GET /api/v1/likes/client/item/{ItemId}/type?Type=0 - Get like status for item"""
    permission_classes = [IsAuthenticated]

    def get(self, request, ItemId):
        """Get like status for an item matching old Swagger format."""
        try:
            # Get Type from query parameter
            type_value = int(request.query_params.get('Type', 0))
            
            # Map integer type to string item_type
            type_mapping = {
                0: 'product',
                1: 'item',
                2: 'blog',
                3: 'comment'
            }
            item_type = type_mapping.get(type_value, 'product')
            
            # Handle ItemId - can be integer (0) or UUID
            # If ItemId is 0 or not a valid UUID, return 0 (not liked)
            if ItemId == '0' or ItemId == 0:
                return create_success_response(data=0, messages=[], status_code=status.HTTP_200_OK)
            
            try:
                item_id_uuid = uuid.UUID(str(ItemId))
            except (ValueError, TypeError):
                # If ItemId is not a valid UUID, return 0 (not liked)
                return create_success_response(data=0, messages=[], status_code=status.HTTP_200_OK)
            
            # Check if current user has liked this item
            is_liked = Like.objects.filter(
                user=request.user,
                item_id=item_id_uuid,
                item_type=item_type
            ).exists()
            
            # Return 1 if liked, 0 if not (matching old Swagger format)
            data_value = 1 if is_liked else 0
            
            return create_success_response(data=data_value, messages=[], status_code=status.HTTP_200_OK)
        
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
    tags=['Likes'],
    operation_id='likes_client_product_status',
    summary='Get like status for product',
    description='Get like status for a specific product matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='ProductId',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            required=True,
            description='Product ID (UUID)'
        ),
        OpenApiParameter(
            name='Type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            default=0,
            description='Type: 0=product, 1=item, 2=blog, 3=comment'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Like status',
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
        )
    }
)
class LikesClientProductStatusView(APIView):
    """GET /api/v1/likes/client/{ProductId}/type?Type=0 - Get like status for product"""
    permission_classes = [IsAuthenticated]

    def get(self, request, ProductId):
        """Get like status for a product matching old Swagger format."""
        try:
            # Get Type from query parameter
            type_value = int(request.query_params.get('Type', 0))
            
            # Map integer type to string item_type
            type_mapping = {
                0: 'product',
                1: 'item',
                2: 'blog',
                3: 'comment'
            }
            item_type = type_mapping.get(type_value, 'product')
            
            # Check if current user has liked this product
            is_liked = Like.objects.filter(
                user=request.user,
                item_id=ProductId,
                item_type=item_type
            ).exists()
            
            # Return 1 if liked, 0 if not (matching old Swagger format)
            data_value = 1 if is_liked else 0
            
            return create_success_response(data=data_value, messages=[], status_code=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

