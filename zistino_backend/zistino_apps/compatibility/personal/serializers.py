"""
Serializers for Personal endpoints.
These import from users app serializers and add compatibility request/response serializers.
"""
from zistino_apps.users.serializers import UserProfileSerializer, UserSerializer
from rest_framework import serializers


class ProfileDateByRepresentativeDateRequestSerializer(serializers.Serializer):
    """Request serializer for getting user representatives by date range."""
    startDate = serializers.DateTimeField(required=False)
    endDate = serializers.DateTimeField(required=False)
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)


class SetBlueBadgeRequestSerializer(serializers.Serializer):
    """Request serializer for setting blue badge (Admin)."""
    userId = serializers.CharField(required=True)
    blueBadge = serializers.BooleanField(required=True)


class RequestBlueBadgeRequestSerializer(serializers.Serializer):
    """Request serializer for requesting blue badge."""
    reason = serializers.CharField(required=False, allow_blank=True)


class RequestRoleRequestSerializer(serializers.Serializer):
    """Request serializer for requesting a role."""
    role = serializers.ChoiceField(
        choices=['driver', 'manager', 'admin'],
        required=True
    )
    reason = serializers.CharField(required=False, allow_blank=True)


class RepresentativeRequestSerializer(serializers.Serializer):
    """Request serializer for updating representative."""
    representative = serializers.CharField(required=False, allow_blank=True)
    representativeBy = serializers.CharField(required=False, allow_blank=True)


class ProfileAdminUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for admin to update user profile matching old Swagger format."""
    userid = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    userName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Username')
    firstName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='First name')
    lastName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Last name')
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Phone number')
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True, help_text='Email address')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image URL')
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company name')
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company number')
    middleName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Middle name')
    gender = serializers.IntegerField(required=False, allow_null=True, help_text='Gender (0=male, 1=female, etc.)')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Title')
    info = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Info')
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='VAT number')
    sheba = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Sheba number')
    bankname = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Bank name')
    birthdate = serializers.DateTimeField(required=False, allow_null=True, help_text='Birth date')
    codeMeli = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='National ID (Code Meli)')
    representativeBy = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Representative by')
    blueUser = serializers.BooleanField(required=False, allow_null=True, help_text='Blue user status')
    blueUSerActiveDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Blue user active date')
    issue = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Issue')
    rolesRequests = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Roles requests')
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Language')
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='City')
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Country')
    companyId = serializers.IntegerField(required=False, allow_null=True, help_text='Company ID')
    instagram = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Instagram')
    facebook = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Facebook')
    linkedIn = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='LinkedIn')
    twitter = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Twitter')
    gitHub = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='GitHub')
    skype = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Skype')
    telegram = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Telegram')
    whatsApp = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='WhatsApp')


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Request serializer for reset password by email."""
    email = serializers.EmailField(required=True)


class ChangePasswordRequestSerializer(serializers.Serializer):
    """Request serializer for changing password matching old Swagger format."""
    password = serializers.CharField(required=True, help_text='Current password')
    newPassword = serializers.CharField(required=True, min_length=8, help_text='New password')
    confirmNewPassword = serializers.CharField(required=True, min_length=8, help_text='Confirm new password')
    
    def validate(self, data):
        """Validate that new password and confirm password match."""
        if data['newPassword'] != data['confirmNewPassword']:
            raise serializers.ValidationError({'confirmNewPassword': ['New password and confirm password do not match.']})
        return data


class RepairRequestsRequestSerializer(serializers.Serializer):
    """Request serializer for getting repair requests."""
    trackingCode = serializers.CharField(required=False, allow_blank=True)
    status = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.IntegerField(required=False, allow_null=True)


class RepairRequestDocumentRequestSerializer(serializers.Serializer):
    """Request serializer for adding repair request document."""
    repairRequestId = serializers.IntegerField(required=True)
    fileUrl = serializers.CharField(required=True)


class RepairRequestMessageRequestSerializer(serializers.Serializer):
    """Request serializer for adding repair request message."""
    repairRequestId = serializers.IntegerField(required=True)
    message = serializers.CharField(required=True)
    type = serializers.IntegerField(required=True)

