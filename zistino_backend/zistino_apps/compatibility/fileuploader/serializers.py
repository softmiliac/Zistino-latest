"""
Serializers for FileUploader endpoints.
"""
from rest_framework import serializers


class FileUploaderSerializer(serializers.Serializer):
    """Serializer for FileUploader - placeholder structure."""
    id = serializers.IntegerField(read_only=True)
    fileName = serializers.CharField(read_only=True)
    fileUrl = serializers.CharField(read_only=True)
    fileSize = serializers.IntegerField(read_only=True, allow_null=True)
    mimeType = serializers.CharField(read_only=True, allow_null=True)
    token = serializers.CharField(read_only=True, allow_null=True)
    folder = serializers.CharField(read_only=True, allow_null=True)
    groupName = serializers.CharField(read_only=True, allow_null=True)
    userId = serializers.UUIDField(read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(read_only=True, allow_null=True)


class FileUploadRequestSerializer(serializers.Serializer):
    """Request serializer for file upload."""
    # File will be sent as multipart/form-data
    file = serializers.FileField(required=True)
    folder = serializers.CharField(required=False, allow_blank=True, default='')


class FileGroupNameRequestSerializer(serializers.Serializer):
    """Request serializer for grouping files by name."""
    groupName = serializers.CharField(required=True)
    fileIds = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="List of file IDs to group"
    )


class FileGenerateTokenRequestSerializer(serializers.Serializer):
    """Request serializer for generating file token."""
    # Token generation parameters (if any)
    expiresIn = serializers.IntegerField(required=False, default=3600, help_text="Token expiration in seconds")


class FileByTokenResponseSerializer(serializers.Serializer):
    """Response serializer for file by token."""
    id = serializers.IntegerField(read_only=True)
    fileName = serializers.CharField(read_only=True)
    fileUrl = serializers.CharField(read_only=True)
    fileSize = serializers.IntegerField(read_only=True, allow_null=True)
    mimeType = serializers.CharField(read_only=True, allow_null=True)

