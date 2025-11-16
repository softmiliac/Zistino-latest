"""
Compatibility views for Localizations endpoints.
All endpoints will appear under "Localizations" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Localizations
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count
from zistino_apps.users.permissions import IsManager

from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .models import Localization
from .serializers import (
    LocalizationSerializer,
    LocalizationCreateSerializer,
    LocalizationSearchRequestSerializer,
    ResourceSetSerializer,
    LocalizationByResourceSetSerializer,
    LocalizationDetailSerializer
)
import uuid
import hashlib
from django.http import Http404


@extend_schema(tags=['Localizations'])
class LocalizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing localizations.
    All endpoints will appear under "Localizations" folder in Swagger UI.
    """
    queryset = Localization.objects.all()
    serializer_class = LocalizationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_value_regex = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9]+'  # Accept UUID or integer

    def get_queryset(self):
        """Return all localizations."""
        return Localization.objects.all().order_by('resource_set', 'key', 'locale')

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Use different serializer for create and retrieve."""
        if self.action == 'create':
            return LocalizationCreateSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return LocalizationDetailSerializer
        return LocalizationSerializer
    
    def get_object_by_id(self, id_value):
        """Helper method to get object by ID (UUID or integer)."""
        # Try to parse as UUID first
        try:
            lookup_uuid = uuid.UUID(str(id_value))
            return Localization.objects.get(pk=lookup_uuid)
        except (ValueError, TypeError):
            # If not UUID, try as integer (hash-based lookup)
            try:
                lookup_int = int(id_value)
                # Find localization by converting UUIDs to integers and matching
                for loc in Localization.objects.all():
                    loc_id_hash = int(hashlib.md5(str(loc.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
                    if loc_id_hash == lookup_int:
                        return loc
                raise Http404('No Localization matches the given query.')
            except (ValueError, TypeError):
                raise Http404('Invalid ID format.')
    
    def get_object(self):
        """Override to support both UUID and integer IDs."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        return self.get_object_by_id(lookup_value)
    
    @extend_schema(
        tags=['Localizations'],
        operation_id='localizations_retrieve',
        summary='Retrieve a localization by ID',
        description='Retrieve a localization by its ID matching old Swagger format. Accepts both UUID and integer IDs.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Localization ID (UUID or integer)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Localization details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'resourceSet': 'string',
                                'locale': 'string',
                                'key': 'asd',
                                'text': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Localization not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a localization by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = LocalizationDetailSerializer(instance)
            
            # Convert UUID to integer for response
            localization_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            data = serializer.data
            data['id'] = localization_id_hash
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Localization matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Localization with ID "{self.kwargs.get(self.lookup_field)}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Localization with ID "{self.kwargs.get(self.lookup_field)}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['Localizations'],
        operation_id='localizations_update',
        summary='Update a localization by ID',
        description='Update a localization by its ID matching old Swagger format. Accepts both UUID and integer IDs.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Localization ID (UUID or integer)'
            )
        ],
        request=LocalizationCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Localization updated',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'resourceSet': 'string',
                                'locale': 'string',
                                'key': 'asd',
                                'text': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Localization not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a localization by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input
            serializer = LocalizationCreateSerializer(data=request.data)
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
            instance.resource_set = validated_data['resourceSet']
            instance.locale = validated_data['locale']
            instance.key = validated_data['key']
            instance.value = validated_data['text']  # Map 'text' to 'value'
            instance.save()
            
            # Return updated data
            response_serializer = LocalizationDetailSerializer(instance)
            localization_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            data = response_serializer.data
            data['id'] = localization_id_hash
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Localization matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Localization with ID "{self.kwargs.get(self.lookup_field)}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Localization with ID "{self.kwargs.get(self.lookup_field)}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['Localizations'],
        operation_id='localizations_destroy',
        summary='Delete a localization by ID',
        description='Delete a localization by its ID matching old Swagger format. Accepts both UUID and integer IDs.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Localization ID (UUID or integer)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Localization deleted',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'resourceSet': 'string',
                                'locale': 'string',
                                'key': 'asd',
                                'text': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Localization not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a localization by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Get data before deletion
            response_serializer = LocalizationDetailSerializer(instance)
            localization_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            data = response_serializer.data
            data['id'] = localization_id_hash
            
            # Delete instance
            instance.delete()
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No Localization matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Localization with ID "{self.kwargs.get(self.lookup_field)}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Localization with ID "{self.kwargs.get(self.lookup_field)}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['Localizations'],
        operation_id='localizations_create',
        summary='Create a new localization',
        description='Create a new localization matching old Swagger format.',
        request=LocalizationCreateSerializer,
        examples=[
            OpenApiExample(
                'Create localization',
                value={
                    'resourceSet': 'string',
                    'locale': 'string',
                    'key': 'string',
                    'text': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Localization created successfully',
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
    def create(self, request, *args, **kwargs):
        """Create a new localization matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input using old Swagger format serializer
            serializer = LocalizationCreateSerializer(data=request_data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            # Create localization
            localization = serializer.save()
            
            # Convert UUID to integer for response (using hash for consistent mapping)
            import hashlib
            localization_id_hash = int(hashlib.md5(str(localization.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            
            # Return response matching old Swagger format
            return create_success_response(data=localization_id_hash, messages=[], status_code=status.HTTP_200_OK)
        
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
        tags=['Localizations'],
        operation_id='localizations_dapper',
        summary='Get localizations (dapper context)',
        description='Get localizations in dapper context matching old Swagger format. Accepts optional id query parameter.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Localization ID (UUID or integer)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Dapper context',
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
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get localizations in dapper context matching old Swagger format."""
        # Check if id parameter is provided
        id_param = request.query_params.get('id')
        if id_param:
            try:
                # Try to get the localization
                instance = self.get_object_by_id(id_param)
                serializer = LocalizationDetailSerializer(instance)
                localization_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
                data = serializer.data
                data['id'] = localization_id_hash
                return create_success_response(data=data, messages=[])
            except (Http404, Localization.DoesNotExist):
                # If not found, return null
                return create_success_response(data=None, messages=[])
        
        # Old Swagger returns null for dapper when no ID
        return create_success_response(data=None, messages=[])

    @extend_schema(
        tags=['Localizations'],
        operation_id='localizations_search',
        summary='Search Localization using available Filters',
        description='Search Localization using available Filters matching old Swagger format.',
        request=LocalizationSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search localizations',
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
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search localizations with pagination matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = LocalizationSearchRequestSerializer(data=request_data)
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
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword') or keyword
            
            # Build query
            qs = Localization.objects.all()
            
            # Apply keyword search
            if keyword:
                qs = qs.filter(
                    Q(key__icontains=keyword) |
                    Q(value__icontains=keyword) |
                    Q(resource_set__icontains=keyword) |
                    Q(locale__icontains=keyword)
                )
            
            # Apply orderBy if provided
            order_by = validated_data.get('orderBy', [])
            valid_order_fields = ['key', 'value', 'resource_set', 'locale', 'created_at', 'updated_at']
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
                    qs = qs.order_by('resource_set', 'key', 'locale')
            else:
                qs = qs.order_by('resource_set', 'key', 'locale')
            
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
                serializer = self.get_serializer(items, many=True)
                items_data = serializer.data
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                has_previous = False
                has_next = False
                serializer = self.get_serializer(qs, many=True)
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
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )


@extend_schema(
    tags=['Localizations'],
    operation_id='localizations_resourcesets',
    summary='Get resource sets',
    description='Get list of all resource sets matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of resource set names',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': ['asdf', 'string'],
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class LocalizationsResourceSetsView(APIView):
    """GET /api/v1/localizations/resourcesets - Get resource sets"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get list of all resource sets matching old Swagger format."""
        # Get unique resource set names
        resource_sets = Localization.objects.values_list('resource_set', flat=True).distinct().order_by('resource_set')
        
        # Return as array of strings
        return create_success_response(data=list(resource_sets), messages=[])


@extend_schema(
    tags=['Localizations'],
    operation_id='localizations_client_by_resourceset',
    summary='Get localizations by resource set',
    description='Get localizations for a specific resource set matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of localizations',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [],
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class LocalizationsClientByResourceSetView(APIView):
    """GET /api/v1/localizations/client/by-resourceset/{set} - Get localizations by resource set"""
    permission_classes = [AllowAny]

    def get(self, request, set):
        """Get localizations for a specific resource set matching old Swagger format."""
        locale = request.query_params.get('locale', 'en')
        
        localizations = Localization.objects.filter(
            resource_set=set,
            locale=locale,
            is_active=True
        ).order_by('key')

        # Return as array matching old Swagger format
        # Old Swagger returns empty array, but we could return localization objects if needed
        return create_success_response(data=[], messages=[])

