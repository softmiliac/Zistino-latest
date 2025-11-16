from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, inline_serializer
from rest_framework import serializers

from .models import Address
from .serializers import AddressSerializer


@extend_schema(tags=['Customer'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Addresses" folder instead
class CustomerAddressViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        qs = Address.objects.filter(user=request.user).order_by('-id')
        return Response(AddressSerializer(qs, many=True).data)

    @extend_schema(
        request=AddressSerializer,
        examples=[
            OpenApiExample(
                'Create address',
                value={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone_number": "+989121234567",
                    "address": "No. 10, Example St",
                    "description": "Near park",
                    "plate": "12",
                    "unit": "3",
                    "city": "Tehran",
                    "province": "Tehran",
                    "country": "IR",
                    "zip_code": "1234567890",
                    "company_name": "Acme Co",
                    "company_number": "12345",
                    "vat_number": "IR1234567890",
                    "latitude": 35.6892,
                    "longitude": 51.3890
                }
            )
        ]
    )
    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = AddressSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            obj = Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AddressSerializer(obj).data)

    @extend_schema(request=AddressSerializer)
    def update(self, request, pk=None):
        try:
            obj = Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = AddressSerializer(obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        deleted, _ = Address.objects.filter(pk=pk, user=request.user).delete()
        if not deleted:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsManager
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

User = get_user_model()
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    AddressSerializer,
    VehicleSerializer,
    ZoneSerializer,
    UserZoneSerializer,
    EmptyRequestSerializer,
    UserInZoneRequestSerializer,
)
from .models import Address, Vehicle, Zone, UserZone


@extend_schema(tags=['Users'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Personal" folder instead
class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Users'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Personal" folder instead
class UserProfileView(APIView):
    """Get current user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Users'])
class UploadProfileImageView(APIView):
    """Upload profile image"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['image']
        user = request.user
        user.image_url = image
        user.save()

        serializer = UserProfileSerializer(user)
        return Response({
            'message': 'Profile image uploaded successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Users'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "Addresses" folder instead
class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Users'])
class VehicleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VehicleSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    tags=['Customer'],
    operation_id='searchuserinzone',
    request=inline_serializer(
        name='EmptyRequest',
        fields={},
    ),
    parameters=[
        OpenApiParameter(
            name='zoneId',
            type=int,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Zone ID to filter users (required as query parameter: ?zoneId=1)',
            examples=[
                OpenApiExample('Zone 1', value=1),
                OpenApiExample('Zone 2', value=2),
            ]
        ),
    ],
    examples=[
        OpenApiExample(
            'Empty request body',
            description='Request body should be an empty JSON object: {}. Pass zoneId as query parameter in the URL: ?zoneId=1',
            value={},
        ),
    ]
)
@extend_schema(tags=['Admin'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "MapZone" folder instead
class ZoneUserSearchView(APIView):
    """Search users by zone ID - matches UserZoneModel structure."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        zone_id = request.query_params.get('zoneId')
        if not zone_id:
            return Response({'detail': 'zoneId is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            zone_id = int(zone_id)
        except ValueError:
            return Response({'detail': 'zoneId must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        user_zones = UserZone.objects.filter(zone_id=zone_id).select_related('user', 'zone')
        data = UserZoneSerializer(user_zones, many=True).data
        return Response(data)


# ============================================
# MANAGER ENDPOINTS - Separated for clarity
# ============================================
# These endpoints are for managers only (is_staff=True)
# They provide admin-level access to all resources
# ============================================

@extend_schema(
    tags=['Manager'],
    operation_id='users_userbyrole',
    request=inline_serializer(
        name='UserByRoleRequest',
        fields={
            'role': serializers.CharField(help_text='Role to filter: "driver", "customer", etc.', required=False, allow_blank=True),
            'isActive': serializers.BooleanField(help_text='Filter by active status', required=False),
        }
    ),
    examples=[
        OpenApiExample(
            'Get all drivers',
            description='Get all users with driver role',
            value={
                "role": "driver",
                "isActive": True
            }
        ),
        OpenApiExample(
            'Get all active users',
            description='Get all active users regardless of role',
            value={
                "isActive": True
            }
        )
    ]
)
class ManagerUserByRoleView(APIView):
    """Get users by role - Manager-only endpoint matching userbyrole."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Get users filtered by role and status."""
        role = request.data.get('role', '').lower()
        is_active = request.data.get('isActive')
        
        queryset = User.objects.all()
        
        # Filter by role
        if role == 'driver':
            queryset = queryset.filter(is_driver=True)
        elif role == 'customer':
            queryset = queryset.filter(is_driver=False)
        
        # Filter by active status
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        serializer = UserSerializer(queryset.order_by('-created_at'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Admin'],
    operation_id='drivers_by_zone',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'zoneId': {'type': 'integer', 'description': 'Zone ID to filter drivers (optional)'},
            }
        }
    },
    examples=[
        OpenApiExample(
            'Get all drivers',
            description='Get all active drivers across all zones',
            value={}
        ),
        OpenApiExample(
            'Get drivers in specific zone',
            description='Get only drivers assigned to zone ID 1',
            value={
                'zoneId': 1
            }
        ),
        OpenApiExample(
            'Get drivers in zone 2',
            value={
                'zoneId': 2
            }
        )
    ],
    responses={
        200: {
            'description': 'List of drivers',
            'content': {
                'application/json': {
                    'example': {
                        'drivers': [
                            {
                                'id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                'name': 'John Doe',
                                'phone_number': '+989121234567',
                                'zones': ['North Tehran', 'South Tehran']
                            },
                            {
                                'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                'name': 'Jane Smith',
                                'phone_number': '+989121234568',
                                'zones': ['North Tehran']
                            }
                        ]
                    }
                }
            }
        }
    }
)
class DriversByZoneView(APIView):
    """Get list of drivers for dropdown selection, optionally filtered by zone. Used for manual delivery transfer."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def post(self, request):
        """Get drivers list for dropdown. Optionally filter by zoneId."""
        from .serializers import UserSerializer
        
        zone_id = request.data.get('zoneId')
        
        # Start with all active drivers
        queryset = User.objects.filter(is_driver=True, is_active=True, is_active_driver=True)
        
        # Filter by zone if provided
        if zone_id:
            user_zones = UserZone.objects.filter(zone_id=zone_id, user__is_driver=True, user__is_active=True)
            driver_ids = [uz.user.id for uz in user_zones]
            queryset = queryset.filter(id__in=driver_ids)
        
        # Return simplified driver list for dropdown
        drivers_data = [{
            'id': str(driver.id),
            'name': f"{driver.first_name} {driver.last_name}".strip() or driver.phone_number,
            'phone_number': driver.phone_number,
            'zones': [uz.zone.zone for uz in driver.user_zones.all()]
        } for driver in queryset.order_by('first_name', 'last_name')]
        
        return Response({
            'drivers': drivers_data
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Manager'])
class ManagerVehicleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managers to view all vehicles - Manager-only."""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        """Return all vehicles (no filtering by user)."""
        return Vehicle.objects.all().select_related('user').order_by('-created_at')


# ============================================
# ADMIN ENDPOINTS - Separated for clarity
# ============================================
# These endpoints are for admin panel (is_staff=True)
# They provide admin-level access with search/pagination
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='users_search',
    request=inline_serializer(
        name='UserSearchRequest',
        fields={
            'pageNumber': serializers.IntegerField(required=False, min_value=1, default=1),
            'pageSize': serializers.IntegerField(required=False, min_value=1, default=20),
            'keyword': serializers.CharField(required=False, allow_blank=True, default=""),
        }
    ),
    examples=[
        OpenApiExample(
            'Search users',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': 'john'
            }
        )
    ]
)
class AdminUserSearchView(APIView):
    """Admin search endpoint for users with pagination."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search users with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        
        qs = User.objects.all()
        
        if keyword:
            # Search in username, email, phone, full name
            from django.db.models import Q
            q = Q(username__icontains=keyword) | Q(email__icontains=keyword) | Q(phone_number__icontains=keyword)
            # If user has first_name/last_name fields
            try:
                q = q | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            except:
                pass
            qs = qs.filter(q)
        
        qs = qs.order_by('-created_at')
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': UserSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


# ============================================
# ZONE MANAGEMENT ENDPOINTS
# ============================================
# Admin endpoints for managing zones and user-zone relationships
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='mapzone_search',
    exclude=True,  # Excluded from Swagger - use compatibility endpoints in "MapZone" folder instead
    request=inline_serializer(
        name='ZoneSearchRequest',
        fields={
            'pageNumber': serializers.IntegerField(required=False, min_value=1, default=1),
            'pageSize': serializers.IntegerField(required=False, min_value=1, default=20),
            'keyword': serializers.CharField(required=False, allow_blank=True, default=""),
        }
    ),
    examples=[
        OpenApiExample(
            'Search zones',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': 'north'
            }
        ),
        OpenApiExample(
            'Get all zones',
            value={}
        )
    ]
)
class ZoneSearchView(APIView):
    """Admin search endpoint for zones with pagination."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search zones with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        
        qs = Zone.objects.all()
        
        if keyword:
            from django.db.models import Q
            qs = qs.filter(
                Q(zone__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(address__icontains=keyword)
            )
        
        qs = qs.order_by('zone')
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': ZoneSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Admin'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "MapZone" folder instead
class ZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for managing zones - Admin-only."""
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        """Return all zones ordered by name."""
        return Zone.objects.all().order_by('zone')


@extend_schema(
    tags=['Admin'],
    operation_id='mapzone_createuserinzone',
    request=inline_serializer(
        name='CreateUserZoneRequest',
        fields={
            'userId': serializers.UUIDField(required=True, help_text='User ID to assign to zone'),
            'zoneId': serializers.IntegerField(required=True, help_text='Zone ID to assign user to'),
        }
    ),
    examples=[
        OpenApiExample(
            'Assign user to zone',
            value={
                'userId': '46e818ce-0518-4c64-8438-27bc7163a706',
                'zoneId': 1
            }
        )
    ]
)
@extend_schema(tags=['Admin'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "MapZone" folder instead
class CreateUserZoneView(APIView):
    """Assign a user to a zone - Admin-only."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Create a user-zone relationship."""
        user_id = request.data.get('userId') or request.data.get('user_id') or request.data.get('user')
        zone_id = request.data.get('zoneId') or request.data.get('zone_id') or request.data.get('zone')
        
        if not user_id:
            return Response({'detail': 'userId is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not zone_id:
            return Response({'detail': 'zoneId is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            zone = Zone.objects.get(pk=zone_id)
        except Zone.DoesNotExist:
            return Response({'detail': 'Zone not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create or get existing UserZone
        user_zone, created = UserZone.objects.get_or_create(
            user=user,
            zone=zone,
            defaults={'user': user, 'zone': zone}
        )
        
        if created:
            return Response(UserZoneSerializer(user_zone).data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'detail': 'User already assigned to this zone',
                'data': UserZoneSerializer(user_zone).data
            }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Admin'],
    operation_id='mapzone_userinzone',
    exclude=True,  # Excluded from Swagger - use compatibility endpoints in "MapZone" folder instead
    request=UserInZoneRequestSerializer,
    parameters=[
        OpenApiParameter(
            name='userid',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description='User ID to get zones for (alternative to JSON body)',
            examples=[
                OpenApiExample('User ID', value='0641067f-df76-416c-98cd-6f89e43d3b3f'),
            ]
        ),
    ],
    examples=[
        OpenApiExample(
            'Get user zones (POST with JSON body)',
            description='POST /api/v1/mapzone/userinzone with userid in JSON body',
            value={
                'userid': '0641067f-df76-416c-98cd-6f89e43d3b3f'
            }
        ),
        OpenApiExample(
            'Get user zones (GET)',
            description='GET /api/v1/mapzone/userinzone?userid=0641067f-df76-416c-98cd-6f89e43d3b3f',
            value={}
        ),
        OpenApiExample(
            'Get user zones (POST with query param)',
            description='POST /api/v1/mapzone/userinzone?userid=0641067f-df76-416c-98cd-6f89e43d3b3f',
            value={}
        ),
    ]
)
class UserInZoneView(APIView):
    """Get all zones for a specific user - Admin-only. Supports both GET and POST methods."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get zones assigned to a user (GET method)."""
        return self._get_user_zones(request)

    def post(self, request):
        """Get zones assigned to a user (POST method)."""
        return self._get_user_zones(request)

    def _get_user_zones(self, request):
        """Common method to get user zones."""
        # Try query parameter first (works for both GET and POST)
        user_id = request.query_params.get('userid') or request.query_params.get('user_id')
        
        # If not in query params and POST request, try request body
        if not user_id and request.method == 'POST':
            user_id = (
                request.data.get('userid') or 
                request.data.get('user_id') or 
                request.data.get('userId') or
                request.data.get('user')
            )
        
        if not user_id:
            return Response({
                'detail': 'userid is required. Pass it as query parameter (?userid=...) or in JSON body ({"userid": "..."})'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user_zones = UserZone.objects.filter(user=user).select_related('zone').order_by('-last_modified_on')
        
        return Response({
            'items': UserZoneSerializer(user_zones, many=True).data,
            'total': user_zones.count()
        })


@extend_schema(tags=['Admin'], exclude=True)  # Excluded from Swagger - use compatibility endpoints in "MapZone" folder instead
class UserZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user-zone relationships - Admin-only."""
    queryset = UserZone.objects.all()
    serializer_class = UserZoneSerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        """Return all user-zone relationships."""
        return UserZone.objects.all().select_related('user', 'zone').order_by('-last_modified_on')
