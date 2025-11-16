"""
Compatibility views for AdsItems endpoints.
All endpoints will appear under "AdsItems" folder in Swagger UI.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.compatibility.adszones.models import AdsZone
from .models import AdsItem
from .serializers import (
    AdsItemCreateRequestSerializer,
    AdsItemCompatibilitySerializer,
    AdsItemSearchRequestSerializer,
    AdsItemSearchResponseSerializer
)


@extend_schema(tags=['AdsItems'])
class AdsItemsViewSet(viewsets.ViewSet):
    """
    Compatibility viewset for ads items endpoints.
    All endpoints will appear under "AdsItems" folder in Swagger UI.
    """
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated if needed

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_list',
        summary='List all ads items',
        description='Get list of all ads items matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of ads items',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'adsZoneId': 1,
                                    'filePath': 'string',
                                    'fileType': 0,
                                    'fromTime': '2025-11-09T06:54:24.692',
                                    'toTime': '2025-11-09T06:54:24.692',
                                    'locale': 'fa'
                                }
                            ],
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def list(self, request):
        """Get list of ads items matching old Swagger format."""
        ads_items = AdsItem.objects.filter(is_active=True).order_by('-created_at')
        serializer = AdsItemCompatibilitySerializer(ads_items, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_create',
        summary='Create new ad item',
        description='Create a new advertisement item matching old Swagger format.',
        request=AdsItemCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create ad item',
                value={
                    'adsZoneId': 1,
                    'filePath': 'string',
                    'fileType': 0,
                    'fromTime': '2025-11-09T06:54:24.692Z',
                    'toTime': '2025-11-09T06:54:24.692Z',
                    'locale': 'fa'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad item created successfully',
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
            404: {'description': 'Ads zone not found'}
        }
    )
    def create(self, request):
        """Create new ad item matching old Swagger format. Returns item ID."""
        # Validate input using old Swagger format serializer
        input_serializer = AdsItemCreateRequestSerializer(data=request.data)
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
        
        # Check if ads zone exists
        ads_zone_id = validated_data.get('adsZoneId')
        try:
            ads_zone = AdsZone.objects.get(id=ads_zone_id, is_active=True)
        except AdsZone.DoesNotExist:
            return create_error_response(
                error_message=f'Ads zone with ID "{ads_zone_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'adsZoneId': [f'Ads zone with ID "{ads_zone_id}" not found.']}
            )
        
        # Create ad item
        ads_item = AdsItem.objects.create(
            ads_zone=ads_zone,
            file_path=validated_data.get('filePath'),
            file_type=validated_data.get('fileType', 0),
            from_time=validated_data.get('fromTime'),
            to_time=validated_data.get('toTime'),
            locale=validated_data.get('locale', 'en')
        )
        
        # Return just the item ID wrapped in standard response
        return create_success_response(data=ads_item.id)  # 200 OK to match old Swagger

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_retrieve',
        summary='Get ad item by ID',
        description='Retrieve an ad item by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ad item ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad item details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'adsZoneId': 1,
                                'filePath': 'string',
                                'fileType': 0,
                                'fromTime': '2025-11-09T06:54:24.692',
                                'toTime': '2025-11-09T06:54:24.692',
                                'locale': 'fa'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Ad item not found'}
        }
    )
    def retrieve(self, request, id=None):
        """Get ad item by ID matching old Swagger format."""
        try:
            ads_item = AdsItem.objects.get(id=id, is_active=True)
            serializer = AdsItemCompatibilitySerializer(ads_item)
            return create_success_response(data=serializer.data)
        except AdsItem.DoesNotExist:
            return create_error_response(
                error_message=f'Ad item with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_update',
        summary='Update ad item',
        description='Update an existing ad item matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ad item ID'
            )
        ],
        request=AdsItemCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update ad item',
                value={
                    'adsZoneId': 1,
                    'filePath': 'string',
                    'fileType': 0,
                    'fromTime': '2025-11-09T06:54:24.692Z',
                    'toTime': '2025-11-09T06:54:24.692Z',
                    'locale': 'fa'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad item updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'adsZoneId': 1,
                                'filePath': 'string',
                                'fileType': 0,
                                'fromTime': '2025-11-09T06:54:24.692',
                                'toTime': '2025-11-09T06:54:24.692',
                                'locale': 'fa'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Ad item not found'}
        }
    )
    def update(self, request, id=None):
        """Update ad item matching old Swagger format."""
        try:
            ads_item = AdsItem.objects.get(id=id, is_active=True)
        except AdsItem.DoesNotExist:
            return create_error_response(
                error_message=f'Ad item with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = AdsItemCreateRequestSerializer(data=request.data)
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
        
        # Check if ads zone exists (if adsZoneId is provided)
        ads_zone_id = validated_data.get('adsZoneId')
        if ads_zone_id:
            try:
                ads_zone = AdsZone.objects.get(id=ads_zone_id, is_active=True)
                ads_item.ads_zone = ads_zone
            except AdsZone.DoesNotExist:
                return create_error_response(
                    error_message=f'Ads zone with ID "{ads_zone_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'adsZoneId': [f'Ads zone with ID "{ads_zone_id}" not found.']}
                )
        
        # Update ad item fields
        if 'filePath' in validated_data:
            ads_item.file_path = validated_data.get('filePath')
        if 'fileType' in validated_data:
            ads_item.file_type = validated_data.get('fileType', 0)
        if 'fromTime' in validated_data:
            ads_item.from_time = validated_data.get('fromTime')
        if 'toTime' in validated_data:
            ads_item.to_time = validated_data.get('toTime')
        if 'locale' in validated_data:
            ads_item.locale = validated_data.get('locale', 'en')
        
        ads_item.save()
        
        # Return updated item
        serializer = AdsItemCompatibilitySerializer(ads_item)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_destroy',
        summary='Delete ad item',
        description='Delete an ad item by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ad item ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad item deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Ad item not found'}
        }
    )
    def destroy(self, request, id=None):
        """Delete ad item matching old Swagger format."""
        try:
            ads_item = AdsItem.objects.get(id=id, is_active=True)
            # Soft delete by setting is_active to False
            ads_item.is_active = False
            ads_item.save()
            return create_success_response(data=None)
        except AdsItem.DoesNotExist:
            return create_error_response(
                error_message=f'Ad item with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_dapper',
        summary='Get ads items (dapper context)',
        description='Get ads items in dapper context. If id query parameter is provided, returns single item.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Ad item ID. If provided, returns single item.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad item(s) data',
                examples=[
                    OpenApiExample(
                        'Success response (single item)',
                        value={
                            'data': {
                                'id': 1,
                                'adsZoneId': 1,
                                'filePath': 'string',
                                'fileType': 0,
                                'fromTime': '2025-11-09T06:54:24.692',
                                'toTime': '2025-11-09T06:54:24.692',
                                'locale': 'fa'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def dapper(self, request):
        """Get ads items in dapper context matching old Swagger format."""
        item_id = request.query_params.get('id')
        
        if item_id:
            # Return single item by ID
            try:
                ads_item = AdsItem.objects.get(id=int(item_id), is_active=True)
                serializer = AdsItemCompatibilitySerializer(ads_item)
                return create_success_response(data=serializer.data)
            except (AdsItem.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Ad item with ID "{item_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all items
            ads_items = AdsItem.objects.filter(is_active=True).order_by('-created_at')
            serializer = AdsItemCompatibilitySerializer(ads_items, many=True)
            return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_search',
        summary='Search ads items',
        description='Search AdsItems using available Filters matching old Swagger format.',
        request=AdsItemSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search ad items',
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
                            'messages': [],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 0,
                                    'adsZone': {
                                        'id': 0,
                                        'name': 'string',
                                        'width': 0,
                                        'height': 0
                                    },
                                    'fromTime': '2025-11-09T07:30:16.660Z',
                                    'toTime': '2025-11-09T07:30:16.660Z',
                                    'locale': 'string'
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
            ),
            400: {'description': 'Validation error'}
        }
    )
    def search(self, request):
        """Search ads items using filters matching old Swagger format."""
        # Validate input
        serializer = AdsItemSearchRequestSerializer(data=request.data)
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
        
        # Get pagination parameters
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        # Get keyword from request or advancedSearch
        keyword = validated_data.get('keyword') or ''
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and advanced_search.get('keyword'):
            keyword = advanced_search.get('keyword') or keyword
        
        # Build query
        qs = AdsItem.objects.filter(is_active=True)
        
        # Apply keyword search on file_path field
        if keyword and keyword.strip():
            qs = qs.filter(file_path__icontains=keyword.strip())
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Parse orderBy fields (e.g., "id", "-id" for descending)
            order_fields = []
            for field in order_by:
                if field and field.strip():
                    order_fields.append(field.strip())
            if order_fields:
                qs = qs.order_by(*order_fields)
        else:
            # Default ordering
            qs = qs.order_by('-created_at')
        
        # Get total count
        total_count = qs.count()
        
        # Calculate pagination
        if page_size > 0:
            total_pages = (total_count + page_size - 1) // page_size
            start = (page_number - 1) * page_size
            end = start + page_size
            has_previous = page_number > 1
            has_next = page_number < total_pages
        else:
            # If pageSize is 0, return all results
            total_pages = 0
            start = 0
            end = None
            has_previous = False
            has_next = False
        
        # Get paginated results
        if end is not None:
            ads_items = qs[start:end]
        else:
            ads_items = qs[start:]
        
        # Serialize results using search response serializer (with nested adsZone)
        item_serializer = AdsItemSearchResponseSerializer(ads_items, many=True)
        
        # Build response matching old Swagger format
        response_data = {
            'messages': [],  # Empty array on success
            'succeeded': True,
            'data': item_serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous,
            'hasNextPage': has_next
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['AdsItems'],
        operation_id='adsitems_client_by_zoneid',
        summary='Get ads items by zone ID',
        description='Get ads items by zone ID for client matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ads zone ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of ads items for the zone',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': ['string'],
                            'succeeded': True,
                            'data': [
                                {
                                    'id': 0,
                                    'adsZone': {
                                        'id': 0,
                                        'name': 'string',
                                        'width': 0,
                                        'height': 0
                                    },
                                    'fromTime': '2025-11-12T05:44:51.097Z',
                                    'toTime': '2025-11-12T05:44:51.097Z',
                                    'locale': 'string'
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    def client_by_zoneid(self, request, id=None):
        """Get ads items by zone ID for client matching old Swagger format."""
        # Get ads items for the specified zone
        ads_items = AdsItem.objects.filter(ads_zone_id=id, is_active=True).order_by('-created_at')
        # Use AdsItemSearchResponseSerializer which includes nested adsZone object
        serializer = AdsItemSearchResponseSerializer(ads_items, many=True)
        
        # Return response matching old Swagger format
        return Response({
            'messages': ['string'],  # Old Swagger shows array with string
            'succeeded': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

