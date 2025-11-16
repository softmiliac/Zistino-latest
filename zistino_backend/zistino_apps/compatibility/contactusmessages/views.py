"""
Views for ContactUsMessages compatibility layer.
Provides all endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter, OpenApiTypes
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import ContactUsMessage
from .serializers import (
    ContactUsMessageResponseSerializer,
    ContactUsMessageCreateRequestSerializer,
    ContactUsMessageSearchRequestSerializer,
)
from zistino_apps.compatibility.utils import create_success_response, create_error_response

User = get_user_model()


@extend_schema(tags=['ContactUsMessages'])
class ContactUsMessagesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ContactUsMessages endpoints.
    """
    queryset = ContactUsMessage.objects.all()
    serializer_class = ContactUsMessageResponseSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access for contact form

    @extend_schema(
        tags=['ContactUsMessages'],
        operation_id='contactusmessages_create',
        summary='Create a new contact us message',
        request=ContactUsMessageCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Contact Us Message (default)',
                value={
                    "firstName": "string",
                    "lastName": "string",
                    "email": "string",
                    "message": "string",
                    "jsonExt": "string",
                    "type": 0,
                    "responseStatus": 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Contact us message created successfully',
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
    def create(self, request, *args, **kwargs):
        """Create a new contact us message matching old Swagger format."""
        try:
            serializer = ContactUsMessageCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Create contact us message
            message = ContactUsMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=validated_data['firstName'],
                last_name=validated_data['lastName'],
                email=validated_data['email'],
                message=validated_data['message'],
                json_ext=validated_data.get('jsonExt'),
                type=validated_data.get('type', 0),
                response_status=validated_data.get('responseStatus', 0)
            )
            
            return create_success_response(data=message.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating contact us message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['ContactUsMessages'],
        operation_id='contactusmessages_search',
        summary='Search contact us messages using available filters',
        request=ContactUsMessageSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search Request (default)',
                value={
                    "advancedSearch": {
                        "fields": [
                            "string"
                        ],
                        "keyword": "string",
                        "groupBy": [
                            "string"
                        ]
                    },
                    "keyword": "string",
                    "pageNumber": 0,
                    "pageSize": 0,
                    "orderBy": [
                        "string"
                    ],
                    "userId": "string",
                    "type": 0,
                    "responseStatus": 0
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results with pagination',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "messages": [
                                "string"
                            ],
                            "succeeded": True,
                            "data": [
                                {
                                    "id": 0,
                                    "firstName": "string",
                                    "lastName": "string",
                                    "email": "string",
                                    "message": "string",
                                    "jsonExt": "string",
                                    "type": 0,
                                    "responseStatus": 0
                                }
                            ],
                            "currentPage": 0,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 0,
                            "hasPreviousPage": True,
                            "hasNextPage": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search contact us messages with pagination and filters matching old Swagger format."""
        try:
            serializer = ContactUsMessageSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            if page_number == 0:
                page_number = 1
            page_size = validated_data.get('pageSize', 0)
            if page_size == 0:
                page_size = 20
            
            # Build query
            qs = ContactUsMessage.objects.all()
            
            # Filter by userId
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    qs = qs.filter(user=user)
                except User.DoesNotExist:
                    pass  # If user not found, return empty results
            
            # Filter by type
            if validated_data.get('type') is not None:
                qs = qs.filter(type=validated_data['type'])
            
            # Filter by responseStatus
            if validated_data.get('responseStatus') is not None:
                qs = qs.filter(response_status=validated_data['responseStatus'])
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '').strip()
            if keyword:
                qs = qs.filter(
                    Q(first_name__icontains=keyword) |
                    Q(last_name__icontains=keyword) |
                    Q(email__icontains=keyword) |
                    Q(message__icontains=keyword)
                )
            
            # Handle orderBy
            order_by = validated_data.get('orderBy', [])
            if order_by and isinstance(order_by, list):
                valid_order_by = []
                for field in order_by:
                    if field and isinstance(field, str):
                        # Map common fields
                        mapped_field = None
                        if field.lower() in ['created_at', 'createdat', 'createdon']:
                            mapped_field = 'created_at'
                        elif field.lower() in ['first_name', 'firstname']:
                            mapped_field = 'first_name'
                        elif field.lower() in ['last_name', 'lastname']:
                            mapped_field = 'last_name'
                        elif field.lower() in ['email']:
                            mapped_field = 'email'
                        elif field.lower() in ['type']:
                            mapped_field = 'type'
                        elif field.lower() in ['response_status', 'responsestatus']:
                            mapped_field = 'response_status'
                        
                        if mapped_field:
                            valid_order_by.append(mapped_field)
                
                if valid_order_by:
                    qs = qs.order_by(*valid_order_by)
                else:
                    qs = qs.order_by('-created_at')
            else:
                qs = qs.order_by('-created_at')
            
            # Calculate pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
            current_page = page_number
            has_previous_page = current_page > 1
            has_next_page = current_page < total_pages
            
            # Get paginated items
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end]
            
            # Serialize
            serializer = ContactUsMessageResponseSerializer(items, many=True)
            
            # Return in old Swagger format
            # messages should be ["string"] if there's data, otherwise []
            messages = ["string"] if len(serializer.data) > 0 else []
            return Response({
                "messages": messages,
                "succeeded": True,
                "data": serializer.data,
                "currentPage": current_page,
                "totalPages": total_pages,
                "totalCount": total_count,
                "pageSize": page_size,
                "hasPreviousPage": has_previous_page,
                "hasNextPage": has_next_page
            })
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching contact us messages: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['ContactUsMessages'],
        operation_id='contactusmessages_retrieve',
        summary='Retrieve a contact us message by ID',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Contact us message details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "userId": None,
                                "firstName": "nawab",
                                "lastName": "na",
                                "email": "asd@exam.com",
                                "message": "hi",
                                "jsonExt": "string",
                                "type": 0,
                                "responseStatus": 0
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a contact us message by ID matching old Swagger format."""
        try:
            message = self.get_object()
            serializer = ContactUsMessageResponseSerializer(message)
            return create_success_response(data=serializer.data, messages=[])
        except ContactUsMessage.DoesNotExist:
            pk = kwargs.get('pk', 'unknown')
            return create_error_response(
                error_message=f'Contact us message with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Contact us message with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['ContactUsMessages'],
        operation_id='contactusmessages_update',
        summary='Update a contact us message',
        request=ContactUsMessageCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Contact us message updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "userId": None,
                                "firstName": "nawab",
                                "lastName": "na",
                                "email": "asd@exam.com",
                                "message": "hi",
                                "jsonExt": "string",
                                "type": 0,
                                "responseStatus": 0
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a contact us message matching old Swagger format."""
        try:
            message = self.get_object()
            serializer = ContactUsMessageCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update message
            message.first_name = validated_data.get('firstName', message.first_name)
            message.last_name = validated_data.get('lastName', message.last_name)
            message.email = validated_data.get('email', message.email)
            message.message = validated_data.get('message', message.message)
            message.json_ext = validated_data.get('jsonExt', message.json_ext)
            message.type = validated_data.get('type', message.type)
            message.response_status = validated_data.get('responseStatus', message.response_status)
            message.save()
            
            # Return updated message
            response_serializer = ContactUsMessageResponseSerializer(message)
            return create_success_response(data=response_serializer.data, messages=[])
        except ContactUsMessage.DoesNotExist:
            pk = kwargs.get('pk', 'unknown')
            return create_error_response(
                error_message=f'Contact us message with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Contact us message with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating contact us message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['ContactUsMessages'],
        operation_id='contactusmessages_destroy',
        summary='Delete a contact us message',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Contact us message deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": None,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a contact us message matching old Swagger format."""
        try:
            message = self.get_object()
            message.delete()
            return create_success_response(data=None, messages=[])
        except ContactUsMessage.DoesNotExist:
            pk = kwargs.get('pk', 'unknown')
            return create_error_response(
                error_message=f'Contact us message with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Contact us message with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting contact us message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['ContactUsMessages'],
        operation_id='contactusmessages_dapper',
        summary='Get contact us message (dapper context)',
        description='Get contact us message in dapper context. Returns null if no id provided, or message data if id provided.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Contact us message ID (optional)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Dapper context response',
                examples=[
                    OpenApiExample(
                        'Success response (no id)',
                        value={
                            "data": None,
                            "messages": [],
                            "succeeded": True
                        }
                    ),
                    OpenApiExample(
                        'Success response (with id)',
                        value={
                            "data": {
                                "id": 1,
                                "userId": None,
                                "firstName": "nawab",
                                "lastName": "na",
                                "email": "asd@exam.com",
                                "message": "hi",
                                "jsonExt": "string",
                                "type": 0,
                                "responseStatus": 0
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get contact us message in dapper context matching old Swagger format."""
        try:
            message_id = request.query_params.get('id')
            
            if message_id:
                try:
                    message = ContactUsMessage.objects.get(id=int(message_id))
                    serializer = ContactUsMessageResponseSerializer(message)
                    return create_success_response(data=serializer.data, messages=[])
                except (ValueError, ContactUsMessage.DoesNotExist):
                    return create_success_response(data=None, messages=[])
            
            # If no id provided, return null as per old Swagger
            return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['ContactUsMessages'],
    operation_id='contactusmessages_client_create',
    summary='Create a contact us message from client',
    description='Create a contact us message from authenticated client.',
    request=ContactUsMessageCreateRequestSerializer,
    examples=[
        OpenApiExample(
            'Client Create Request (default)',
            value={
                "firstName": "string",
                "lastName": "string",
                "email": "string",
                "message": "string",
                "jsonExt": "string",
                "type": 0,
                "responseStatus": 0
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Contact us message created successfully',
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
class ContactUsMessagesClientCreateView(APIView):
    """POST /api/v1/contactusmessages/client"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a contact us message from authenticated client matching old Swagger format."""
        try:
            serializer = ContactUsMessageCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Create contact us message with authenticated user
            message = ContactUsMessage.objects.create(
                user=request.user,
                first_name=validated_data['firstName'],
                last_name=validated_data['lastName'],
                email=validated_data['email'],
                message=validated_data['message'],
                json_ext=validated_data.get('jsonExt'),
                type=validated_data.get('type', 0),
                response_status=validated_data.get('responseStatus', 0)
            )
            
            return create_success_response(data=message.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating contact us message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['ContactUsMessages'],
    operation_id='contactusmessages_anonymous_client_create',
    summary='Create a contact us message from anonymous client',
    description='Create a contact us message from anonymous (unauthenticated) client.',
    request=ContactUsMessageCreateRequestSerializer,
    examples=[
        OpenApiExample(
            'Anonymous Client Create Request (default)',
            value={
                "firstName": "string",
                "lastName": "string",
                "email": "string",
                "message": "string",
                "jsonExt": "string",
                "type": 0,
                "responseStatus": 0
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Contact us message created successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": 3,
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class ContactUsMessagesAnonymousClientCreateView(APIView):
    """POST /api/v1/contactusmessages/anonymous-client"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Create a contact us message from anonymous client matching old Swagger format."""
        try:
            serializer = ContactUsMessageCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Create contact us message without user (anonymous)
            message = ContactUsMessage.objects.create(
                user=None,
                first_name=validated_data['firstName'],
                last_name=validated_data['lastName'],
                email=validated_data['email'],
                message=validated_data['message'],
                json_ext=validated_data.get('jsonExt'),
                type=validated_data.get('type', 0),
                response_status=validated_data.get('responseStatus', 0)
            )
            
            return create_success_response(data=message.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating contact us message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
