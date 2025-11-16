"""
Compatibility views for Addresses endpoints.
All endpoints will appear under "Addresses" folder in Swagger UI.
"""
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.models import Address
from zistino_apps.authentication.models import User
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    AddressCreateRequestSerializer, 
    AddressClientCreateRequestSerializer, 
    AddressCompatibilitySerializer,
    AddressSearchRequestSerializer
)


def normalize_website_value(value):
    """Normalize website value - return None if empty or None."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return value


def normalize_email_value(value):
    """Normalize email value - return empty string if None or empty (email field is not nullable)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ''
    return value


@extend_schema(tags=['Addresses'])
class AddressesListView(APIView):
    """GET/POST /api/v1/addresses - List/Create addresses"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_list',
        summary='List addresses',
        description='List all addresses for the current user.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of addresses',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': []
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        """List addresses matching old Swagger format."""
        addresses = Address.objects.filter(user=request.user).order_by('-id')
        serializer = AddressCompatibilitySerializer(addresses, many=True)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_create',
        summary='Create address',
        description='Create a new address matching old Swagger format.',
        request=AddressCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create address',
                value={
                    'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'latitude': 12,
                    'longitude': 11,
                    'address': 'asdfasdfsdf',
                    'zipCode': '1',
                    'fullName': 'nawabi',
                    'phoneNumber': '123123',
                    'description': 'asdfasdfdsf',
                    'plate': 'string',
                    'unit': 'string',
                    'country': 'string',
                    'province': 'string',
                    'city': 'string',
                    'companyName': 'string',
                    'companyNumber': 'string',
                    'vatNumber': 'string',
                    'fax': 'string',
                    'website': 'string',
                    'email': 'string',
                    'title': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Address created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 10010,
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
        """Create address matching old Swagger format. Returns address ID."""
        # Validate input using old Swagger format serializer
        input_serializer = AddressCreateRequestSerializer(data=request.data)
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
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return create_error_response(
                error_message=f'User with ID "{user_id}" does not exist.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'userId': [f'User with ID "{user_id}" not found.']}
            )
        
        # Map old Swagger fields to Django model fields
        address_data = {
            'user': user,
            'latitude': validated_data.get('latitude'),
            'longitude': validated_data.get('longitude'),
            'address': validated_data.get('address') or '',
            'zip_code': validated_data.get('zipCode') or '',
            'full_name': validated_data.get('fullName') or '',
            'phone_number': validated_data.get('phoneNumber') or '',
            'description': validated_data.get('description') or '',
            'plate': validated_data.get('plate') or '',
            'unit': validated_data.get('unit') or '',
            'country': validated_data.get('country') or '',
            'province': validated_data.get('province') or '',
            'city': validated_data.get('city') or '',
            'company_name': validated_data.get('companyName') or None,
            'company_number': validated_data.get('companyNumber') or None,
            'vat_number': validated_data.get('vatNumber') or None,
            'fax': validated_data.get('fax') or None,
            'website': normalize_website_value(validated_data.get('website')),
            'email': normalize_email_value(validated_data.get('email')),
            'title': validated_data.get('title') or None,
        }
        
        # Create address
        address = Address.objects.create(**address_data)
        
        # Return just the address ID wrapped in standard response
        return create_success_response(data=address.id)  # 200 OK to match old Swagger


@extend_schema(tags=['Addresses'])
class AddressesDetailView(APIView):
    """GET/PUT/DELETE /api/v1/addresses/{id} - Retrieve/Update/Delete address"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_retrieve',
        summary='Retrieve address by ID',
        description='Retrieve an address by its ID.',
        responses={
            200: AddressCompatibilitySerializer,
            404: {'description': 'Address not found'}
        }
    )
    def get(self, request, pk):
        """Get address by ID."""
        try:
            address = Address.objects.get(id=int(pk), user=request.user)
            serializer = AddressCompatibilitySerializer(address)
            return create_success_response(data=serializer.data)
        except (Address.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Address with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_update',
        summary='Update address by ID',
        description='Update an address by its ID.',
        request=AddressCreateRequestSerializer,
        responses={
            200: AddressCompatibilitySerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Address not found'}
        }
    )
    def put(self, request, pk):
        """Update address by ID."""
        try:
            address = Address.objects.get(id=int(pk), user=request.user)
        except (Address.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Address with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = AddressCreateRequestSerializer(data=request.data)
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
        
        # Update address fields
        if 'latitude' in validated_data:
            address.latitude = validated_data.get('latitude')
        if 'longitude' in validated_data:
            address.longitude = validated_data.get('longitude')
        if 'address' in validated_data:
            address.address = validated_data.get('address') or ''
        if 'zipCode' in validated_data:
            address.zip_code = validated_data.get('zipCode') or ''
        if 'fullName' in validated_data:
            address.full_name = validated_data.get('fullName') or ''
        if 'phoneNumber' in validated_data:
            address.phone_number = validated_data.get('phoneNumber') or ''
        if 'description' in validated_data:
            address.description = validated_data.get('description') or ''
        if 'plate' in validated_data:
            address.plate = validated_data.get('plate') or ''
        if 'unit' in validated_data:
            address.unit = validated_data.get('unit') or ''
        if 'country' in validated_data:
            address.country = validated_data.get('country') or ''
        if 'province' in validated_data:
            address.province = validated_data.get('province') or ''
        if 'city' in validated_data:
            address.city = validated_data.get('city') or ''
        if 'companyName' in validated_data:
            address.company_name = validated_data.get('companyName') or None
        if 'companyNumber' in validated_data:
            address.company_number = validated_data.get('companyNumber') or None
        if 'vatNumber' in validated_data:
            address.vat_number = validated_data.get('vatNumber') or None
        if 'fax' in validated_data:
            address.fax = validated_data.get('fax') or None
        if 'website' in validated_data:
            address.website = normalize_website_value(validated_data.get('website'))
        if 'email' in validated_data:
            address.email = normalize_email_value(validated_data.get('email'))
        if 'title' in validated_data:
            address.title = validated_data.get('title') or None
        
        address.save()
        
        serializer = AddressCompatibilitySerializer(address)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_delete',
        summary='Delete address by ID',
        description='Delete an address by its ID.',
        responses={
            200: {'description': 'Address deleted successfully'},
            404: {'description': 'Address not found'}
        }
    )
    def delete(self, request, pk):
        """Delete address by ID."""
        try:
            address = Address.objects.get(id=int(pk), user=request.user)
            address.delete()
            return create_success_response(data=None, status_code=status.HTTP_200_OK)
        except (Address.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Address with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['Addresses'])
