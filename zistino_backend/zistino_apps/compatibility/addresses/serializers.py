"""
Serializers for Addresses compatibility layer.
"""
from rest_framework import serializers
from zistino_apps.users.models import Address


class AddressCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating address matching old Swagger format."""
    userId = serializers.UUIDField(required=True, help_text='User UUID')
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True, help_text='Latitude')
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True, help_text='Longitude')
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Street address')
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='ZIP code')
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Full name')
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Phone number')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Description')
    plate = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Plate number')
    unit = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Unit number')
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Country')
    province = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Province/State')
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='City')
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company name')
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company number')
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='VAT number')
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Fax number')
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Website URL')
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Email address')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Address title/label')
    
    def validate_website(self, value):
        """Validate website URL only if provided and not empty."""
        if value and value.strip():
            # Use URLField validation for non-empty values
            from rest_framework.fields import URLField
            url_field = URLField()
            try:
                return url_field.to_internal_value(value)
            except Exception:
                # If URL validation fails, return None (optional field)
                return None
        return None
    
    def validate_email(self, value):
        """Validate email only if provided and not empty."""
        if value and value.strip():
            # Use EmailField validation for non-empty values
            from rest_framework.fields import EmailField
            email_field = EmailField()
            try:
                return email_field.to_internal_value(value)
            except Exception:
                # If email validation fails, return None (optional field)
                return None
        return None


class AddressClientCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating address via client endpoint (userId not required)."""
    userId = serializers.UUIDField(required=False, allow_null=True, help_text='User UUID (ignored, uses current logged-in user)')
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True, help_text='Latitude')
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True, help_text='Longitude')
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Street address')
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='ZIP code')
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Full name')
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Phone number')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Description')
    plate = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Plate number')
    unit = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Unit number')
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Country')
    province = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Province/State')
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='City')
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company name')
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company number')
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='VAT number')
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Fax number')
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Website URL')
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Email address')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Address title/label')
    
    def validate_website(self, value):
        """Validate website URL only if provided and not empty."""
        if value and value.strip():
            # Use URLField validation for non-empty values
            from rest_framework.fields import URLField
            url_field = URLField()
            try:
                return url_field.to_internal_value(value)
            except Exception:
                # If URL validation fails, return None (optional field)
                return None
        return None
    
    def validate_email(self, value):
        """Validate email only if provided and not empty."""
        if value and value.strip():
            # Use EmailField validation for non-empty values
            from rest_framework.fields import EmailField
            email_field = EmailField()
            try:
                return email_field.to_internal_value(value)
            except Exception:
                # If email validation fails, return None (optional field)
                return None
        return None


class AddressCompatibilitySerializer(serializers.ModelSerializer):
    """Compatibility serializer for Address that matches old Swagger output format."""
    userId = serializers.SerializerMethodField()
    zipCode = serializers.CharField(source='zip_code', read_only=True)
    fullName = serializers.CharField(source='full_name', read_only=True)
    phoneNumber = serializers.CharField(source='phone_number', read_only=True)
    companyName = serializers.CharField(source='company_name', read_only=True, allow_null=True)
    companyNumber = serializers.CharField(source='company_number', read_only=True, allow_null=True)
    vatNumber = serializers.CharField(source='vat_number', read_only=True, allow_null=True)

    class Meta:
        model = Address
        fields = [
            'id', 'userId', 'latitude', 'longitude', 'address', 'zipCode', 'fullName',
            'phoneNumber', 'description', 'plate', 'unit', 'country', 'province', 'city',
            'companyName', 'companyNumber', 'vatNumber', 'fax', 'website', 'email', 'title'
        ]
        read_only_fields = ['id']

    def get_userId(self, obj):
        """Return user ID as UUID string."""
        return str(obj.user.id) if obj.user else None


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search parameters."""
    fields = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Search keyword')
    groupBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Group by fields'
    )


class AddressSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching addresses matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search parameters')
    keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, default=1, min_value=1, help_text='Page number (1-based)')
    pageSize = serializers.IntegerField(required=False, default=20, min_value=1, help_text='Page size')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text='Order by fields'
    )

