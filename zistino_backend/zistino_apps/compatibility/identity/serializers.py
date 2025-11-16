"""
Serializers for Identity endpoints.
"""
from rest_framework import serializers


class RegisterRequestSerializer(serializers.Serializer):
    """Request serializer for registration matching old Swagger format."""
    firstName = serializers.CharField(required=True, help_text='First name')
    lastName = serializers.CharField(required=True, help_text='Last name')
    email = serializers.EmailField(required=True, help_text='Email address')
    userName = serializers.CharField(required=True, help_text='Username')
    password = serializers.CharField(required=True, min_length=6, write_only=True, help_text='Password')
    confirmPassword = serializers.CharField(required=True, min_length=6, write_only=True, help_text='Confirm password')
    middleName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Middle name')
    gender = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Gender (0=Not Specified, 1=Male, 2=Female)')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Title')
    info = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Additional info')
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Phone number')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Thumbnail URL')
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company name')
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company number')
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='VAT number')
    representative = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Representative')
    sheba = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Sheba number')
    bankname = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Bank name')
    birthdate = serializers.DateTimeField(required=False, allow_null=True, help_text='Birth date')
    codeMeli = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='National ID (code meli)')
    representativeBy = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Representative by')
    companyId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Company ID')
    
    def validate(self, attrs):
        """Validate that password and confirmPassword match."""
        password = attrs.get('password')
        confirm_password = attrs.get('confirmPassword')
        
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirmPassword': 'Passwords do not match.'
            })
        
        return attrs


class RegisterWithCodeRequestSerializer(serializers.Serializer):
    """Request serializer for registration with code matching old Swagger format."""
    firstName = serializers.CharField(required=True, help_text='First name')
    lastName = serializers.CharField(required=True, help_text='Last name')
    email = serializers.EmailField(required=True, help_text='Email address')
    userName = serializers.CharField(required=True, help_text='Username')
    password = serializers.CharField(required=True, min_length=6, write_only=True, help_text='Password')
    confirmPassword = serializers.CharField(required=True, min_length=6, write_only=True, help_text='Confirm password')
    middleName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Middle name')
    gender = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Gender (0=Not Specified, 1=Male, 2=Female)')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Title')
    info = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Additional info')
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Phone number')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Image URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Thumbnail URL')
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company name')
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Company number')
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='VAT number')
    representative = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Representative')
    sheba = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Sheba number')
    bankname = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Bank name')
    birthdate = serializers.DateTimeField(required=False, allow_null=True, help_text='Birth date')
    codeMeli = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='National ID (code meli)')
    representativeBy = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Representative by')
    companyId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Company ID')
    
    def validate(self, attrs):
        """Validate that password and confirmPassword match."""
        password = attrs.get('password')
        confirm_password = attrs.get('confirmPassword')
        
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirmPassword': 'Passwords do not match.'
            })
        
        return attrs


class AddressSerializer(serializers.Serializer):
    """Serializer for address in register-with-phonecall request."""
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    latitude = serializers.FloatField(required=False, default=0)
    longitude = serializers.FloatField(required=False, default=0)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    plate = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    unit = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    province = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class DeliverySerializer(serializers.Serializer):
    """Serializer for delivery in register-with-phonecall request."""
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    deliveryUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    setUserId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    addressId = serializers.IntegerField(required=False, default=0)
    orderId = serializers.IntegerField(required=False, default=0)
    examId = serializers.IntegerField(required=False, default=0)
    requestId = serializers.IntegerField(required=False, default=0)
    zoneId = serializers.IntegerField(required=False, default=0)
    preOrderId = serializers.IntegerField(required=False, default=0)
    status = serializers.IntegerField(required=False, default=0)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RegisterWithPhoneCallRequestSerializer(serializers.Serializer):
    """Request serializer for registration with phone call matching old Swagger format."""
    userInfo = RegisterRequestSerializer(required=True, help_text='User information')
    address = AddressSerializer(required=False, allow_null=True, help_text='Address information')
    delivery = DeliverySerializer(required=False, allow_null=True, help_text='Delivery information')


class VerifyTokenRequestSerializer(serializers.Serializer):
    """Request serializer for token verification."""
    token = serializers.CharField(required=True)


class VerifyPhoneNumberRequestSerializer(serializers.Serializer):
    """Request serializer for phone number verification."""
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)


class SendConfirmEmailRequestSerializer(serializers.Serializer):
    """Request serializer for sending confirmation email."""
    email = serializers.EmailField(required=True)


class ForgotPasswordRequestSerializer(serializers.Serializer):
    """Request serializer for forgot password matching old Swagger format."""
    email = serializers.EmailField(required=True, help_text='Email address')


class ForgotPasswordByCodeRequestSerializer(serializers.Serializer):
    """Request serializer for forgot password by code matching old Swagger format."""
    email = serializers.EmailField(required=True, help_text='Email address')


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Request serializer for reset password matching old Swagger format."""
    email = serializers.EmailField(required=True, help_text='Email address')
    password = serializers.CharField(required=True, min_length=6, write_only=True, help_text='New password')
    token = serializers.CharField(required=True, help_text='Reset token')


class CheckResetPasswordCodeRequestSerializer(serializers.Serializer):
    """Request serializer for checking reset password code matching old Swagger format."""
    email = serializers.EmailField(required=True, help_text='Email address')
    code = serializers.CharField(required=True, help_text='Verification code')


class ResetPasswordByCodeRequestSerializer(serializers.Serializer):
    """Request serializer for reset password by code matching old Swagger format."""
    email = serializers.EmailField(required=True, help_text='Email address')
    password = serializers.CharField(required=True, min_length=6, write_only=True, help_text='New password')
    code = serializers.CharField(required=True, help_text='Verification code')


class SendCodeRequestSerializer(serializers.Serializer):
    """Request serializer for sending code."""
    phone_number = serializers.CharField(required=True)


class ConfirmEmailCodeRegisteredRequestSerializer(serializers.Serializer):
    """Request serializer for confirming email code for registered user matching old Swagger format."""
    email = serializers.EmailField(required=True, help_text='Email address')
    password = serializers.CharField(required=True, min_length=6, write_only=True, help_text='Password')
    code = serializers.CharField(required=True, help_text='Verification code')

