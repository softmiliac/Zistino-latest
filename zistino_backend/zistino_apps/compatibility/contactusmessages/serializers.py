"""
Serializers for ContactUsMessages endpoints.
"""
from rest_framework import serializers
from .models import ContactUsMessage


class ContactUsMessageResponseSerializer(serializers.ModelSerializer):
    """Response serializer for ContactUsMessage matching old Swagger format."""
    userId = serializers.CharField(source='user.id', read_only=True, allow_null=True)
    firstName = serializers.CharField(source='first_name', read_only=True)
    lastName = serializers.CharField(source='last_name', read_only=True)
    jsonExt = serializers.CharField(source='json_ext', read_only=True, allow_null=True)
    type = serializers.IntegerField(read_only=True)
    responseStatus = serializers.IntegerField(source='response_status', read_only=True)
    
    class Meta:
        model = ContactUsMessage
        fields = ['id', 'userId', 'firstName', 'lastName', 'email', 'message', 'jsonExt', 'type', 'responseStatus']
        read_only_fields = ['id']


class ContactUsMessageCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating contact us message matching old Swagger format."""
    firstName = serializers.CharField(required=True, max_length=255, help_text='First name')
    lastName = serializers.CharField(required=True, max_length=255, help_text='Last name')
    email = serializers.EmailField(required=True, help_text='Email address')
    message = serializers.CharField(required=True, help_text='Message content')
    jsonExt = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='JSON extension field')
    type = serializers.IntegerField(required=False, default=0, help_text='Message type (0=General, 1=Support, 2=Complaint, 3=Suggestion, 4=Other)')
    responseStatus = serializers.IntegerField(required=False, default=0, help_text='Response status (0=Pending, 1=In Progress, 2=Resolved, 3=Closed)')


class ContactUsMessageSearchRequestSerializer(serializers.Serializer):
    """Request serializer for contact us message search matching old Swagger format."""
    advancedSearch = serializers.DictField(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Message type filter')
    responseStatus = serializers.IntegerField(required=False, allow_null=True, help_text='Response status filter')
