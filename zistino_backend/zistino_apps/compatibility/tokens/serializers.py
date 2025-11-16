"""
Serializers for Tokens endpoints.
Matches old Swagger format exactly.
"""
from rest_framework import serializers


class CredentialsSerializer(serializers.Serializer):
    """
    Serializer for submitting credentials to get a token.
    Matches old Swagger: { "email": "...", "password": "..." }
    Note: tenant is passed as header, not in body.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenByEmailSerializer(serializers.Serializer):
    """Serializer for submitting email credentials to get a token."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ExternalLoginSerializer(serializers.Serializer):
    """Serializer for external login credentials."""
    provider = serializers.CharField(required=True)  # e.g., 'google', 'facebook', 'apple'
    externalToken = serializers.CharField(required=True, write_only=True)


class TokenWithPermissionsSerializer(serializers.Serializer):
    """Serializer for submitting credentials to get a token with permissions."""
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenByCodeSerializer(serializers.Serializer):
    """
    Serializer for submitting a code to get a token.
    Matches old Swagger format: { "phonenumber": "...", "code": "...", "token": "..." }
    """
    phonenumber = serializers.CharField(required=True)  # Matches old Swagger field name
    code = serializers.CharField(required=True)
    token = serializers.CharField(required=False, allow_blank=True)  # Optional, may be used for existing token validation


class TokenByCodeConfirmationSerializer(serializers.Serializer):
    """
    Serializer for confirming a code to get a token.
    Matches token-by-code format: { "phonenumber": "...", "code": "...", "token": "..." }
    """
    phonenumber = serializers.CharField(required=True)  # Match token-by-code format
    code = serializers.CharField(required=True)
    token = serializers.CharField(required=False, allow_blank=True)  # Optional, same as token-by-code


class RefreshTokenRequestSerializer(serializers.Serializer):
    """
    Serializer for refreshing an access token.
    Matches old Swagger format: { "token": "...", "refreshToken": "..." }
    """
    token = serializers.CharField(required=True, write_only=True)  # Current access token
    refreshToken = serializers.CharField(required=True, write_only=True)  # Refresh token


class TokenDataSerializer(serializers.Serializer):
    """Serializer for token data inside response wrapper."""
    token = serializers.CharField()
    refreshToken = serializers.CharField()
    refreshTokenExpiryTime = serializers.DateTimeField()


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response matching old Swagger format.
    {
        "data": {
            "token": "...",
            "refreshToken": "...",
            "refreshTokenExpiryTime": "..."
        },
        "messages": [],
        "succeeded": true
    }
    """
    data = TokenDataSerializer()
    messages = serializers.ListField(child=serializers.CharField(), default=list)
    succeeded = serializers.BooleanField(default=True)

