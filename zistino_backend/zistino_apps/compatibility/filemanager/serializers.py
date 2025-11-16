"""
Serializers for FileManager endpoints.
"""
from rest_framework import serializers


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for file search."""
    fields = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    groupBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Group by fields'
    )


class ImageDataSerializer(serializers.Serializer):
    """Serializer for image data in upload request."""
    name = serializers.CharField(required=True, help_text='File name')
    extension = serializers.CharField(required=True, help_text='File extension')
    data = serializers.CharField(required=True, help_text='Base64 encoded file data')


class FileUploadRequestSerializer(serializers.Serializer):
    """Request serializer for file upload matching old Swagger format."""
    image = ImageDataSerializer(required=True, help_text='Image data object')


class FileSearchRequestSerializer(serializers.Serializer):
    """Request serializer for file search matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 = page 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 = all results)')
    orderBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )
    fromDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Filter from date')
    toDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Filter to date')
    folder = serializers.CharField(required=False, allow_blank=True, default='', help_text='Filter by folder')


class FileSerializer(serializers.Serializer):
    """Serializer for File - placeholder structure."""
    id = serializers.IntegerField(read_only=True)
    fileName = serializers.CharField(read_only=True)
    fileUrl = serializers.CharField(read_only=True)
    fileSize = serializers.IntegerField(read_only=True, allow_null=True)
    mimeType = serializers.CharField(read_only=True, allow_null=True)
    userId = serializers.UUIDField(read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(read_only=True, allow_null=True)


class DomainEventSerializer(serializers.Serializer):
    """Serializer for domain events in file response."""
    triggeredOn = serializers.DateTimeField(read_only=True)


class FileDetailSerializer(serializers.Serializer):
    """Serializer for detailed file information matching old Swagger format."""
    domainEvents = serializers.ListField(
        child=DomainEventSerializer(),
        required=False,
        default=list,
        help_text='Domain events'
    )
    id = serializers.IntegerField(read_only=True)
    createdBy = serializers.CharField(read_only=True, allow_null=True)
    userId = serializers.CharField(read_only=True, allow_null=True)
    createDate = serializers.DateTimeField(read_only=True, allow_null=True)
    fileName = serializers.CharField(read_only=True, allow_null=True)
    fileExtention = serializers.CharField(read_only=True, allow_null=True)
    fileInternalName = serializers.CharField(read_only=True, allow_null=True)
    originalPath = serializers.CharField(read_only=True, allow_null=True)
    originalSize = serializers.IntegerField(read_only=True, allow_null=True)
    webPPath = serializers.CharField(read_only=True, allow_null=True)
    thumbnailPath = serializers.CharField(read_only=True, allow_null=True)
    groupName = serializers.CharField(read_only=True, allow_null=True)


class FileDownloadRequestSerializer(serializers.Serializer):
    """Request serializer for file download by ID."""
    id = serializers.IntegerField(required=True)

