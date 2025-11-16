"""
Views for Locations compatibility layer.
Provides all endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
import uuid

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.deliveries.models import Delivery, Trip
from .models import LocationUpdate
from .serializers import (
    LocationCreateUpdateRequestSerializer,
    LocationSearchRequestSerializer,
)

User = get_user_model()


def location_to_old_swagger_format(location):
    """Convert LocationUpdate model instance to old Swagger response format."""
    return {
        'id': location.id,
        'userId': str(location.user.id) if location.user else None,
        'tripId': location.trip.id if location.trip else 0,
        'latitude': float(location.latitude) if location.latitude else 0,
        'longitude': float(location.longitude) if location.longitude else 0,
        'speed': location.speed or 0,
        'heading': location.heading or None,
        'altitude': float(location.altitude) if location.altitude else 0,
        'satellites': location.satellites or 0,
        'hdop': location.hdop or 0,
        'gsmSignal': location.gsm_signal or 0,
        'odometer': location.odometer or 0,
        'createdOn': location.created_at.isoformat() if location.created_at else None
    }


@extend_schema(tags=['Locations'])
class LocationsViewSet(viewsets.ViewSet):
    """
    ViewSet for Locations endpoints.
    All endpoints will appear under "Locations" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Locations'],
        operation_id='locations_create',
        summary='Create a location',
        description='Create a new location matching old Swagger format.',
        request=LocationCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create location',
                value={
                    'userId': 'string',
                    'tripId': 0,
                    'latitude': 0,
                    'longitude': 0,
                    'speed': 0,
                    'heading': 'string',
                    'altitude': 0,
                    'satellites': 0,
                    'hdop': 0,
                    'gsmSignal': 0,
                    'odometer': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Location created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 10101,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request):
        """Create a new location matching old Swagger format."""
        try:
            serializer = LocationCreateUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get user
            user_id = validated_data.get('userId')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{user_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'userId': [f'User with ID "{user_id}" not found.']}
                )
            
            # Get trip
            trip_id = validated_data.get('tripId')
            try:
                trip = Trip.objects.get(id=trip_id)
            except Trip.DoesNotExist:
                return create_error_response(
                    error_message=f'Trip with ID "{trip_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'tripId': [f'Trip with ID "{trip_id}" not found.']}
                )
            
            # Create location
            location = LocationUpdate.objects.create(
                user=user,
                trip=trip,
                latitude=validated_data.get('latitude'),
                longitude=validated_data.get('longitude'),
                speed=validated_data.get('speed', 0),
                heading=validated_data.get('heading', ''),
                altitude=validated_data.get('altitude', 0),
                satellites=validated_data.get('satellites', 0),
                hdop=validated_data.get('hdop', 0),
                gsm_signal=validated_data.get('gsmSignal', 0),
                odometer=validated_data.get('odometer', 0)
            )
            
            return create_success_response(data=location.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating location: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Locations'],
        operation_id='locations_retrieve',
        summary='Retrieve a location by ID',
        description='Get a location by its ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Location details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "userId": "85edc2ba-81db-4648-b008-816aa2ad1dd2",
                                "tripId": 2,
                                "latitude": 36.312794,
                                "longitude": 59.590782,
                                "speed": 0,
                                "heading": "110.00298309326172",
                                "altitude": 995.7,
                                "satellites": 0,
                                "hdop": 0,
                                "gsmSignal": 0,
                                "odometer": 0,
                                "createdOn": "2024-03-13T07:23:45.2071278"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, pk=None):
        """Retrieve a location by ID matching old Swagger format."""
        try:
            try:
                location = LocationUpdate.objects.get(id=pk)
            except (ValueError, LocationUpdate.DoesNotExist):
                return create_error_response(
                    error_message=f'Location with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Location with ID "{pk}" not found.']}
                )
            
            location_data = location_to_old_swagger_format(location)
            return create_success_response(data=location_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving location: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Locations'],
        operation_id='locations_update',
        summary='Update a location',
        description='Update an existing location matching old Swagger format.',
        request=LocationCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update location',
                value={
                    'userId': 'string',
                    'tripId': 0,
                    'latitude': 0,
                    'longitude': 0,
                    'speed': 0,
                    'heading': 'string',
                    'altitude': 0,
                    'satellites': 0,
                    'hdop': 0,
                    'gsmSignal': 0,
                    'odometer': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Location updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """Update a location matching old Swagger format."""
        try:
            serializer = LocationCreateUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # Get location
            try:
                location = LocationUpdate.objects.get(id=pk)
            except (ValueError, LocationUpdate.DoesNotExist):
                return create_error_response(
                    error_message=f'Location with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Location with ID "{pk}" not found.']}
                )
            
            validated_data = serializer.validated_data
            
            # Update user if provided
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    location.user = user
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data["userId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{validated_data["userId"]}" not found.']}
                    )
            
            # Update trip if provided
            if validated_data.get('tripId'):
                try:
                    trip = Trip.objects.get(id=validated_data['tripId'])
                    location.trip = trip
                except Trip.DoesNotExist:
                    return create_error_response(
                        error_message=f'Trip with ID "{validated_data["tripId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'tripId': [f'Trip with ID "{validated_data["tripId"]}" not found.']}
                    )
            
            # Update fields
            if 'latitude' in validated_data:
                location.latitude = validated_data['latitude']
            if 'longitude' in validated_data:
                location.longitude = validated_data['longitude']
            if 'speed' in validated_data:
                location.speed = validated_data['speed']
            if 'heading' in validated_data:
                location.heading = validated_data['heading']
            if 'altitude' in validated_data:
                location.altitude = validated_data['altitude']
            if 'satellites' in validated_data:
                location.satellites = validated_data['satellites']
            if 'hdop' in validated_data:
                location.hdop = validated_data['hdop']
            if 'gsmSignal' in validated_data:
                location.gsm_signal = validated_data['gsmSignal']
            if 'odometer' in validated_data:
                location.odometer = validated_data['odometer']
            
            location.save()
            
            return create_success_response(data=location.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating location: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Locations'],
        operation_id='locations_destroy',
        summary='Delete a location',
        description='Delete a location by ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Location deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, pk=None):
        """Delete a location matching old Swagger format."""
        try:
            try:
                location = LocationUpdate.objects.get(id=pk)
            except (ValueError, LocationUpdate.DoesNotExist):
                return create_error_response(
                    error_message=f'Location with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Location with ID "{pk}" not found.']}
                )
            
            location_id = location.id
            location.delete()
            
            return create_success_response(data=location_id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting location: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Locations'],
        operation_id='locations_search',
        summary='Search locations using available filters',
        description='Search locations with filters matching old Swagger format.',
        request=LocationSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search locations',
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
                    'tripId': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Paginated list of locations',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 1,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search locations matching old Swagger format."""
        try:
            serializer = LocationSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Start with all locations
            qs = LocationUpdate.objects.all().select_related('user', 'trip')
            
            # Filter by userId if provided
            user_id = validated_data.get('userId')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    qs = qs.filter(user=user)
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{user_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{user_id}" not found.']}
                    )
            
            # Filter by tripId if provided
            trip_id = validated_data.get('tripId')
            if trip_id is not None:
                qs = qs.filter(trip_id=trip_id)
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '')
            if keyword:
                qs = qs.filter(
                    Q(heading__icontains=keyword)
                )
            
            # Apply advanced search if provided
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                adv_keyword = advanced_search['keyword']
                qs = qs.filter(
                    Q(heading__icontains=adv_keyword)
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                order_fields = []
                for field in order_by:
                    if field:
                        # Map camelCase to snake_case
                        field_mapping = {
                            'userId': 'user_id',
                            'tripId': 'trip_id',
                            'gsmSignal': 'gsm_signal',
                            'createdOn': 'created_at',
                        }
                        db_field = field_mapping.get(field, field)
                        if hasattr(LocationUpdate, db_field):
                            order_fields.append(db_field)
                if order_fields:
                    qs = qs.order_by(*order_fields)
            else:
                qs = qs.order_by('-created_at')
            
            # Get total count
            total_count = qs.count()
            
            # Handle pagination (pageNumber: 0 defaults to 1, pageSize: 0 defaults to 1)
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            if page_number == 0:
                page_number = 1
            if page_size == 0:
                page_size = 1
            
            # Apply pagination
            start = (page_number - 1) * page_size
            end = start + page_size
            locations = qs[start:end]
            
            # Convert to old Swagger format
            locations_data = [location_to_old_swagger_format(loc) for loc in locations]
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            has_previous_page = page_number > 1
            has_next_page = page_number < total_pages if total_pages > 0 else False
            
            # Build response matching old Swagger format
            response_data = {
                'data': locations_data,
                'currentPage': page_number,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
                'hasPreviousPage': has_previous_page,
                'hasNextPage': has_next_page,
                'messages': None,  # Old Swagger shows null
                'succeeded': True
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching locations: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Locations'],
    operation_id='locations_get_by_job_id',
    summary='Get locations by job ID',
    description='Get all locations associated with a specific job ID (delivery ID) matching old Swagger format. '
                'To get delivery IDs, use GET /api/v1/driverdelivery/ or POST /api/v1/driverdelivery/search. '
                'The delivery "id" field is what you use as the "jobid" parameter here.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='List of locations for the job',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class LocationsGetByJobIdView(APIView):
    """GET /api/v1/locations/job-id/{jobid}
    
    Note: jobid is a delivery ID. Get delivery IDs from:
    - GET /api/v1/driverdelivery/ (list all deliveries)
    - POST /api/v1/driverdelivery/search (search deliveries)
    - GET /api/v1/driverdelivery/{id} (get specific delivery)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, jobid):
        """Get locations by job ID (delivery ID) matching old Swagger format.
        
        Args:
            jobid: Delivery ID (UUID string or integer hash). 
                   Get delivery IDs from /api/v1/driverdelivery/ endpoints.
        """
        try:
            # Try to get delivery by UUID first, then by integer
            try:
                delivery = Delivery.objects.get(id=jobid)
            except (ValueError, Delivery.DoesNotExist):
                # Try to find by integer hash
                import hashlib
                deliveries = Delivery.objects.all()
                delivery = None
                for d in deliveries:
                    delivery_id_str = str(d.id).replace('-', '')
                    delivery_id_int = int(hashlib.md5(delivery_id_str.encode()).hexdigest()[:8], 16) % 100000000
                    if str(delivery_id_int) == str(jobid):
                        delivery = d
                        break
                
                if not delivery:
                    return create_error_response(
                        error_message=f'Delivery (job) with ID "{jobid}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'jobid': [f'Delivery (job) with ID "{jobid}" not found.']}
                    )
            
            # Get locations for trips associated with the delivery's driver
            driver = delivery.driver
            # Get all trips for this driver, then get locations for those trips
            trips = Trip.objects.filter(user=driver)
            locations = LocationUpdate.objects.filter(trip__in=trips).select_related('user', 'trip').order_by('-created_at')
            
            # Convert to old Swagger format
            locations_data = [location_to_old_swagger_format(loc) for loc in locations]
            
            return create_success_response(data=locations_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting locations by job ID: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Locations'],
    operation_id='locations_all',
    summary='Get all locations',
    description='Get all locations matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='List of all locations',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "id": 1,
                                "userId": "85edc2ba-81db-4648-b008-816aa2ad1dd2",
                                "tripId": 2,
                                "latitude": 36.312794,
                                "longitude": 59.590782,
                                "speed": 0,
                                "heading": "110.00298309326172",
                                "altitude": 995.7,
                                "satellites": 0,
                                "hdop": 0,
                                "gsmSignal": 0,
                                "odometer": 0,
                                "createdOn": "2024-03-13T07:23:45.2071278"
                            }
                        ],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class LocationsAllView(APIView):
    """GET /api/v1/locations/all"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all locations matching old Swagger format."""
        try:
            locations = LocationUpdate.objects.all().select_related('user', 'trip').order_by('-created_at')
            
            # Convert to old Swagger format
            locations_data = [location_to_old_swagger_format(loc) for loc in locations]
            
            return create_success_response(data=locations_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting all locations: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

