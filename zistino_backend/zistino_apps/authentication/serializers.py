from rest_framework import serializers
from .models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ['id', 'phone_number', 'code', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at', 'expires_at']


class SendCodeRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerifyCodeRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)


class LoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)


class RegisterRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    referral_code = serializers.CharField(required=False, allow_blank=True, max_length=20, help_text='Optional referral code')


class ForgotPasswordRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class ResetPasswordRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)