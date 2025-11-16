"""
Serializers for Users endpoints.
Matches Flutter UserModel format (camelCase).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from zistino_apps.users.serializers import UserSerializer, UserProfileSerializer

User = get_user_model()


class UserCompatibilitySerializer(serializers.ModelSerializer):
    """
    Compatibility serializer for User that matches old Swagger format exactly.
    Includes all fields from old Swagger API response.
    """
    # Core fields
    id = serializers.UUIDField(read_only=True)
    userName = serializers.CharField(source='username', read_only=True)
    firstName = serializers.CharField(source='first_name', read_only=True, allow_null=True)
    lastName = serializers.CharField(source='last_name', read_only=True, allow_null=True)
    email = serializers.EmailField(read_only=True, allow_null=True)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    createDate = serializers.SerializerMethodField()
    middleName = serializers.CharField(read_only=True, allow_null=True, default=None)
    gender = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    title = serializers.CharField(read_only=True, allow_null=True, default=None)
    info = serializers.CharField(read_only=True, allow_null=True, default=None)
    emailConfirmed = serializers.BooleanField(source='email_confirmed', read_only=True)
    phoneNumberConfirmed = serializers.SerializerMethodField()
    phoneNumber = serializers.CharField(source='phone_number', read_only=True)
    imageUrl = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    companyName = serializers.CharField(source='company_name', read_only=True, allow_null=True)
    companyNumber = serializers.CharField(read_only=True, allow_null=True, default=None)
    code = serializers.SerializerMethodField()
    codeType = serializers.IntegerField(read_only=True, allow_null=True, default=0)
    companyId = serializers.IntegerField(read_only=True, allow_null=True, default=None)
    jsonExt = serializers.CharField(read_only=True, allow_null=True, default=None)
    vatNumber = serializers.CharField(source='vat_number', read_only=True, allow_null=True)
    representative = serializers.CharField(read_only=True, allow_null=True)
    sheba = serializers.CharField(read_only=True, allow_null=True)
    bankname = serializers.CharField(source='bank_name', read_only=True, allow_null=True)
    birthdate = serializers.SerializerMethodField()
    codeMeli = serializers.CharField(source='national_id', read_only=True, allow_null=True)
    representativeBy = serializers.CharField(source='representative_by', read_only=True, allow_null=True)
    representativeDate = serializers.DateTimeField(read_only=True, allow_null=True, default=None)
    blueUser = serializers.SerializerMethodField()
    blueUSerActiveDate = serializers.DateTimeField(read_only=True, allow_null=True, default=None)
    issue = serializers.CharField(read_only=True, allow_null=True, default=None)
    rolesRequests = serializers.CharField(read_only=True, allow_null=True, default=None)
    instagram = serializers.CharField(read_only=True, allow_null=True, default=None)
    facebook = serializers.CharField(read_only=True, allow_null=True, default=None)
    linkedIn = serializers.CharField(read_only=True, allow_null=True, default=None)
    twitter = serializers.CharField(read_only=True, allow_null=True, default=None)
    gitHub = serializers.CharField(read_only=True, allow_null=True, default=None)
    skype = serializers.CharField(read_only=True, allow_null=True, default=None)
    telegram = serializers.CharField(read_only=True, allow_null=True, default=None)
    whatsApp = serializers.CharField(read_only=True, allow_null=True, default=None)
    follower = serializers.IntegerField(read_only=True, default=0)
    following = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = User
        fields = [
            'id', 'userName', 'firstName', 'lastName', 'email', 'isActive', 'createDate',
            'middleName', 'gender', 'title', 'info', 'emailConfirmed', 'phoneNumberConfirmed',
            'phoneNumber', 'imageUrl', 'thumbnail', 'companyName', 'companyNumber', 'code',
            'codeType', 'companyId', 'jsonExt', 'vatNumber', 'representative', 'sheba',
            'bankname', 'birthdate', 'codeMeli', 'representativeBy', 'representativeDate',
            'blueUser', 'blueUSerActiveDate', 'issue', 'rolesRequests', 'instagram',
            'facebook', 'linkedIn', 'twitter', 'gitHub', 'skype', 'telegram', 'whatsApp',
            'follower', 'following'
        ]
    
    def get_createDate(self, obj):
        """Get createDate in ISO format without Z (old Swagger format: "2025-11-06T21:38:06.697")."""
        if obj.created_at:
            dt_str = obj.created_at.isoformat()
            # Remove timezone info and Z
            if dt_str.endswith('+00:00'):
                dt_str = dt_str[:-6]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return dt_str
        return None
    
    def get_phoneNumberConfirmed(self, obj):
        """Phone number is confirmed if user is active and has phone number."""
        return bool(obj.phone_number and obj.is_active)
    
    def get_imageUrl(self, obj):
        """Get image URL as relative path string (old Swagger format: "/uploads/app/...")."""
        if obj.image_url:
            # Get relative URL path (like "/uploads/app/image.webp")
            image_url = obj.image_url.url
            # If it's already a full URL, extract the path
            if image_url.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                image_url = parsed.path
            return image_url
        return None
    
    def get_thumbnail(self, obj):
        """Get thumbnail URL as relative path string (old Swagger format: "/uploads/app/...")."""
        if obj.image_url:
            # Get relative URL path (like "/uploads/app/image.180.webp")
            image_url = obj.image_url.url
            # If it's already a full URL, extract the path
            if image_url.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                image_url = parsed.path
            # For thumbnail, try to get a thumbnail version if available
            # For now, return the same path (old Swagger might have different logic)
            return image_url
        return None
    
    def get_code(self, obj):
        """Get user code (old Swagger returns "0" as default)."""
        # Old Swagger returns "0" as default, not None
        return "0"
    
    def get_birthdate(self, obj):
        """Get birthdate as datetime string (ISO format without Z: "2025-10-12T20:30:00")."""
        if obj.birth_date:
            # Convert date to datetime at midnight, then to ISO string without Z
            from django.utils import timezone
            from datetime import datetime
            dt = datetime.combine(obj.birth_date, datetime.min.time())
            if timezone.is_aware(dt):
                dt = timezone.make_naive(dt)
            # Return ISO format without Z (old Swagger format: "2025-10-12T20:30:00")
            return dt.isoformat()
        return None
    
    def get_blueUser(self, obj):
        """Get blue user status (placeholder)."""
        # TODO: Implement blue badge logic if needed
        return None
    
    def to_representation(self, instance):
        """Convert to old Swagger format."""
        data = super().to_representation(instance)
        
        # Convert UUID to string
        if data.get('id'):
            data['id'] = str(data['id'])
        
        # createDate is already formatted in get_createDate() method (without Z)
        
        # Ensure birthdate is in ISO format without Z (old Swagger shows: "2025-10-12T20:30:00")
        if data.get('birthdate'):
            if isinstance(data['birthdate'], str):
                # Remove Z if present (old Swagger format doesn't use Z)
                if data['birthdate'].endswith('Z'):
                    data['birthdate'] = data['birthdate'][:-1]
        
        # Ensure representativeDate is in ISO format with Z if it exists
        if data.get('representativeDate'):
            if isinstance(data['representativeDate'], str):
                if not data['representativeDate'].endswith('Z'):
                    data['representativeDate'] = data['representativeDate'] + 'Z'
        
        # Ensure blueUSerActiveDate is in ISO format with Z if it exists
        if data.get('blueUSerActiveDate'):
            if isinstance(data['blueUSerActiveDate'], str):
                if not data['blueUSerActiveDate'].endswith('Z'):
                    data['blueUSerActiveDate'] = data['blueUSerActiveDate'] + 'Z'
        
        # Keep None values as None (they'll be serialized as null in JSON)
        # Don't convert None to empty string - old Swagger shows null
        
        return data


class UserListResponseSerializer(serializers.Serializer):
    """Response serializer for user list matching old Swagger format."""
    messages = serializers.ListField(child=serializers.CharField(), default=list)
    succeeded = serializers.BooleanField(default=True)
    data = serializers.ListField(child=UserCompatibilitySerializer())


class UserDetailResponseSerializer(serializers.Serializer):
    """Response serializer for user detail matching old Swagger format."""
    messages = serializers.ListField(child=serializers.CharField(), default=list)
    succeeded = serializers.BooleanField(default=True)
    data = UserCompatibilitySerializer()


class UserUpdateRequestSerializer(serializers.ModelSerializer):
    """
    Request serializer for updating user profile.
    Accepts Flutter's camelCase format and converts to Django's snake_case.
    """
    userName = serializers.CharField(source='username', required=False, allow_blank=True)
    firstName = serializers.CharField(source='first_name', required=False, allow_blank=True)
    lastName = serializers.CharField(source='last_name', required=False, allow_blank=True)
    phoneNumber = serializers.CharField(source='phone_number', required=False, allow_blank=True)
    isActive = serializers.BooleanField(source='is_active', required=False)
    emailConfirmed = serializers.BooleanField(source='email_confirmed', required=False)
    imageUrl = serializers.CharField(source='image_url', required=False, allow_blank=True)
    companyName = serializers.CharField(source='company_name', required=False, allow_blank=True)
    vatNumber = serializers.CharField(source='vat_number', required=False, allow_blank=True)
    bankname = serializers.CharField(source='bank_name', required=False, allow_blank=True)
    birthdate = serializers.DateField(source='birth_date', required=False, allow_null=True)
    codeMeli = serializers.CharField(source='national_id', required=False, allow_blank=True)  # Flutter uses codeMeli
    representativeBy = serializers.CharField(source='representative_by', required=False, allow_blank=True)
    
    # Fields that match directly
    id = serializers.UUIDField(required=False, read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    representative = serializers.CharField(required=False, allow_blank=True)
    sheba = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'userName', 'firstName', 'lastName', 'email',
            'isActive', 'emailConfirmed', 'phoneNumber', 'imageUrl',
            'companyName', 'vatNumber', 'representative', 'sheba',
            'bankname', 'birthdate', 'codeMeli', 'representativeBy',
            'language', 'country', 'city'
        ]


class UserSearchRequestSerializer(serializers.Serializer):
    """Request serializer for user search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")


class UserSearchSPRequestSerializer(serializers.Serializer):
    """Request serializer for user search (stored procedure)."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")


class UserByRoleRequestSerializer(serializers.Serializer):
    """Request serializer for getting users by role."""
    role = serializers.CharField(required=False, allow_blank=True)
    isActive = serializers.BooleanField(required=False, allow_null=True)


class UserByRoleRequestRequestSerializer(serializers.Serializer):
    """Request serializer for getting users by role request."""
    roleRequest = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)


class UserRoleItemSerializer(serializers.Serializer):
    """Serializer for a single user role item."""
    roleId = serializers.CharField(required=True)
    roleName = serializers.CharField(required=True)
    enabled = serializers.BooleanField(required=True)


class UserRolesUpdateSerializer(serializers.Serializer):
    """Serializer for updating user roles. Matches old Swagger format."""
    userRoles = serializers.ListField(
        child=UserRoleItemSerializer(),
        required=True
    )


class RoleSerializer(serializers.Serializer):
    """Serializer for role information."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    codename = serializers.CharField()


class PermissionSerializer(serializers.Serializer):
    """Serializer for permission information."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    codename = serializers.CharField()
    contentType = serializers.CharField(source='content_type', required=False)

