"""
Serializers for RepairRequests endpoints.
"""
from rest_framework import serializers
from .models import RepairRequest, RepairRequestDetail, RepairRequestStatus, RepairRequestDocument
from zistino_apps.products.models import Product, Problem


class RepairRequestDetailCreateSerializer(serializers.Serializer):
    """Serializer for creating repair request detail matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Detail ID (0 for new, >0 for update)')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    startRepairDate = serializers.DateTimeField(required=False, allow_null=True)
    endRepairDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestId = serializers.IntegerField(required=False, default=0, help_text='Will be set automatically')
    problemId = serializers.IntegerField(required=False, allow_null=True, default=0)
    isCanceled = serializers.BooleanField(required=False, default=False)
    cancelationDescription = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RepairRequestStatusUpdateSerializer(serializers.Serializer):
    """Serializer for repair request status in update request matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Status ID (0 for new, >0 for update)')
    repairRequestId = serializers.IntegerField(required=False, default=0, help_text='Will be set automatically')
    text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.IntegerField(required=False, default=0)


class RepairRequestDocumentUpdateSerializer(serializers.Serializer):
    """Serializer for repair request document in update request matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Document ID (0 for new, >0 for update)')
    repairRequestId = serializers.IntegerField(required=False, default=0, help_text='Will be set automatically')
    fileUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RepairRequestCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating repair request matching old Swagger format."""
    duration = serializers.IntegerField(required=False, default=0)
    totalPrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    steps = serializers.IntegerField(required=False, default=0)
    deliveryInformation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID string)')
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    gender = serializers.IntegerField(required=False, default=0)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    userType = serializers.IntegerField(required=False, default=0)
    requestType = serializers.IntegerField(required=False, default=0)
    deliveryMode = serializers.IntegerField(required=False, default=0)
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestDetails = RepairRequestDetailCreateSerializer(many=True, required=False, allow_empty=True)


class RepairRequestUpdateRequestSerializer(serializers.Serializer):
    """Request serializer for updating repair request matching old Swagger format."""
    duration = serializers.IntegerField(required=False, default=0)
    totalPrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    steps = serializers.IntegerField(required=False, default=0)
    deliveryInformation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    createRequestDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Create request date')
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID string)')
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    gender = serializers.IntegerField(required=False, default=0)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    userType = serializers.IntegerField(required=False, default=0)
    requestType = serializers.IntegerField(required=False, default=0)
    deliveryMode = serializers.IntegerField(required=False, default=0)
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestDetails = RepairRequestDetailCreateSerializer(many=True, required=False, allow_empty=True)
    repairRequestStatuses = RepairRequestStatusUpdateSerializer(many=True, required=False, allow_empty=True)
    repairRequestDocuments = RepairRequestDocumentUpdateSerializer(many=True, required=False, allow_empty=True)


class RepairRequestSerializer(serializers.Serializer):
    """Serializer for RepairRequest (placeholder)."""
    id = serializers.CharField(read_only=True)
    userId = serializers.CharField(required=False)
    productId = serializers.CharField(required=False)
    problemId = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(read_only=True)


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search fields for repair request search."""
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


class RepairRequestSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching repair requests matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID string)')
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    requestType = serializers.IntegerField(required=False, allow_null=True, help_text='Request type filter')


class RepairRequestDetailClientSerializer(serializers.Serializer):
    """Serializer for repair request detail in client request (simplified format)."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    problemId = serializers.IntegerField(required=False, allow_null=True, default=0)


class RepairRequestClientSerializer(serializers.Serializer):
    """Request serializer for creating repair request (client) matching old Swagger format."""
    duration = serializers.IntegerField(required=False, default=0)
    totalPrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    steps = serializers.IntegerField(required=False, default=0)
    deliveryInformation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID string)')
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    gender = serializers.IntegerField(required=False, default=0)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    userType = serializers.IntegerField(required=False, default=0)
    requestType = serializers.IntegerField(required=False, default=0)
    deliveryMode = serializers.IntegerField(required=False, default=0)
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestDetails = RepairRequestDetailClientSerializer(many=True, required=False, allow_empty=True)


