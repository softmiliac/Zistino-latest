"""
Views for Trip compatibility layer.
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
from zistino_apps.deliveries.models import Delivery
from .models import Trip
from .serializers import (
    TripCreateUpdateRequestSerializer,
    TripSearchRequestSerializer,
)

User = get_user_model()


def trip_to_old_swagger_format(trip):
    """Convert Trip model instance to old Swagger response format."""
    return {
        'id': trip.id,
        'userId': str(trip.user.id) if trip.user else None,
        'startLocationId': trip.start_location_id or 0,
        'endLocationId': trip.end_location_id or 0,
        'distance': trip.distance or 0,
        'duration': trip.duration or 0,
        'maxSpeed': trip.max_speed or 0,
        'averageSpeed': trip.average_speed or 0,
        'averageAltitude': trip.average_altitude or 0,
        'createdOn': trip.created_at.isoformat() if trip.created_at else None
    }


@extend_schema(tags=['Trip'])
class TripViewSet(viewsets.ViewSet):
    """
    ViewSet for Trip endpoints.
    All endpoints will appear under "Trip" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Trip'],
        operation_id='trip_create',
        summary='Create a trip',
        description='Create a new trip matching old Swagger format.',
        request=TripCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create trip',
                value={
                    'userId': 'string',
                    'startLocationId': 0,
                    'endLocationId': 0,
                    'distance': 0,
                    'duration': 0,
                    'maxSpeed': 0,
                    'averageSpeed': 0,
                    'averageAltitude': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Trip created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 10004,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request):
        """Create a new trip matching old Swagger format."""
        try:
            serializer = TripCreateUpdateRequestSerializer(data=request.data)
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
            
            # Create trip
            trip = Trip.objects.create(
                user=user,
                start_location_id=validated_data.get('startLocationId', 0),
                end_location_id=validated_data.get('endLocationId', 0),
                distance=validated_data.get('distance', 0),
                duration=validated_data.get('duration', 0),
                max_speed=validated_data.get('maxSpeed', 0),
                average_speed=validated_data.get('averageSpeed', 0),
                average_altitude=validated_data.get('averageAltitude', 0)
            )
            
            return create_success_response(data=trip.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating trip: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Trip'],
        operation_id='trip_retrieve',
        summary='Retrieve a trip by ID',
        description='Get a trip by its ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Trip details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "userId": "85edc2ba-81db-4648-b008-816aa2ad1dd2",
                                "startLocationId": 0,
                                "endLocationId": 0,
                                "distance": 0,
                                "duration": 0,
                                "maxSpeed": 0,
                                "averageSpeed": 0,
                                "averageAltitude": 0,
                                "createdOn": "2024-03-13T07:17:14.2860233"
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
        """Retrieve a trip by ID matching old Swagger format."""
        try:
            try:
                trip = Trip.objects.get(id=pk)
            except (ValueError, Trip.DoesNotExist):
                return create_error_response(
                    error_message=f'Trip with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Trip with ID "{pk}" not found.']}
                )
            
            trip_data = trip_to_old_swagger_format(trip)
            return create_success_response(data=trip_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving trip: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Trip'],
        operation_id='trip_update',
        summary='Update a trip',
        description='Update an existing trip matching old Swagger format.',
        request=TripCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update trip',
                value={
                    'userId': 'string',
                    'startLocationId': 0,
                    'endLocationId': 0,
                    'distance': 0,
                    'duration': 0,
                    'maxSpeed': 0,
                    'averageSpeed': 0,
                    'averageAltitude': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Trip updated successfully',
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
        """Update a trip matching old Swagger format."""
        try:
            serializer = TripCreateUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # Get trip
            try:
                trip = Trip.objects.get(id=pk)
            except (ValueError, Trip.DoesNotExist):
                return create_error_response(
                    error_message=f'Trip with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Trip with ID "{pk}" not found.']}
                )
            
            validated_data = serializer.validated_data
            
            # Update user if provided
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    trip.user = user
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data["userId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{validated_data["userId"]}" not found.']}
                    )
            
            # Update fields
            if 'startLocationId' in validated_data:
                trip.start_location_id = validated_data['startLocationId']
            if 'endLocationId' in validated_data:
                trip.end_location_id = validated_data['endLocationId']
            if 'distance' in validated_data:
                trip.distance = validated_data['distance']
            if 'duration' in validated_data:
                trip.duration = validated_data['duration']
            if 'maxSpeed' in validated_data:
                trip.max_speed = validated_data['maxSpeed']
            if 'averageSpeed' in validated_data:
                trip.average_speed = validated_data['averageSpeed']
            if 'averageAltitude' in validated_data:
                trip.average_altitude = validated_data['averageAltitude']
            
            trip.save()
            
            return create_success_response(data=trip.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating trip: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Trip'],
        operation_id='trip_destroy',
        summary='Delete a trip',
        description='Delete a trip by ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Trip deleted successfully',
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
        """Delete a trip matching old Swagger format."""
        try:
            try:
                trip = Trip.objects.get(id=pk)
            except (ValueError, Trip.DoesNotExist):
                return create_error_response(
                    error_message=f'Trip with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Trip with ID "{pk}" not found.']}
                )
            
            trip_id = trip.id
            trip.delete()
            
            return create_success_response(data=trip_id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting trip: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Trip'],
        operation_id='trip_search',
        summary='Search trip using available filters',
        description='Search trips with filters matching old Swagger format.',
        request=TripSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search trips',
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
                    'userId': 'string'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Paginated list of trips',
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
        """Search trips matching old Swagger format."""
        try:
            serializer = TripSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Start with all trips
            qs = Trip.objects.all().select_related('user')
            
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
            
            # Apply keyword search (not much to search on trips, but we can search by ID)
            keyword = validated_data.get('keyword', '')
            if keyword:
                try:
                    keyword_int = int(keyword)
                    qs = qs.filter(id=keyword_int)
                except ValueError:
                    # If keyword is not a number, skip search
                    pass
            
            # Apply advanced search if provided
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                adv_keyword = advanced_search['keyword']
                try:
                    adv_keyword_int = int(adv_keyword)
                    qs = qs.filter(id=adv_keyword_int)
                except ValueError:
                    pass
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                order_fields = []
                for field in order_by:
                    if field:
                        # Map camelCase to snake_case
                        field_mapping = {
                            'userId': 'user_id',
                            'startLocationId': 'start_location_id',
                            'endLocationId': 'end_location_id',
                            'maxSpeed': 'max_speed',
                            'averageSpeed': 'average_speed',
                            'averageAltitude': 'average_altitude',
                            'createdOn': 'created_at',
                        }
                        db_field = field_mapping.get(field, field)
                        if hasattr(Trip, db_field):
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
            trips = qs[start:end]
            
            # Convert to old Swagger format
            trips_data = [trip_to_old_swagger_format(t) for t in trips]
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            has_previous_page = page_number > 1
            has_next_page = page_number < total_pages if total_pages > 0 else False
            
            # Build response matching old Swagger format
            response_data = {
                'data': trips_data,
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
                error_message=f'An error occurred while searching trips: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Trip'],
    operation_id='trip_get_by_job_id',
    summary='Get trip by job ID',
    description='Get a trip associated with a specific job ID (delivery ID) matching old Swagger format. '
                'To get delivery IDs, use GET /api/v1/driverdelivery/ or POST /api/v1/driverdelivery/search. '
                'The delivery "id" field is what you use as the "jobid" parameter here.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Trip details for the job',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": {},
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class TripGetByJobIdView(APIView):
    """GET /api/v1/trip/job-id/{jobid}
    
    Note: jobid is a delivery ID. Get delivery IDs from:
    - GET /api/v1/driverdelivery/ (list all deliveries)
    - POST /api/v1/driverdelivery/search (search deliveries)
    - GET /api/v1/driverdelivery/{id} (get specific delivery)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, jobid):
        """Get trip by job ID (delivery ID) matching old Swagger format.
        
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
            
            # Get trips for the delivery's driver (most recent trip)
            driver = delivery.driver
            trip = Trip.objects.filter(user=driver).order_by('-created_at').first()
            
            if not trip:
                return create_error_response(
                    error_message=f'No trip found for delivery (job) ID "{jobid}".',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'jobid': [f'No trip found for delivery (job) ID "{jobid}".']}
                )
            
            trip_data = trip_to_old_swagger_format(trip)
            return create_success_response(data=trip_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting trip by job ID: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Trip'],
    operation_id='trip_all',
    summary='Get all trips',
    description='Get all trips matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='List of all trips',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "id": 1,
                                "userId": "85edc2ba-81db-4648-b008-816aa2ad1dd2",
                                "startLocationId": 0,
                                "endLocationId": 0,
                                "distance": 0,
                                "duration": 0,
                                "maxSpeed": 0,
                                "averageSpeed": 0,
                                "averageAltitude": 0,
                                "createdOn": "2024-03-13T07:17:14.2860233"
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
class TripAllView(APIView):
    """GET /api/v1/trip/all"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all trips matching old Swagger format."""
        try:
            trips = Trip.objects.all().select_related('user').order_by('-created_at')
            
            # Convert to old Swagger format
            trips_data = [trip_to_old_swagger_format(t) for t in trips]
            
            return create_success_response(data=trips_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting all trips: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

