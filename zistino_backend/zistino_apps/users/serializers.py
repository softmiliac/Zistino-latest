from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address, Vehicle, Zone, UserZone

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'is_active', 'email_confirmed', 'image_url',
            'company_name', 'vat_number', 'representative', 'sheba',
            'bank_name', 'birth_date', 'national_id', 'representative_by',
            'language', 'country', 'city', 'is_driver', 'driver_license_number',
            'vehicle_type', 'vehicle_plate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'phone_number', 'is_active', 'email_confirmed', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'is_active', 'email_confirmed', 'image_url',
            'profile_image_url', 'company_name', 'vat_number', 
            'representative', 'sheba', 'bank_name', 'birth_date', 
            'national_id', 'representative_by', 'language', 'country', 
            'city', 'is_driver', 'driver_license_number', 'vehicle_type', 
            'vehicle_plate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'phone_number', 'is_active', 'email_confirmed', 'created_at', 'updated_at']

    def get_profile_image_url(self, obj):
        if obj.image_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_url.url)
            return obj.image_url.url
        return None


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'full_name', 'email', 'phone_number', 'address', 'description',
            'plate', 'unit', 'city', 'province', 'country', 'zip_code',
            'company_name', 'company_number', 'vat_number', 'fax', 'website', 'title',
            'latitude', 'longitude', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'id', 'user', 'model_make', 'plate_num', 'licence', 'bodytype', 'color',
            'manufacturer', 'registration_num', 'engine_size', 'tank', 'numoftyres',
            'gps_device_id', 'active', 'latitude', 'longitude', 'protocol', 'port',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ZoneSerializer(serializers.ModelSerializer):
    centerLatitude = serializers.DecimalField(source='center_latitude', max_digits=9, decimal_places=6, allow_null=True, required=False)
    centerLongitude = serializers.DecimalField(source='center_longitude', max_digits=9, decimal_places=6, allow_null=True, required=False)
    radiusKm = serializers.DecimalField(source='radius_km', max_digits=10, decimal_places=2, allow_null=True, required=False)
    
    class Meta:
        model = Zone
        fields = ['id', 'zone', 'zonepath', 'description', 'address', 'centerLatitude', 'centerLongitude', 'radiusKm', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserZoneSerializer(serializers.ModelSerializer):
    """Serializer for UserZone matching UserZoneModel structure."""
    userId = serializers.CharField(source='user.id', read_only=True)
    zoneId = serializers.IntegerField(source='zone.id', read_only=True)
    zone = serializers.CharField(source='zone.zone', read_only=True)
    firstName = serializers.CharField(source='user.first_name', read_only=True)
    lastName = serializers.CharField(source='user.last_name', read_only=True)
    lastModifiedOn = serializers.DateTimeField(source='last_modified_on', read_only=True)

    class Meta:
        model = UserZone
        fields = ['id', 'userId', 'zoneId', 'zone', 'firstName', 'lastName', 'lastModifiedOn']
        read_only_fields = ['id', 'userId', 'zoneId', 'zone', 'firstName', 'lastName', 'lastModifiedOn']


class EmptyRequestSerializer(serializers.Serializer):
    """Empty request body serializer for zone search endpoint."""
    pass


class UserInZoneRequestSerializer(serializers.Serializer):
    """Request serializer for getting user zones."""
    userid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text='User ID to get zones for (can also be passed as query parameter)'
    )
