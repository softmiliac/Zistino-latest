"""
Views for Tickets compatibility layer.
Implements all endpoints matching old Swagger format.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from django.db.models import Q
import uuid

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from .models import Ticket, TicketMessage, TicketMessageDocument
from .serializers import (
    TicketCreateRequestSerializer,
    TicketSearchRequestSerializer,
    TicketMessageRequestSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketMessageSerializer,
)


@extend_schema(tags=['Tickets'])
class TicketsViewSet(viewsets.ViewSet):
    """
    ViewSet for Tickets endpoints.
    All endpoints will appear under "Tickets" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, Authenticated for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]  # list, retrieve, client, client_search, client_message

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_list',
        summary='Get all tickets',
        description='Returns all tickets matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='List of all tickets',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [
                                {
                                    "id": 1,
                                    "subject": "new tick",
                                    "status": 0,
                                    "priority": 1,
                                    "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                    "itemID": None,
                                    "itemType": 0,
                                    "ownerUserFullName": "مدیر آروین ویرا",
                                    "isAdmin": True,
                                    "category": None,
                                    "createdOn": "2025-11-10T12:41:25.9585748"
                                }
                            ],
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def list(self, request):
        """Get all tickets matching old Swagger format."""
        try:
            tickets = Ticket.objects.all().order_by('-created_at')
            serializer = TicketListSerializer(tickets, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_retrieve',
        summary='Get ticket by ID',
        description='Retrieves a ticket by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Ticket ID')
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Ticket details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "subject": "new tick",
                                "status": 0,
                                "priority": 1,
                                "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                "itemID": None,
                                "itemType": 0,
                                "ownerUserFullName": "مدیر آروین ویرا",
                                "isAdmin": True,
                                "category": None,
                                "createdOn": "2025-11-10T12:41:25.9585748",
                                "ticketMessages": []
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Ticket not found'}
        }
    )
    def retrieve(self, request, pk=None):
        """Get ticket by ID matching old Swagger format."""
        try:
            try:
                ticket = Ticket.objects.get(id=pk)
            except Ticket.DoesNotExist:
                return create_error_response(
                    error_message=f'Ticket with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Ticket with ID "{pk}" not found.']}
                )
            
            serializer = TicketDetailSerializer(ticket)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_update',
        summary='Update ticket',
        description='Updates a ticket by ID matching old Swagger format.',
        request=TicketCreateRequestSerializer,
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Ticket ID')
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Ticket updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "subject": "new tick",
                                "status": 0,
                                "priority": 1,
                                "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                "itemID": None,
                                "itemType": 0,
                                "ownerUserFullName": "مدیر آروین ویرا",
                                "isAdmin": True,
                                "category": None,
                                "createdOn": "2025-11-10T12:41:25.9585748",
                                "ticketMessages": []
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """Update ticket matching old Swagger format."""
        try:
            try:
                ticket = Ticket.objects.get(id=pk)
            except Ticket.DoesNotExist:
                return create_error_response(
                    error_message=f'Ticket with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Ticket with ID "{pk}" not found.']}
                )
            
            serializer = TicketCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update ticket
            ticket.subject = validated_data['subject']
            ticket.status = validated_data.get('status', ticket.status)
            ticket.priority = validated_data.get('priority', ticket.priority)
            
            # Handle categoryId (can be null)
            if 'categoryId' in validated_data:
                ticket.category_id = validated_data['categoryId']  # Can be None
            
            # Handle itemID (can be null)
            if 'itemID' in validated_data:
                ticket.item_id = validated_data['itemID']  # Can be None
            
            ticket.item_type = validated_data.get('itemType', ticket.item_type)
            ticket.save()
            
            # Update/create ticket messages if provided
            ticket_messages_data = validated_data.get('ticketMessages', [])
            if ticket_messages_data:
                # Delete existing messages (or keep them - based on requirements)
                # For now, we'll add new messages
                for msg_data in ticket_messages_data:
                    ticket_message = TicketMessage.objects.create(
                        ticket=ticket,
                        user=request.user,
                        message=msg_data['message'],
                        type=msg_data.get('type', 0),
                        status=msg_data.get('status', 0),
                        response_message_id=msg_data.get('responseMessageId')
                    )
                    
                    # Create ticket message documents if provided
                    documents_data = msg_data.get('ticketMessageDocuments', [])
                    for doc_data in documents_data:
                        TicketMessageDocument.objects.create(
                            ticket_message=ticket_message,
                            file_url=doc_data['fileUrl']
                        )
            
            # Return updated ticket
            detail_serializer = TicketDetailSerializer(ticket)
            return create_success_response(data=detail_serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating ticket: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_destroy',
        summary='Delete ticket',
        description='Deletes a ticket by ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Ticket ID')
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Ticket deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "subject": "new tick",
                                "status": 0,
                                "priority": 1,
                                "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                "itemID": None,
                                "itemType": 0,
                                "ownerUserFullName": "مدیر آروین ویرا",
                                "isAdmin": True,
                                "category": None,
                                "createdOn": "2025-11-10T12:41:25.9585748"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, pk=None):
        """Delete ticket matching old Swagger format."""
        try:
            try:
                ticket = Ticket.objects.get(id=pk)
            except Ticket.DoesNotExist:
                return create_error_response(
                    error_message=f'Ticket with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Ticket with ID "{pk}" not found.']}
                )
            
            # Serialize before deletion
            serializer = TicketListSerializer(ticket)
            ticket_data = serializer.data
            
            # Delete ticket (cascade will delete messages and documents)
            ticket.delete()
            
            return create_success_response(data=ticket_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting ticket: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_create',
        summary='Create a new ticket',
        description='Creates a new ticket matching old Swagger format.',
        request=TicketCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Ticket (default)',
                value={
                    "subject": "string",
                    "status": 0,
                    "priority": 0,
                    "categoryId": 0,
                    "itemID": 0,
                    "itemType": 0,
                    "ticketMessages": [
                        {
                            "message": "string",
                            "type": 0,
                            "status": 0,
                            "responseMessageId": 0,
                            "ticketMessageDocuments": [
                                {
                                    "fileUrl": "string"
                                }
                            ]
                        }
                    ]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Ticket created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request):
        """Create a new ticket matching old Swagger format."""
        try:
            serializer = TicketCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Create ticket
            category_id = validated_data.get('categoryId')
            item_id = validated_data.get('itemID')
            
            ticket = Ticket.objects.create(
                user=request.user,
                subject=validated_data['subject'],
                status=validated_data.get('status', 0),
                priority=validated_data.get('priority', 0),
                category_id=category_id,  # Can be None
                item_id=item_id,  # Can be None
                item_type=validated_data.get('itemType', 0)
            )
            
            # Create ticket messages if provided
            ticket_messages_data = validated_data.get('ticketMessages', [])
            for msg_data in ticket_messages_data:
                ticket_message = TicketMessage.objects.create(
                    ticket=ticket,
                    user=request.user,
                    message=msg_data['message'],
                    type=msg_data.get('type', 0),
                    status=msg_data.get('status', 0),
                    response_message_id=msg_data.get('responseMessageId')
                )
                
                # Create ticket message documents if provided
                documents_data = msg_data.get('ticketMessageDocuments', [])
                for doc_data in documents_data:
                    TicketMessageDocument.objects.create(
                        ticket_message=ticket_message,
                        file_url=doc_data['fileUrl']
                    )
            
            return create_success_response(
                data=ticket.id,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating ticket: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_search',
        summary='Search tickets',
        description='Search tickets with pagination and filters matching old Swagger format.',
        request=TicketSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": ["string"],
                        "keyword": "string",
                        "groupBy": ["string"]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": ["string"],
                    "userId": "string",
                    "categoryId": 0,
                    "itemID": 0,
                    "itemType": 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "data": [],
                                "currentPage": 1,
                                "totalPages": 0,
                                "totalCount": 0,
                                "pageSize": 1,
                                "hasPreviousPage": False,
                                "hasNextPage": False,
                                "messages": None,
                                "succeeded": True
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search tickets with pagination and filters matching old Swagger format."""
        try:
            serializer = TicketSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Handle pagination (0 means default)
            page_number = validated_data.get('pageNumber', 0)
            if page_number == 0:
                page_number = 1
            page_size = validated_data.get('pageSize', 0)
            if page_size == 0:
                page_size = 10  # Default page size
            
            # Build query
            qs = Ticket.objects.all()
            
            # Keyword search
            keyword = validated_data.get('keyword', '').strip()
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '').strip()
            
            if keyword:
                qs = qs.filter(
                    Q(subject__icontains=keyword)
                )
            
            # Filter by userId
            user_id = validated_data.get('userId')
            if user_id:
                try:
                    user_uuid = uuid.UUID(str(user_id))
                    qs = qs.filter(user_id=user_uuid)
                except (ValueError, TypeError):
                    pass  # Invalid UUID, skip filter
            
            # Filter by categoryId
            category_id = validated_data.get('categoryId')
            if category_id and category_id != 0:
                qs = qs.filter(category_id=category_id)
            
            # Filter by itemID
            item_id = validated_data.get('itemID')
            if item_id and item_id != 0:
                qs = qs.filter(item_id=item_id)
            
            # Filter by itemType
            item_type = validated_data.get('itemType')
            if item_type and item_type != 0:
                qs = qs.filter(item_type=item_type)
            
            # Ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out blank strings and validate fields
                valid_order_by = []
                for field in order_by:
                    if field and field.strip():
                        # Map field names
                        field_mapping = {
                            'subject': 'subject',
                            'status': 'status',
                            'priority': 'priority',
                            'createdAt': 'created_at',
                            'created_at': 'created_at',
                        }
                        mapped_field = field_mapping.get(field.strip(), None)
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-created_at')
            else:
                qs = qs.order_by('-created_at')
            
            # Pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
            
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]
            
            # Serialize results
            serializer = TicketDetailSerializer(items, many=True)
            
            # Nested response structure for search
            pagination_data = {
                "data": serializer.data,
                "currentPage": page_number,
                "totalPages": total_pages,
                "totalCount": total_count,
                "pageSize": page_size,
                "hasPreviousPage": page_number > 1,
                "hasNextPage": page_number < total_pages,
                "messages": None,
                "succeeded": True
            }
            
            return create_success_response(
                data=pagination_data,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching tickets: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_message',
        summary='Add message to ticket',
        description='Adds a message to a ticket matching old Swagger format.',
        request=TicketMessageRequestSerializer,
        examples=[
            OpenApiExample(
                'Add Message Request (default)',
                value={
                    "ticketId": 0,
                    "message": "string",
                    "responseMessageId": 0,
                    "status": 0,
                    "type": 0,
                    "ticketMessageDocuments": [
                        {
                            "fileUrl": "string"
                        }
                    ]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Message added successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 2,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='message')
    def message(self, request):
        """Add message to ticket matching old Swagger format."""
        try:
            serializer = TicketMessageRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get ticket
            try:
                ticket = Ticket.objects.get(id=validated_data['ticketId'])
            except Ticket.DoesNotExist:
                return create_error_response(
                    error_message=f'Ticket with ID "{validated_data["ticketId"]}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'ticketId': [f'Ticket with ID "{validated_data["ticketId"]}" not found.']}
                )
            
            # Create ticket message
            ticket_message = TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=validated_data['message'],
                type=validated_data.get('type', 0),
                status=validated_data.get('status', 0),
                response_message_id=validated_data.get('responseMessageId')
            )
            
            # Create ticket message documents if provided
            documents_data = validated_data.get('ticketMessageDocuments', [])
            for doc_data in documents_data:
                TicketMessageDocument.objects.create(
                    ticket_message=ticket_message,
                    file_url=doc_data['fileUrl']
                )
            
            return create_success_response(
                data=ticket_message.id,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while adding message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_client',
        summary='Get tickets (client)',
        description='Gets tickets for the authenticated user matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='List of user tickets',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [
                                {
                                    "id": 1,
                                    "subject": "new tick",
                                    "status": 0,
                                    "priority": 1,
                                    "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                    "itemID": None,
                                    "itemType": 0,
                                    "ownerUserFullName": "مدیر آروین ویرا",
                                    "isAdmin": True,
                                    "category": None,
                                    "createdOn": "2025-11-10T12:41:25.9585748"
                                }
                            ],
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_client_list',
        summary='Get tickets (client)',
        description='Gets tickets for the authenticated user matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='List of user tickets',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [
                                {
                                    "id": 1,
                                    "subject": "new tick",
                                    "status": 0,
                                    "priority": 1,
                                    "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                    "itemID": None,
                                    "itemType": 0,
                                    "ownerUserFullName": "مدیر آروین ویرا",
                                    "isAdmin": True,
                                    "category": None,
                                    "createdOn": "2025-11-10T12:41:25.9585748"
                                }
                            ],
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='client')
    def client(self, request):
        """Get tickets for client matching old Swagger format."""
        try:
            tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
            serializer = TicketListSerializer(tickets, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_client_search',
        summary='Search tickets (client)',
        description='Search tickets for client with pagination and filters matching old Swagger format.',
        request=TicketSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Client Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": ["string"],
                        "keyword": "string",
                        "groupBy": [""]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 1,
                    "orderBy": [""],
                    "userId": "string",
                    "categoryId": 0,
                    "itemID": 0,
                    "itemType": 0
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "data": [],
                                "currentPage": 1,
                                "totalPages": 0,
                                "totalCount": 0,
                                "pageSize": 1,
                                "hasPreviousPage": False,
                                "hasNextPage": False,
                                "messages": None,
                                "succeeded": True
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='client/search')
    def client_search(self, request):
        """Search tickets for client matching old Swagger format (same as search but filtered by user)."""
        try:
            serializer = TicketSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Handle pagination (0 means default)
            page_number = validated_data.get('pageNumber', 0)
            if page_number == 0:
                page_number = 1
            page_size = validated_data.get('pageSize', 0)
            if page_size == 0:
                page_size = 10  # Default page size
            
            # Build query - filter by current user
            qs = Ticket.objects.filter(user=request.user)
            
            # Keyword search
            keyword = validated_data.get('keyword', '').strip()
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword', '').strip()
            
            if keyword:
                qs = qs.filter(
                    Q(subject__icontains=keyword)
                )
            
            # Filter by categoryId
            category_id = validated_data.get('categoryId')
            if category_id and category_id != 0:
                qs = qs.filter(category_id=category_id)
            
            # Filter by itemID
            item_id = validated_data.get('itemID')
            if item_id and item_id != 0:
                qs = qs.filter(item_id=item_id)
            
            # Filter by itemType
            item_type = validated_data.get('itemType')
            if item_type and item_type != 0:
                qs = qs.filter(item_type=item_type)
            
            # Ordering
            order_by = validated_data.get('orderBy', [])
            if order_by:
                # Filter out blank strings and validate fields
                valid_order_by = []
                for field in order_by:
                    if field and field.strip():
                        # Map field names
                        field_mapping = {
                            'subject': 'subject',
                            'status': 'status',
                            'priority': 'priority',
                            'createdAt': 'created_at',
                            'created_at': 'created_at',
                        }
                        mapped_field = field_mapping.get(field.strip(), None)
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-created_at')
            else:
                qs = qs.order_by('-created_at')
            
            # Pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
            
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]
            
            # Serialize results
            serializer = TicketDetailSerializer(items, many=True)
            
            # Nested response structure for search
            pagination_data = {
                "data": serializer.data,
                "currentPage": page_number,
                "totalPages": total_pages,
                "totalCount": total_count,
                "pageSize": page_size,
                "hasPreviousPage": page_number > 1,
                "hasNextPage": page_number < total_pages,
                "messages": None,
                "succeeded": True
            }
            
            return create_success_response(
                data=pagination_data,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching tickets: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Tickets'],
        operation_id='tickets_client_message',
        summary='Add message to ticket (client)',
        description='Adds a message to a ticket for client matching old Swagger format.',
        request=TicketMessageRequestSerializer,
        examples=[
            OpenApiExample(
                'Client Add Message Request (default)',
                value={
                    "ticketId": 0,
                    "message": "string",
                    "responseMessageId": 0,
                    "status": 0,
                    "type": 0,
                    "ticketMessageDocuments": [
                        {
                            "fileUrl": "string"
                        }
                    ]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Message added successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 4,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='client/message')
    def client_message(self, request):
        """Add message to ticket for client matching old Swagger format."""
        try:
            serializer = TicketMessageRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get ticket - ensure it belongs to the user
            try:
                ticket = Ticket.objects.get(id=validated_data['ticketId'], user=request.user)
            except Ticket.DoesNotExist:
                return create_error_response(
                    error_message=f'Ticket with ID "{validated_data["ticketId"]}" not found or does not belong to you.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'ticketId': [f'Ticket with ID "{validated_data["ticketId"]}" not found or does not belong to you.']}
                )
            
            # Create ticket message
            ticket_message = TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=validated_data['message'],
                type=validated_data.get('type', 0),
                status=validated_data.get('status', 0),
                response_message_id=validated_data.get('responseMessageId')
            )
            
            # Create ticket message documents if provided
            documents_data = validated_data.get('ticketMessageDocuments', [])
            for doc_data in documents_data:
                TicketMessageDocument.objects.create(
                    ticket_message=ticket_message,
                    file_url=doc_data['fileUrl']
                )
            
            return create_success_response(
                data=ticket_message.id,
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while adding message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Tickets'],
    operation_id='tickets_dapper',
    summary='Get tickets (dapper)',
    description='Get tickets in dapper context. Accepts optional id parameter.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Optional ticket ID'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Tickets data',
            examples=[
                OpenApiExample(
                    'Success Response (no ID)',
                    value={
                        "data": None,
                        "messages": [],
                        "succeeded": True
                    }
                ),
                OpenApiExample(
                    'Success Response (with ID)',
                    value={
                        "data": {
                            "id": 1,
                            "subject": "new tick",
                            "status": 0,
                            "priority": 1,
                            "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                            "itemID": None,
                            "itemType": 0,
                            "ownerUserFullName": "مدیر آروین ویرا",
                            "isAdmin": True,
                            "category": None,
                            "createdOn": "2025-11-10T12:41:25.9585748",
                            "ticketMessages": []
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class TicketsDapperView(APIView):
    """GET /api/v1/tickets/dapper"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get tickets in dapper context matching old Swagger format."""
        try:
            ticket_id = request.query_params.get('id')
            
            if ticket_id:
                try:
                    ticket = Ticket.objects.get(id=ticket_id)
                    serializer = TicketDetailSerializer(ticket)
                    return create_success_response(data=serializer.data, messages=[])
                except Ticket.DoesNotExist:
                    return create_error_response(
                        error_message=f'Ticket with ID "{ticket_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Ticket with ID "{ticket_id}" not found.']}
                    )
            else:
                # No ID provided, return null
                return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView for client-specific ticket retrieval