class AddressesClientView(APIView):
    """GET/POST /api/v1/addresses/client - Get/Create addresses for current user"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_client_list',
        summary='Get addresses of currently logged in user',
        description='Get addresses of currently logged in user.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of addresses',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': []
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        """Get addresses for current user."""
        addresses = Address.objects.filter(user=request.user).order_by('-id')
        serializer = AddressCompatibilitySerializer(addresses, many=True)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_client_create',
        summary='Create address for currently logged in user',
        description='Create address for currently logged in user matching old Swagger format. userId is optional and will be ignored.',
        request=AddressClientCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Address created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 10010,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def post(self, request):
        """Create address for current user matching old Swagger format."""
        # Validate input (userId is optional for client endpoint)
        input_serializer = AddressClientCreateRequestSerializer(data=request.data)
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
        
        # Use current user (userId from request is ignored for client endpoint)
        user = request.user
        
        # Map old Swagger fields to Django model fields
        address_data = {
            'user': user,
            'latitude': validated_data.get('latitude'),
            'longitude': validated_data.get('longitude'),
            'address': validated_data.get('address') or '',
            'zip_code': validated_data.get('zipCode') or '',
            'full_name': validated_data.get('fullName') or '',
            'phone_number': validated_data.get('phoneNumber') or '',
            'description': validated_data.get('description') or '',
            'plate': validated_data.get('plate') or '',
            'unit': validated_data.get('unit') or '',
            'country': validated_data.get('country') or '',
            'province': validated_data.get('province') or '',
            'city': validated_data.get('city') or '',
            'company_name': validated_data.get('companyName') or None,
            'company_number': validated_data.get('companyNumber') or None,
            'vat_number': validated_data.get('vatNumber') or None,
            'fax': validated_data.get('fax') or None,
            'website': normalize_website_value(validated_data.get('website')),
            'email': normalize_email_value(validated_data.get('email')),
            'title': validated_data.get('title') or None,
        }
        
        # Create address
        address = Address.objects.create(**address_data)
        
        # Return just the address ID wrapped in standard response
        return create_success_response(data=address.id)  # 200 OK to match old Swagger


@extend_schema(tags=['Addresses'])
class AddressesClientDetailView(APIView):
    """GET/PUT/DELETE /api/v1/addresses/client/{id} - Retrieve/Update/Delete address for current user"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_client_retrieve',
        summary='Get address by ID for current user',
        description='Get address by ID for currently logged in user.',
        responses={
            200: AddressCompatibilitySerializer,
            404: {'description': 'Address not found'}
        }
    )
    def get(self, request, pk):
        """Get address by ID for current user."""
        try:
            address = Address.objects.get(id=int(pk), user=request.user)
            serializer = AddressCompatibilitySerializer(address)
            return create_success_response(data=serializer.data)
        except (Address.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Address with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_client_update',
        summary='Update address by ID for current user',
        description='Update address by ID for currently logged in user.',
        request=AddressCreateRequestSerializer,
        responses={
            200: AddressCompatibilitySerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Address not found'}
        }
    )
    def put(self, request, pk):
        """Update address by ID for current user."""
        try:
            address = Address.objects.get(id=int(pk), user=request.user)
        except (Address.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Address with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate input
        input_serializer = AddressCreateRequestSerializer(data=request.data)
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
        
        # Update address fields (same logic as AddressesDetailView.put)
        if 'latitude' in validated_data:
            address.latitude = validated_data.get('latitude')
        if 'longitude' in validated_data:
            address.longitude = validated_data.get('longitude')
        if 'address' in validated_data:
            address.address = validated_data.get('address') or ''
        if 'zipCode' in validated_data:
            address.zip_code = validated_data.get('zipCode') or ''
        if 'fullName' in validated_data:
            address.full_name = validated_data.get('fullName') or ''
        if 'phoneNumber' in validated_data:
            address.phone_number = validated_data.get('phoneNumber') or ''
        if 'description' in validated_data:
            address.description = validated_data.get('description') or ''
        if 'plate' in validated_data:
            address.plate = validated_data.get('plate') or ''
        if 'unit' in validated_data:
            address.unit = validated_data.get('unit') or ''
        if 'country' in validated_data:
            address.country = validated_data.get('country') or ''
        if 'province' in validated_data:
            address.province = validated_data.get('province') or ''
        if 'city' in validated_data:
            address.city = validated_data.get('city') or ''
        if 'companyName' in validated_data:
            address.company_name = validated_data.get('companyName') or None
        if 'companyNumber' in validated_data:
            address.company_number = validated_data.get('companyNumber') or None
        if 'vatNumber' in validated_data:
            address.vat_number = validated_data.get('vatNumber') or None
        if 'fax' in validated_data:
            address.fax = validated_data.get('fax') or None
        if 'website' in validated_data:
            address.website = normalize_website_value(validated_data.get('website'))
        if 'email' in validated_data:
            address.email = normalize_email_value(validated_data.get('email'))
        if 'title' in validated_data:
            address.title = validated_data.get('title') or None
        
        address.save()
        
        serializer = AddressCompatibilitySerializer(address)
        return create_success_response(data=serializer.data)
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_client_delete',
        summary='Delete address by ID for current user',
        description='Delete address by ID for currently logged in user.',
        responses={
            200: {'description': 'Address deleted successfully'},
            404: {'description': 'Address not found'}
        }
    )
    def delete(self, request, pk):
        """Delete address by ID for current user."""
        try:
            address = Address.objects.get(id=int(pk), user=request.user)
            address.delete()
            return create_success_response(data=None, status_code=status.HTTP_200_OK)
        except (Address.DoesNotExist, ValueError):
            return create_error_response(
                error_message=f'Address with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['Addresses'])
class AddressesDapperView(APIView):
    """GET /api/v1/addresses/dapper - Get addresses (dapper context)"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_dapper',
        summary='Get addresses (dapper context)',
        description='Get addresses in dapper context.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Address ID. If provided, returns single address.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Address(es) data',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': []
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        """Get addresses in dapper context."""
        address_id = request.query_params.get('id')
        
        if address_id:
            # Return single address by ID
            try:
                address = Address.objects.get(id=int(address_id), user=request.user)
                serializer = AddressCompatibilitySerializer(address)
                return create_success_response(data=serializer.data)
            except (Address.DoesNotExist, ValueError):
                return create_error_response(
                    error_message=f'Address with ID "{address_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return all addresses for current user
            addresses = Address.objects.filter(user=request.user).order_by('-id')
            serializer = AddressCompatibilitySerializer(addresses, many=True)
            return create_success_response(data=serializer.data)


@extend_schema(tags=['Addresses'])
class AddressesByUserIdView(APIView):
    """GET /api/v1/addresses/by-userid - Get addresses by user ID"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_by_userid',
        summary='Get addresses by user ID',
        description='Get addresses by user ID.',
        parameters=[
            OpenApiParameter(
                name='userId',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='User ID. If not provided, returns current user addresses.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of addresses',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': []
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        """Get addresses by user ID."""
        user_id = request.query_params.get('userId')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Only allow if requesting own addresses or is staff
                if user != request.user and not request.user.is_staff:
                    return create_error_response(
                        error_message='You can only view your own addresses.',
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                addresses = Address.objects.filter(user=user).order_by('-id')
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{user_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # Return current user's addresses
            addresses = Address.objects.filter(user=request.user).order_by('-id')
        
        serializer = AddressCompatibilitySerializer(addresses, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(tags=['Addresses'])
class AddressesClientByUserIdView(APIView):
    """GET /api/v1/addresses/client/by-userid - Get addresses of currently logged in user"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_client_by_userid',
        summary='Get addresses of currently logged in user',
        description='Get addresses of currently logged in user.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of addresses',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'messages': [],
                            'succeeded': True,
                            'data': []
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        """Get addresses for current user."""
        addresses = Address.objects.filter(user=request.user).order_by('-id')
        serializer = AddressCompatibilitySerializer(addresses, many=True)
        return create_success_response(data=serializer.data)


@extend_schema(tags=['Addresses'])
class AddressesSearchView(APIView):
    """POST /api/v1/addresses/search - Search addresses"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Addresses'],
        operation_id='addresses_search',
        summary='Search addresses',
        description='Search addresses with filters and pagination matching old Swagger format.',
        request=AddressSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search addresses',
                value={
                    'advancedSearch': {
                        'fields': ['recycle'],
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
                description='Paginated list of addresses',
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
            )
        }
    )
    def post(self, request):
        """Search addresses with filters and pagination matching old Swagger format."""
        # Validate input
        input_serializer = AddressSearchRequestSerializer(data=request.data)
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
        
        # Start with user's addresses
        addresses = Address.objects.filter(user=request.user)
        
        # Get keyword from main keyword or advancedSearch.keyword
        keyword = validated_data.get('keyword', '').strip()
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and advanced_search.get('keyword'):
            keyword = advanced_search.get('keyword', '').strip()
        
        # Apply keyword search
        if keyword:
            addresses = addresses.filter(
                Q(address__icontains=keyword) |
                Q(city__icontains=keyword) |
                Q(full_name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(phone_number__icontains=keyword)
            )
        
        # Handle advancedSearch fields if provided
        if advanced_search and advanced_search.get('fields'):
            # For now, we'll use the fields to determine what to search
            # This is a placeholder - you can extend this logic based on field names
            pass
        
        # Apply ordering
        order_by = validated_data.get('orderBy', [])
        if order_by and any(order_by):  # If orderBy has non-empty values
            # Map orderBy fields to Django model fields
            order_fields = []
            for field in order_by:
                if field and field.strip():
                    # Map camelCase to snake_case
                    field_mapping = {
                        'id': 'id',
                        'address': 'address',
                        'city': 'city',
                        'province': 'province',
                        'country': 'country',
                        'fullName': 'full_name',
                        'phoneNumber': 'phone_number',
                        'createdAt': 'created_at',
                    }
                    django_field = field_mapping.get(field, field)
                    order_fields.append(django_field)
            if order_fields:
                addresses = addresses.order_by(*order_fields)
        else:
            # Default ordering
            addresses = addresses.order_by('-id')
        
        # Pagination
        page_number = validated_data.get('pageNumber', 1)
        page_size = validated_data.get('pageSize', 20)
        
        total = addresses.count()
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        # Calculate pagination
        start = (page_number - 1) * page_size
        end = start + page_size
        paginated_addresses = addresses[start:end]
        
        # Serialize addresses
        serializer = AddressCompatibilitySerializer(paginated_addresses, many=True)
        
        # Return paginated response matching old Swagger format
        response_data = {
            'data': serializer.data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total,
            'pageSize': page_size,
            'hasPreviousPage': page_number > 1,
            'hasNextPage': page_number < total_pages,
            'messages': None,  # Old Swagger shows null, not empty array
            'succeeded': True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

