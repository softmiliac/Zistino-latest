"""
Serializers for Tickets endpoints matching old Swagger format.
"""
from rest_framework import serializers
from .models import Ticket, TicketMessage, TicketMessageDocument


class TicketMessageDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ticket message document."""
    class Meta:
        model = TicketMessageDocument
        fields = ['fileUrl']
        read_only_fields = ['id']
    
    fileUrl = serializers.CharField(source='file_url', max_length=500)


class TicketMessageDocumentCreateSerializer(serializers.Serializer):
    """Request serializer for creating ticket message document."""
    fileUrl = serializers.CharField(required=True, max_length=500, help_text='File URL')


class TicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for ticket message matching old Swagger format."""
    ticketMessageDocuments = serializers.SerializerMethodField()
    responseMessageId = serializers.IntegerField(source='response_message_id', read_only=True, allow_null=True)
    
    class Meta:
        model = TicketMessage
        fields = ['id', 'message', 'type', 'status', 'responseMessageId', 'ticketMessageDocuments']
        read_only_fields = ['id']
    
    def get_ticketMessageDocuments(self, obj):
        """Get ticket message documents."""
        documents = obj.ticket_message_documents.all()
        return [{'fileUrl': doc.file_url} for doc in documents]


class TicketMessageCreateSerializer(serializers.Serializer):
    """Request serializer for creating ticket message matching old Swagger format."""
    message = serializers.CharField(required=True, help_text='Message content')
    type = serializers.IntegerField(required=False, default=0, help_text='Message type')
    status = serializers.IntegerField(required=False, default=0, help_text='Message status')
    responseMessageId = serializers.IntegerField(required=False, allow_null=True, default=None, help_text='Response to message ID')
    ticketMessageDocuments = TicketMessageDocumentCreateSerializer(many=True, required=False, allow_empty=True, help_text='Ticket message documents')


class TicketMessageRequestSerializer(serializers.Serializer):
    """Request serializer for POST /api/v1/tickets/message matching old Swagger format."""
    ticketId = serializers.IntegerField(required=True, help_text='Ticket ID')
    message = serializers.CharField(required=True, help_text='Message content')
    responseMessageId = serializers.IntegerField(required=False, allow_null=True, default=None, help_text='Response to message ID')
    status = serializers.IntegerField(required=False, default=0, help_text='Message status')
    type = serializers.IntegerField(required=False, default=0, help_text='Message type')
    ticketMessageDocuments = TicketMessageDocumentCreateSerializer(many=True, required=False, allow_empty=True, help_text='Ticket message documents')


class TicketMessageInCreateSerializer(serializers.Serializer):
    """Request serializer for ticket message in ticket creation."""
    message = serializers.CharField(required=True, help_text='Message content')
    type = serializers.IntegerField(required=False, default=0, help_text='Message type')
    status = serializers.IntegerField(required=False, default=0, help_text='Message status')
    responseMessageId = serializers.IntegerField(required=False, allow_null=True, default=None, help_text='Response to message ID')
    ticketMessageDocuments = TicketMessageDocumentCreateSerializer(many=True, required=False, allow_empty=True, help_text='Ticket message documents')


class TicketCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating ticket matching old Swagger format."""
    subject = serializers.CharField(required=True, max_length=255, help_text='Ticket subject')
    status = serializers.IntegerField(required=False, default=0, help_text='Ticket status')
    priority = serializers.IntegerField(required=False, default=0, help_text='Ticket priority')
    categoryId = serializers.IntegerField(required=False, allow_null=True, default=None, help_text='Category ID')
    itemID = serializers.IntegerField(required=False, allow_null=True, default=None, help_text='Item ID')
    itemType = serializers.IntegerField(required=False, default=0, help_text='Item type')
    ticketMessages = TicketMessageInCreateSerializer(many=True, required=False, allow_empty=True, help_text='Ticket messages')


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search serializer."""
    fields = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    groupBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Group by fields'
    )


class TicketSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching tickets matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 means 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 means default)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Filter by user ID (UUID)')
    categoryId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Filter by category ID')
    itemID = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Filter by item ID')
    itemType = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Filter by item type')


class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializer for ticket details matching old Swagger format."""
    ownerUserId = serializers.UUIDField(source='user_id', read_only=True)
    ownerUserFullName = serializers.SerializerMethodField()
    itemID = serializers.IntegerField(source='item_id', read_only=True, allow_null=True)
    itemType = serializers.IntegerField(source='item_type', read_only=True)
    isAdmin = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    createdOn = serializers.DateTimeField(source='created_at', read_only=True)
    ticketMessages = TicketMessageSerializer(source='ticket_messages', many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'status', 'priority', 'ownerUserId', 'itemID', 'itemType', 'ownerUserFullName', 'isAdmin', 'category', 'createdOn', 'ticketMessages']
        read_only_fields = ['id']
    
    def get_ownerUserFullName(self, obj):
        """Get owner user full name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return None
    
    def get_isAdmin(self, obj):
        """Check if user is admin."""
        if obj.user:
            return obj.user.is_staff or obj.user.is_superuser
        return False
    
    def get_category(self, obj):
        """Get category (placeholder - not in model)."""
        return None


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer for ticket list matching old Swagger format (simplified)."""
    ownerUserId = serializers.UUIDField(source='user_id', read_only=True)
    ownerUserFullName = serializers.SerializerMethodField()
    itemID = serializers.IntegerField(source='item_id', read_only=True, allow_null=True)
    itemType = serializers.IntegerField(source='item_type', read_only=True)
    isAdmin = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    createdOn = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'status', 'priority', 'ownerUserId', 'itemID', 'itemType', 'ownerUserFullName', 'isAdmin', 'category', 'createdOn']
        read_only_fields = ['id']
    
    def get_ownerUserFullName(self, obj):
        """Get owner user full name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return None
    
    def get_isAdmin(self, obj):
        """Check if user is admin."""
        if obj.user:
            return obj.user.is_staff or obj.user.is_superuser
        return False
    
    def get_category(self, obj):
        """Get category (placeholder - not in model)."""
        return None