@extend_schema(
    tags=['Tickets'],
    operation_id='tickets_client_retrieve',
    summary='Get ticket by ID (client)',
    description='Retrieves a ticket by ID only if it belongs to the authenticated user matching old Swagger format.',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, required=True, description='Ticket ID')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Ticket details',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": {
                            "id": 1,
                            "subject": "new tick",
                            "status": 0,
                            "priority": 1,
                            "ownerUserId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                            "itemID": None,
                            "itemType": 0,
                            "ownerUserFullName": "مدیر آروین ویرا",
                            "isAdmin": True,
                            "category": None,
                            "createdOn": "2025-11-10T12:41:25.9585748",
                            "ticketMessages": []
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        ),
        404: {'description': 'Ticket not found or does not belong to you'},
        403: {'description': 'Forbidden - ticket does not belong to you'}
    }
)
class TicketsClientRetrieveView(APIView):
    """GET /api/v1/tickets/client/{id} - Get ticket by ID for client (only own tickets)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get ticket by ID for client matching old Swagger format (only if belongs to user)."""
        try:
            try:
                ticket = Ticket.objects.get(id=id, user=request.user)
            except Ticket.DoesNotExist:
                return create_error_response(
                    error_message=f'Ticket with ID "{id}" not found or does not belong to you.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Ticket with ID "{id}" not found or does not belong to you.']}
                )
            
            serializer = TicketDetailSerializer(ticket)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
