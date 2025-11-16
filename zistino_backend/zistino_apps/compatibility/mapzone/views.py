"""
Compatibility views for MapZone endpoints.
All endpoints will appear under "MapZone" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/MapZone

Note: These endpoints wrap existing zone views from users app.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager
import uuid

from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.users.models import Zone, UserZone, User
from zistino_apps.users.serializers import ZoneSerializer, UserZoneSerializer
from zistino_apps.users.views import (
    ZoneViewSet as OriginalZoneViewSet,
    ZoneSearchView as OriginalZoneSearchView,
    ZoneUserSearchView as OriginalZoneUserSearchView,
    CreateUserZoneView as OriginalCreateUserZoneView,
    UserInZoneView as OriginalUserInZoneView,
    UserZoneViewSet as OriginalUserZoneViewSet,
)
from .serializers import (
    MapZoneSearchRequestSerializer,
    MapZoneSearchUserInZoneRequestSerializer,
    MapZoneUserInZoneRequestSerializer,
    MapZoneCreateUserInZoneRequestSerializer,
    MapZoneCreateSerializer,
)


@extend_schema(tags=['MapZone'])
class MapZoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing zones.
    All endpoints will appear under "MapZone" folder in Swagger UI.
    Wraps existing ZoneViewSet with MapZone tag.
    """
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        """Return all zones."""
        return Zone.objects.all().order_by('zone')
    
    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == 'create':
            return MapZoneCreateSerializer
        return ZoneSerializer
    
    @extend_schema(
        tags=['MapZone'],
        operation_id='mapzone_retrieve',
        summary='Retrieve a zone by ID',
        description='Retrieve a zone by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Zone ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Zone details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'zone': 'منطقه 3',
                                'zonepath': None,
                                'description': 'طبرسی شمالی ',
                                'address': None
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Zone not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a zone by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Zone matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Zone with ID "{self.kwargs.get("pk")}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Zone with ID "{self.kwargs.get("pk")}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['MapZone'],
        operation_id='mapzone_update',
        summary='Update a zone by ID',
        description='Update a zone by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Zone ID'
            )
        ],
        request=MapZoneCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Zone updated',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'zone': 'منطقه 3',
                                'zonepath': None,
                                'description': 'طبرسی شمالی ',
                                'address': None
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Zone not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a zone by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input
            serializer = MapZoneCreateSerializer(data=request.data)
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
            
            # Update instance
            instance.zone = validated_data['zone']
            instance.zonepath = validated_data.get('zonepath', '')
            instance.description = validated_data.get('description', '')
            instance.address = validated_data.get('address', '')
            instance.save()
            
            # Return updated data
            response_serializer = self.get_serializer(instance)
            return create_success_response(data=response_serializer.data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Zone matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Zone with ID "{self.kwargs.get("pk")}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Zone with ID "{self.kwargs.get("pk")}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['MapZone'],
        operation_id='mapzone_destroy',
        summary='Delete a zone by ID',
        description='Delete a zone by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='Zone ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Zone deleted',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'zone': 'منطقه 3',
                                'zonepath': None,
                                'description': 'طبرسی شمالی ',
                                'address': None
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Zone not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a zone by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Get data before deletion
            response_serializer = self.get_serializer(instance)
            data = response_serializer.data
            
            # Delete instance
            instance.delete()
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Zone matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Zone with ID "{self.kwargs.get("pk")}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Zone with ID "{self.kwargs.get("pk")}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['MapZone'],
        operation_id='mapzone_create',
        summary='Create a new zone',
        description='Create a new zone matching old Swagger format.',
        request=MapZoneCreateSerializer,
        examples=[
            OpenApiExample(
                'Create zone',
                value={
                    'zone': 'string',
                    'zonepath': 'string',
                    'description': 'string',
                    'address': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Zone created successfully',
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
    def create(self, request, *args, **kwargs):
        """Create a new zone matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input using old Swagger format serializer
            serializer = MapZoneCreateSerializer(data=request_data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            # Create zone
            zone = serializer.save()
            
            # Return response matching old Swagger format (zone ID as integer)
            return create_success_response(data=zone.id, messages=[], status_code=status.HTTP_200_OK)
        
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
        tags=['MapZone'],
        operation_id='mapzone_search',
        summary='Search MapZone using available Filters',
        description='Search MapZone using available Filters matching old Swagger format.',
        request=MapZoneSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search zones',
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
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search zones with pagination matching old Swagger format."""
        try:
            # Handle empty request body - all fields are optional
            # DRF serializers can handle both dict and QueryDict directly
            try:
                request_data = request.data if request.data else {}
            except AttributeError:
                # If request.data itself causes AttributeError, use empty dict
                request_data = {}
            
            # Validate input
            serializer = MapZoneSearchRequestSerializer(data=request_data)
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
            
            # Get pagination parameters (can be 0)
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Get keyword from request or advancedSearch
            keyword = validated_data.get('keyword') or ''
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and isinstance(advanced_search, dict) and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword') or keyword
            
            # Build query
            qs = Zone.objects.all()
            
            # Apply keyword search
            if keyword:
                qs = qs.filter(
                    Q(zone__icontains=keyword) |
                    Q(zonepath__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(address__icontains=keyword)
                )
            
            # Apply orderBy if provided
            order_by = validated_data.get('orderBy', [])
            valid_order_fields = ['zone', 'zonepath', 'description', 'address', 'created_at']
            if order_by:
                # Filter valid fields and add '-' prefix for descending if needed
                order_fields = []
                for field in order_by:
                    if field and field.strip():
                        field_clean = field.strip().lstrip('-')
                        if field_clean in valid_order_fields:
                            if field.startswith('-'):
                                order_fields.append(f'-{field_clean}')
                            else:
                                order_fields.append(field_clean)
                if order_fields:
                    qs = qs.order_by(*order_fields)
                else:
                    qs = qs.order_by('zone')
            else:
                qs = qs.order_by('zone')
            
            # Get total count
            total_count = qs.count()
            items_data = []
            
            # Calculate pagination
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
                # Handle pageNumber 0 - treat as page 1
                effective_page = page_number if page_number > 0 else 1
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
                
                # Apply pagination
                start = (effective_page - 1) * page_size
                end = start + page_size
                items = qs[start:end]
                serializer = ZoneSerializer(items, many=True)
                items_data = serializer.data
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                has_previous = False
                has_next = False
                serializer = ZoneSerializer(qs, many=True)
                items_data = serializer.data
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 1 if empty, as per old Swagger example)
            response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 1)
            
            response_data = {
                'data': items_data,
                'currentPage': effective_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': response_page_size,
                'hasPreviousPage': has_previous,
                'hasNextPage': has_next,
                'messages': None,  # Old Swagger shows null, not empty array
                'succeeded': True
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            import traceback
            import logging
            error_detail = str(e)
            error_type = type(e).__name__
            traceback_str = traceback.format_exc()
            
            # Log the full traceback for debugging
            logger = logging.getLogger(__name__)
            logger.error(f'MapZone search error: {error_type}: {error_detail}\n{traceback_str}')
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )


@extend_schema(
    tags=['MapZone'],
    operation_id='mapzone_searchuserinzone',
    summary='Search users in zone',
    description='Search users in a specific zone matching old Swagger format. Accepts zoneId as query parameter.',
    parameters=[
        OpenApiParameter(
            name='zoneId',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Zone ID to search users in'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of users in zone',
            examples=[
                OpenApiExample(
                    'Success response',
                    value=[]
                )
            ]
        ),
        400: {'description': 'Validation error'}
    }
)
class MapZoneSearchUserInZoneView(APIView):
    """POST /api/v1/mapzone/searchuserinzone - Search users in zone"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search users in a specific zone matching old Swagger format."""
        try:
            # Get zoneId from query parameter
            zone_id = request.query_params.get('zoneId')
            
            if not zone_id:
                return create_error_response(
                    error_message='zoneId is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'zoneId': ['zoneId is required as query parameter']}
                )
            
            try:
                zone_id = int(zone_id)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message='zoneId must be an integer',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'zoneId': ['zoneId must be an integer']}
                )
            
            # Check if zone exists
            try:
                zone = Zone.objects.get(pk=zone_id)
            except Zone.DoesNotExist:
                return create_error_response(
                    error_message=f'Zone with ID "{zone_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'zoneId': [f'Zone with ID "{zone_id}" not found.']}
                )
            
            # Old Swagger returns empty array
            return Response([], status=status.HTTP_200_OK)
        
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
    tags=['MapZone'],
    operation_id='mapzone_userinzone',
    summary='Get zones for user',
    description='Get zones for a specific user matching old Swagger format. Accepts userId as query parameter.',
    parameters=[
        OpenApiParameter(
            name='userid',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='User ID (UUID) to get zones for'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of user zones',
            examples=[
                OpenApiExample(
                    'Success response',
                    value=[]
                )
            ]
        ),
        400: {'description': 'Validation error'},
        404: {'description': 'User not found'}
    }
)
class MapZoneUserInZoneView(APIView):
    """POST /api/v1/mapzone/userinzone - Get zones for user"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Get zones for a specific user matching old Swagger format."""
        try:
            # Get userid from query parameter
            user_id_str = request.query_params.get('userid')
            
            if not user_id_str:
                return create_error_response(
                    error_message='userid is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userid': ['userid is required as query parameter']}
                )
            
            # Get user by UUID
            try:
                user_uuid = uuid.UUID(user_id_str)
                user = User.objects.get(pk=user_uuid)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message=f'Invalid user ID format: "{user_id_str}". Expected UUID.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'userid': [f'Invalid user ID format: "{user_id_str}". Expected UUID.']}
                )
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{user_id_str}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'userid': [f'User with ID "{user_id_str}" not found.']}
                )
            
            # Old Swagger returns empty array
            return Response([], status=status.HTTP_200_OK)
        
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
    tags=['MapZone'],
    operation_id='mapzone_createuserinzone',
    summary='Create user in zone',
    description='Assign a user to a zone matching old Swagger format.',
    request=MapZoneCreateUserInZoneRequestSerializer,
    examples=[
        OpenApiExample(
            'Create user in zone',
            value={
                'userId': 'string',
                'zoneId': 0
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='User-zone relationship created successfully',
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
        400: {'description': 'Validation error'},
        404: {'description': 'User or Zone not found'}
    }
)
class MapZoneCreateUserInZoneView(APIView):
    """POST /api/v1/mapzone/createuserinzone - Create user in zone"""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Create user-zone relationship matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = MapZoneCreateUserInZoneRequestSerializer(data=request_data)
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
            user_id_str = validated_data['userId']
            zone_id = validated_data['zoneId']
            
            # Get user by UUID or phone number
            try:
                # Try UUID first
                user_uuid = uuid.UUID(user_id_str)
                user = User.objects.get(pk=user_uuid)
            except (ValueError, TypeError):
                # If not UUID, try phone number
                try:
                    user = User.objects.get(phone_number=user_id_str)
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{user_id_str}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{user_id_str}" not found.']}
                    )
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{user_id_str}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'userId': [f'User with ID "{user_id_str}" not found.']}
                )
            
            # Get zone
            try:
                zone = Zone.objects.get(pk=zone_id)
            except Zone.DoesNotExist:
                return create_error_response(
                    error_message=f'Zone with ID "{zone_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'zoneId': [f'Zone with ID "{zone_id}" not found.']}
                )
            
            # Create or get user-zone relationship
            user_zone, created = UserZone.objects.get_or_create(
                user=user,
                zone=zone,
                defaults={}
            )
            
            # Return response matching old Swagger format (user_zone ID as integer)
            return create_success_response(data=user_zone.id, messages=[], status_code=status.HTTP_200_OK)
        
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
    tags=['MapZone'],
    operation_id='mapzone_userinzone_delete',
    summary='Delete user in zone',
    description='Remove a user from a zone matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='UserZone ID (can be 0 or actual ID)'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='User-zone relationship deleted',
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
        404: {'description': 'UserZone not found'}
    }
)
class MapZoneUserInZoneDeleteView(APIView):
    """DELETE /api/v1/mapzone/userinzone/{id} - Delete user in zone"""
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, id):
        """Delete user-zone relationship matching old Swagger format."""
        try:
            # Handle id=0 case (old Swagger accepts 0)
            if id == 0:
                return create_success_response(data=None, messages=[])
            
            try:
                user_zone = UserZone.objects.get(pk=id)
                user_zone.delete()
                return create_success_response(data=None, messages=[])
            except UserZone.DoesNotExist:
                return create_error_response(
                    error_message=f'UserZone with ID "{id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'UserZone with ID "{id}" not found.']}
                )
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