class RepairRequestDetailAnonymousClientSerializer(serializers.Serializer):
    """Serializer for repair request detail in anonymous client request (simplified format)."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    problemId = serializers.IntegerField(required=False, allow_null=True, default=0)


class RepairRequestAnonymousClientSerializer(serializers.Serializer):
    """Request serializer for creating repair request (anonymous client) matching old Swagger format."""
    duration = serializers.IntegerField(required=False, default=0)
    totalPrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.0)
    steps = serializers.IntegerField(required=False, default=0)
    deliveryInformation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    productId = serializers.CharField(required=True, help_text='Product ID (UUID string)')
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    fullName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    gender = serializers.IntegerField(required=False, default=0)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipCode = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    phoneNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    companyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    companyNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    vatNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    userType = serializers.IntegerField(required=False, default=0)
    requestType = serializers.IntegerField(required=False, default=0)
    deliveryMode = serializers.IntegerField(required=False, default=0)
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestDetails = RepairRequestDetailAnonymousClientSerializer(many=True, required=False, allow_empty=True)


class RepairRequestFollowupRequestSerializer(serializers.Serializer):
    """Request serializer for getting repair requests (followup) matching old Swagger format."""
    trackingCode = serializers.CharField(required=True, help_text='Tracking code of the repair request')
    email = serializers.EmailField(required=True, help_text='Email address associated with the repair request')


class RepairRequestMessageRequestSerializer(serializers.Serializer):
    """Request serializer for adding repair request message matching old Swagger format."""
    repairRequestId = serializers.IntegerField(required=True, help_text='Repair Request ID')
    message = serializers.CharField(required=True, help_text='Message content')
    type = serializers.IntegerField(required=False, default=0, help_text='Message type (0=User, 1=Admin, 2=System)')


# Response serializers for GET endpoints
class ProblemResponseSerializer(serializers.Serializer):
    """Serializer for Problem in response."""
    id = serializers.IntegerField()
    title = serializers.CharField()


class ProductResponseSerializer(serializers.Serializer):
    """Serializer for Product in response."""
    id = serializers.CharField()
    name = serializers.CharField()
    masterImage = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)


class RepairRequestDetailResponseSerializer(serializers.Serializer):
    """Serializer for RepairRequestDetail in response."""
    id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    startRepairDate = serializers.DateTimeField(required=False, allow_null=True)
    endRepairDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestId = serializers.IntegerField()
    problem = ProblemResponseSerializer(required=False, allow_null=True)
    isCanceled = serializers.BooleanField()
    cancelationDescription = serializers.CharField(required=False, allow_null=True)


class RepairRequestStatusResponseSerializer(serializers.Serializer):
    """Serializer for RepairRequestStatus in response."""
    id = serializers.IntegerField()
    text = serializers.CharField(required=False, allow_null=True)
    status = serializers.IntegerField()
    createdOn = serializers.DateTimeField()


class RepairRequestDocumentResponseSerializer(serializers.Serializer):
    """Serializer for RepairRequestDocument in response."""
    id = serializers.IntegerField()
    documentUrl = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)


class RepairRequestResponseSerializer(serializers.Serializer):
    """Serializer for RepairRequest detailed response matching old Swagger format."""
    id = serializers.IntegerField()
    duration = serializers.IntegerField()
    totalPrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    trackingCode = serializers.CharField(required=False, allow_null=True)
    steps = serializers.IntegerField()
    deliveryInformation = serializers.CharField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_null=True)
    createRequestDate = serializers.DateTimeField()
    userId = serializers.CharField(required=False, allow_null=True)
    product = ProductResponseSerializer(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    fullName = serializers.CharField(required=False, allow_null=True)
    gender = serializers.IntegerField()
    address = serializers.CharField(required=False, allow_null=True)
    zipCode = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    phoneNumber = serializers.CharField(required=False, allow_null=True)
    companyName = serializers.CharField(required=False, allow_null=True)
    companyNumber = serializers.CharField(required=False, allow_null=True)
    vatNumber = serializers.CharField(required=False, allow_null=True)
    userType = serializers.IntegerField()
    requestType = serializers.IntegerField()
    deliveryMode = serializers.IntegerField()
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    repairRequestDetails = RepairRequestDetailResponseSerializer(many=True, required=False)
    repairRequestStatuses = RepairRequestStatusResponseSerializer(many=True, required=False)
    repairRequestDocuments = RepairRequestDocumentResponseSerializer(many=True, required=False)
