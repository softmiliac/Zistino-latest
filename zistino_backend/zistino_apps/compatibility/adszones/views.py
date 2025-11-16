"""
Compatibility views for AdsZones endpoints.
All endpoints will appear under "AdsZones" folder in Swagger UI.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from django.db.models import Q
from .models import AdsZone
from .serializers import (
    AdsZoneCreateRequestSerializer,
    AdsZoneCompatibilitySerializer,
    AdsZoneSearchRequestSerializer
)


@extend_schema(tags=['AdsZones'])
class AdsZonesViewSet(viewsets.ViewSet):
    """
    Compatibility viewset for ads zones endpoints.
    All endpoints will appear under "AdsZones" folder in Swagger UI.
    """
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated if needed

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_list',
        summary='List all ads zones',
        description='Get list of all ads zones matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of ads zones',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'name': 'west',
                                    'width': 0,
                                    'height': 0
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
        """Get list of ads zones matching old Swagger format."""
        ads_zones = AdsZone.objects.filter(is_active=True).order_by('-created_at')
        serializer = AdsZoneCompatibilitySerializer(ads_zones, many=True)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_create',
        summary='Create new ad zone',
        description='Create a new advertisement zone matching old Swagger format.',
        request=AdsZoneCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create ad zone',
                value={
                    'name': 'west',
                    'width': 0,
                    'height': 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad zone created successfully',
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
    def create(self, request):
        """Create new ad zone matching old Swagger format. Returns zone ID."""
        # Validate input using old Swagger format serializer
        input_serializer = AdsZoneCreateRequestSerializer(data=request.data)
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
        
        # Create ad zone
        ads_zone = AdsZone.objects.create(
            name=validated_data.get('name'),
            width=validated_data.get('width', 0),
            height=validated_data.get('height', 0)
        )
        
        # Return just the zone ID wrapped in standard response
        return create_success_response(data=ads_zone.id)  # 200 OK to match old Swagger

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_retrieve',
        summary='Get ad zone by ID',
        description='Retrieve an ad zone by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ad zone ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad zone details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'west',
                                'width': 0,
                                'height': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Ad zone not found'}
        }
    )
    def retrieve(self, request, id=None):
        """Get ad zone by ID matching old Swagger format."""
        try:
            ads_zone = AdsZone.objects.get(id=id, is_active=True)
            serializer = AdsZoneCompatibilitySerializer(ads_zone)
            return create_success_response(data=serializer.data)
        except AdsZone.DoesNotExist:
            return create_error_response(
                error_message=f'Ad zone with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_update',
        summary='Update ad zone',
        description='Update an existing ad zone matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ad zone ID'
            )
        ],
        request=AdsZoneCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update ad zone',
                value={
                    'name': 'west-updated',
                    'width': 100,
                    'height': 200
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad zone updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'west-updated',
                                'width': 100,
                                'height': 200
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Ad zone not found'}
        }
    )
    def update(self, request, id=None):
        """Update ad zone matching old Swagger format."""
        try:
            ads_zone = AdsZone.objects.get(id=id, is_active=True)
        except AdsZone.DoesNotExist:
            return create_error_response(
                error_message=f'Ad zone with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = AdsZoneCreateRequestSerializer(data=request.data)
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
        
        # Update ad zone
        ads_zone.name = validated_data.get('name', ads_zone.name)
        ads_zone.width = validated_data.get('width', ads_zone.width)
        ads_zone.height = validated_data.get('height', ads_zone.height)
        ads_zone.save()
        
        # Return updated zone
        serializer = AdsZoneCompatibilitySerializer(ads_zone)
        return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_destroy',
        summary='Delete ad zone',
        description='Delete an ad zone by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ad zone ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad zone deleted successfully',
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
            404: {'description': 'Ad zone not found'}
        }
    )
    def destroy(self, request, id=None):
        """Delete ad zone matching old Swagger format."""
        try:
            ads_zone = AdsZone.objects.get(id=id, is_active=True)
            # Soft delete by setting is_active to False
            ads_zone.is_active = False
            ads_zone.save()
            return create_success_response(data=None)
        except AdsZone.DoesNotExist:
            return create_error_response(
                error_message=f'Ad zone with ID "{id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_dapper',
        summary='Get ads zones (dapper context)',
        description='Get ads zones in dapper context. If id query parameter is provided, returns single zone.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Ad zone ID. If provided, returns single zone.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Ad zone(s) data',
                examples=[
                    OpenApiExample(
                        'Success response (single zone)',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'west',
                                'width': 0,
                                'height': 0
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    ),
                    OpenApiExample(
                        'Success response (all zones)',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'name': 'west',
                                    'width': 0,
                                    'height': 0
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
    def dapper(self, request):
        """Get ads zones in dapper context matching old Swagger format."""
        zone_id = request.query_params.get('id')
        
        if zone_id:
            # Return single zone by ID
            try:
                ads_zone = AdsZone.objects.get(id=int(zone_id), is_active=True)
                serializer = AdsZoneCompatibilitySerializer(ads_zone)
                return create_success_response(data=serializer.data)
            except (AdsZone.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Ad zone with ID "{zone_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all zones
            ads_zones = AdsZone.objects.filter(is_active=True).order_by('-created_at')
            serializer = AdsZoneCompatibilitySerializer(ads_zones, many=True)
            return create_success_response(data=serializer.data)

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_search',
        summary='Search ads zones',
        description='Search AdsZones using available Filters matching old Swagger format.',
        request=AdsZoneSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search ad zones',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'new',
                        'groupBy': ['']
                    },
                    'keyword': 'new',
                    'pageNumber': 1,
                    'pageSize': 1,
                    'orderBy': ['']
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
            ),
            400: {'description': 'Validation error'}
        }
    )
    def search(self, request):
        """Search ads zones using filters matching old Swagger format."""
        # Validate input
        serializer = AdsZoneSearchRequestSerializer(data=request.data)
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
        page_number = validated_data.get('pageNumber', 1)
        page_size = validated_data.get('pageSize', 20)
        
        # Get keyword from request or advancedSearch
        keyword = validated_data.get('keyword') or ''
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and advanced_search.get('keyword'):
            keyword = advanced_search.get('keyword') or keyword
        
        # Build query
        qs = AdsZone.objects.filter(is_active=True)
        
        # Apply keyword search on name field
        if keyword and keyword.strip():
            qs = qs.filter(name__icontains=keyword.strip())
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Parse orderBy fields (e.g., "name", "-name" for descending)
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
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        start = (page_number - 1) * page_size
        end = start + page_size
        
        # Get paginated results
        ads_zones = qs[start:end]
        
        # Serialize results
        zone_serializer = AdsZoneCompatibilitySerializer(ads_zones, many=True)
        
        # Build response matching old Swagger format
        response_data = {
            'data': zone_serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': page_number > 1,
            'hasNextPage': page_number < total_pages,
            'messages': None,  # Old Swagger shows null, not empty array
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['AdsZones'],
        operation_id='adszones_all',
        summary='Get all ads zones',
        description='Get all ads zones matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of all ads zones',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [
                                {
                                    'id': 1,
                                    'name': 'west',
                                    'width': 0,
                                    'height': 0
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
    def all(self, request):
        """Get all ads zones matching old Swagger format."""
        ads_zones = AdsZone.objects.filter(is_active=True).order_by('-created_at')
        serializer = AdsZoneCompatibilitySerializer(ads_zones, many=True)
        return create_success_response(data=serializer.data)

