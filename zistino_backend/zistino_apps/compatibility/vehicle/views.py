"""
Views for Vehicle compatibility layer.
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
from .models import Vehicle
from .serializers import (
    VehicleCreateUpdateRequestSerializer,
    VehicleSearchRequestSerializer,
    VehicleResponseSerializer,
)

User = get_user_model()


def vehicle_to_old_swagger_format(vehicle):
    """Convert Vehicle model instance to old Swagger response format."""
    return {
        'id': str(vehicle.id) if vehicle.id else None,
        'userId': str(vehicle.user.id) if vehicle.user else None,
        'modelMake': vehicle.model_make or None,
        'plateNum': vehicle.plate_num or None,
        'licence': vehicle.licence or None,
        'bodytype': vehicle.bodytype or None,
        'color': vehicle.color or None,
        'manufacturer': vehicle.manufacturer or None,
        'registrationNum': vehicle.registration_num or None,
        'engineSize': vehicle.engine_size or None,
        'tank': vehicle.tank or None,
        'numoftyres': vehicle.numoftyres or None,
        'gpsDeviceId': vehicle.gps_device_id or None,
        'active': vehicle.active,
        'latitude': float(vehicle.latitude) if vehicle.latitude else 0,
        'longitude': float(vehicle.longitude) if vehicle.longitude else 0,
        'protocol': vehicle.protocol or None,
        'port': vehicle.port or 0
    }


@extend_schema(tags=['Vehicle'])
class VehicleViewSet(viewsets.ViewSet):
    """
    ViewSet for Vehicle endpoints.
    All endpoints will appear under "Vehicle" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Vehicle'],
        operation_id='vehicle_create',
        summary='Create a vehicle',
        description='Create a new vehicle matching old Swagger format.',
        request=VehicleCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create vehicle',
                value={
                    'userId': 'string',
                    'modelMake': 'string',
                    'plateNum': 'string',
                    'licence': 'string',
                    'bodytype': 'string',
                    'color': 'string',
                    'manufacturer': 'string',
                    'registrationNum': 'string',
                    'engineSize': 'string',
                    'tank': 'string',
                    'numoftyres': 'string',
                    'gpsDeviceId': 'string',
                    'active': True,
                    'latitude': 0,
                    'longitude': 0,
                    'protocol': 'string',
                    'port': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Vehicle created successfully',
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
    def create(self, request):
        """Create a new vehicle matching old Swagger format."""
        try:
            serializer = VehicleCreateUpdateRequestSerializer(data=request.data)
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
            
            # Create vehicle
            vehicle = Vehicle.objects.create(
                user=user,
                model_make=validated_data.get('modelMake', ''),
                plate_num=validated_data.get('plateNum', ''),
                licence=validated_data.get('licence', ''),
                bodytype=validated_data.get('bodytype', ''),
                color=validated_data.get('color', ''),
                manufacturer=validated_data.get('manufacturer', ''),
                registration_num=validated_data.get('registrationNum', ''),
                engine_size=validated_data.get('engineSize', ''),
                tank=validated_data.get('tank', ''),
                numoftyres=validated_data.get('numoftyres', ''),
                gps_device_id=validated_data.get('gpsDeviceId', ''),
                active=validated_data.get('active', True),
                latitude=validated_data.get('latitude'),
                longitude=validated_data.get('longitude'),
                protocol=validated_data.get('protocol', ''),
                port=validated_data.get('port', 0)
            )
            
            # Return vehicle ID (using integer hash for compatibility with old Swagger)
            import hashlib
            vehicle_id_str = str(vehicle.id).replace('-', '')
            vehicle_id_int = int(hashlib.md5(vehicle_id_str.encode()).hexdigest()[:8], 16) % 100000000
            
            return create_success_response(data=vehicle_id_int, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating vehicle: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Vehicle'],
        operation_id='vehicle_retrieve',
        summary='Retrieve a vehicle by ID',
        description='Get a vehicle by its ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Vehicle details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "userId": "string",
                                "modelMake": "string",
                                "plateNum": "string",
                                "licence": "string",
                                "bodytype": "string",
                                "color": "string",
                                "manufacturer": "string",
                                "registrationNum": "string",
                                "engineSize": "string",
                                "tank": "string",
                                "numoftyres": "string",
                                "gpsDeviceId": "string",
                                "active": True,
                                "latitude": 0,
                                "longitude": 0,
                                "protocol": "string",
                                "port": 0
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
        """Retrieve a vehicle by ID matching old Swagger format."""
        try:
            vehicle = None
            
            # Try to parse as UUID first
            try:
                uuid_obj = uuid.UUID(str(pk))
                vehicle = Vehicle.objects.get(id=uuid_obj)
            except (ValueError, Vehicle.DoesNotExist):
                # If UUID parsing fails or not found, try integer hash lookup
                import hashlib
                vehicles = Vehicle.objects.all()
                for v in vehicles:
                    vehicle_id_str = str(v.id).replace('-', '')
                    vehicle_id_int = int(hashlib.md5(vehicle_id_str.encode()).hexdigest()[:8], 16) % 100000000
                    if str(vehicle_id_int) == str(pk):
                        vehicle = v
                        break
            
            if not vehicle:
                return create_error_response(
                    error_message=f'Vehicle with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Vehicle with ID "{pk}" not found.']}
                )
            
            vehicle_data = vehicle_to_old_swagger_format(vehicle)
            return create_success_response(data=vehicle_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving vehicle: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Vehicle'],
        operation_id='vehicle_update',
        summary='Update a vehicle',
        description='Update an existing vehicle matching old Swagger format.',
        request=VehicleCreateUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update vehicle',
                value={
                    'userId': 'string',
                    'modelMake': 'string',
                    'plateNum': 'string',
                    'licence': 'string',
                    'bodytype': 'string',
                    'color': 'string',
                    'manufacturer': 'string',
                    'registrationNum': 'string',
                    'engineSize': 'string',
                    'tank': 'string',
                    'numoftyres': 'string',
                    'gpsDeviceId': 'string',
                    'active': True,
                    'latitude': 0,
                    'longitude': 0,
                    'protocol': 'string',
                    'port': 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Vehicle updated successfully',
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
        """Update a vehicle matching old Swagger format."""
        try:
            serializer = VehicleCreateUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # Get vehicle
            vehicle = None
            
            # Try to parse as UUID first
            try:
                uuid_obj = uuid.UUID(str(pk))
                vehicle = Vehicle.objects.get(id=uuid_obj)
            except (ValueError, Vehicle.DoesNotExist):
                # If UUID parsing fails or not found, try integer hash lookup
                import hashlib
                vehicles = Vehicle.objects.all()
                for v in vehicles:
                    vehicle_id_str = str(v.id).replace('-', '')
                    vehicle_id_int = int(hashlib.md5(vehicle_id_str.encode()).hexdigest()[:8], 16) % 100000000
                    if str(vehicle_id_int) == str(pk):
                        vehicle = v
                        break
            
            if not vehicle:
                return create_error_response(
                    error_message=f'Vehicle with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Vehicle with ID "{pk}" not found.']}
                )
            
            validated_data = serializer.validated_data
            
            # Update user if provided
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    vehicle.user = user
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data["userId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{validated_data["userId"]}" not found.']}
                    )
            
            # Update fields
            if 'modelMake' in validated_data:
                vehicle.model_make = validated_data['modelMake']
            if 'plateNum' in validated_data:
                vehicle.plate_num = validated_data['plateNum']
            if 'licence' in validated_data:
                vehicle.licence = validated_data['licence']
            if 'bodytype' in validated_data:
                vehicle.bodytype = validated_data['bodytype']
            if 'color' in validated_data:
                vehicle.color = validated_data['color']
            if 'manufacturer' in validated_data:
                vehicle.manufacturer = validated_data['manufacturer']
            if 'registrationNum' in validated_data:
                vehicle.registration_num = validated_data['registrationNum']
            if 'engineSize' in validated_data:
                vehicle.engine_size = validated_data['engineSize']
            if 'tank' in validated_data:
                vehicle.tank = validated_data['tank']
            if 'numoftyres' in validated_data:
                vehicle.numoftyres = validated_data['numoftyres']
            if 'gpsDeviceId' in validated_data:
                vehicle.gps_device_id = validated_data['gpsDeviceId']
            if 'active' in validated_data:
                vehicle.active = validated_data['active']
            if 'latitude' in validated_data:
                vehicle.latitude = validated_data['latitude']
            if 'longitude' in validated_data:
                vehicle.longitude = validated_data['longitude']
            if 'protocol' in validated_data:
                vehicle.protocol = validated_data['protocol']
            if 'port' in validated_data:
                vehicle.port = validated_data['port']
            
            vehicle.save()
            
            # Return vehicle ID (using integer hash for compatibility)
            import hashlib
            vehicle_id_str = str(vehicle.id).replace('-', '')
            vehicle_id_int = int(hashlib.md5(vehicle_id_str.encode()).hexdigest()[:8], 16) % 100000000
            
            return create_success_response(data=vehicle_id_int, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating vehicle: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Vehicle'],
        operation_id='vehicle_destroy',
        summary='Delete a vehicle',
        description='Delete a vehicle by ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Vehicle deleted successfully',
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
        """Delete a vehicle matching old Swagger format."""
        try:
            # Get vehicle
            vehicle = None
            
            # Try to parse as UUID first
            try:
                uuid_obj = uuid.UUID(str(pk))
                vehicle = Vehicle.objects.get(id=uuid_obj)
            except (ValueError, Vehicle.DoesNotExist):
                # If UUID parsing fails or not found, try integer hash lookup
                import hashlib
                vehicles = Vehicle.objects.all()
                for v in vehicles:
                    vehicle_id_str = str(v.id).replace('-', '')
                    vehicle_id_int = int(hashlib.md5(vehicle_id_str.encode()).hexdigest()[:8], 16) % 100000000
                    if str(vehicle_id_int) == str(pk):
                        vehicle = v
                        break
            
            if not vehicle:
                return create_error_response(
                    error_message=f'Vehicle with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Vehicle with ID "{pk}" not found.']}
                )
            
            # Get ID before deletion
            import hashlib
            vehicle_id_str = str(vehicle.id).replace('-', '')
            vehicle_id_int = int(hashlib.md5(vehicle_id_str.encode()).hexdigest()[:8], 16) % 100000000
            
            vehicle.delete()
            
            return create_success_response(data=vehicle_id_int, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting vehicle: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Vehicle'],
        operation_id='vehicle_search',
        summary='Search vehicles using available filters',
        description='Search vehicles with filters matching old Swagger format.',
        request=VehicleSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search vehicles',
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
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Paginated list of vehicles',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "messages": ["string"],
                            "succeeded": True,
                            "data": [
                                {
                                    "userId": "string",
                                    "modelMake": "string",
                                    "plateNum": "string",
                                    "licence": "string",
                                    "bodytype": "string",
                                    "color": "string",
                                    "manufacturer": "string",
                                    "registrationNum": "string",
                                    "engineSize": "string",
                                    "tank": "string",
                                    "numoftyres": "string",
                                    "gpsDeviceId": "string",
                                    "active": True,
                                    "latitude": 0,
                                    "longitude": 0,
                                    "protocol": "string",
                                    "port": 0
                                }
                            ],
                            "currentPage": 0,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 0,
                            "hasPreviousPage": True,
                            "hasNextPage": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search vehicles matching old Swagger format."""
        try:
            serializer = VehicleSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Start with all vehicles
            qs = Vehicle.objects.all().select_related('user')
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '')
            if keyword:
                qs = qs.filter(
                    Q(model_make__icontains=keyword) |
                    Q(plate_num__icontains=keyword) |
                    Q(licence__icontains=keyword) |
                    Q(bodytype__icontains=keyword) |
                    Q(color__icontains=keyword) |
                    Q(manufacturer__icontains=keyword) |
                    Q(registration_num__icontains=keyword) |
                    Q(gps_device_id__icontains=keyword)
                )
            
            # Apply advanced search if provided
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                adv_keyword = advanced_search['keyword']
                qs = qs.filter(
                    Q(model_make__icontains=adv_keyword) |
                    Q(plate_num__icontains=adv_keyword) |
                    Q(licence__icontains=adv_keyword) |
                    Q(bodytype__icontains=adv_keyword) |
                    Q(color__icontains=adv_keyword) |
                    Q(manufacturer__icontains=adv_keyword) |
                    Q(registration_num__icontains=adv_keyword) |
                    Q(gps_device_id__icontains=adv_keyword)
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                order_fields = []
                for field in order_by:
                    if field:
                        # Map camelCase to snake_case
                        field_mapping = {
                            'modelMake': 'model_make',
                            'plateNum': 'plate_num',
                            'registrationNum': 'registration_num',
                            'engineSize': 'engine_size',
                            'gpsDeviceId': 'gps_device_id',
                            'numoftyres': 'numoftyres',
                        }
                        db_field = field_mapping.get(field, field)
                        if hasattr(Vehicle, db_field):
                            order_fields.append(db_field)
                if order_fields:
                    qs = qs.order_by(*order_fields)
            else:
                qs = qs.order_by('-created_at')
            
            # Get total count
            total_count = qs.count()
            
            # Handle pagination
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size
                effective_page = page_number if page_number > 0 else 1
                start = (effective_page - 1) * page_size
                end = start + page_size
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
            else:
                total_pages = 0
                effective_page = 0
                start = 0
                end = None
                has_previous = True
                has_next = True
            
            # Get paginated results
            if end is not None:
                vehicles = qs[start:end]
            else:
                vehicles = qs[start:]
            
            # Convert to old Swagger format
            vehicles_data = [vehicle_to_old_swagger_format(v) for v in vehicles]
            
            # Build response matching old Swagger format
            response_data = {
                'messages': ["string"],  # Old Swagger shows ["string"]
                'succeeded': True,
                'data': vehicles_data,
                'currentPage': effective_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
                'hasPreviousPage': has_previous,
                'hasNextPage': has_next
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching vehicles: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Vehicle'],
    operation_id='vehicle_get_by_job_id',
    summary='Get vehicles by job ID',
    description='Get all vehicles associated with a specific job ID (delivery ID) matching old Swagger format. '
                'To get delivery IDs, use GET /api/v1/driverdelivery/ or POST /api/v1/driverdelivery/search. '
                'The delivery "id" field is what you use as the "jobid" parameter here.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='List of vehicles for the job',
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
class VehicleGetByJobIdView(APIView):
    """GET /api/v1/vehicle/job-id/{jobid}
    
    Note: jobid is a delivery ID. Get delivery IDs from:
    - GET /api/v1/driverdelivery/ (list all deliveries)
    - POST /api/v1/driverdelivery/search (search deliveries)
    - GET /api/v1/driverdelivery/{id} (get specific delivery)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, jobid):
        """Get vehicles by job ID (delivery ID) matching old Swagger format.
        
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
            
            # Get vehicles for the delivery's driver
            driver = delivery.driver
            vehicles = Vehicle.objects.filter(user=driver)
            
            # Convert to old Swagger format
            vehicles_data = [vehicle_to_old_swagger_format(v) for v in vehicles]
            
            return create_success_response(data=vehicles_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting vehicles by job ID: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Vehicle'],
    operation_id='vehicle_all',
    summary='Get all vehicles',
    description='Get all vehicles matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='List of all vehicles',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "id": "string",
                                "userId": "string",
                                "modelMake": "string",
                                "plateNum": "string",
                                "licence": "string",
                                "bodytype": "string",
                                "color": "string",
                                "manufacturer": "string",
                                "registrationNum": "string",
                                "engineSize": "string",
                                "tank": "string",
                                "numoftyres": "string",
                                "gpsDeviceId": "string",
                                "active": True,
                                "latitude": 0,
                                "longitude": 0,
                                "protocol": "string",
                                "port": 0
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
class VehicleAllView(APIView):
    """GET /api/v1/vehicle/all"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all vehicles matching old Swagger format."""
        try:
            vehicles = Vehicle.objects.all().select_related('user').order_by('-created_at')
            
            # Convert to old Swagger format
            vehicles_data = [vehicle_to_old_swagger_format(v) for v in vehicles]
            
            return create_success_response(data=vehicles_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while getting all vehicles: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

