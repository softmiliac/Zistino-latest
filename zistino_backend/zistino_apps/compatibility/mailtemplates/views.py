"""
Compatibility views for MailTemplates endpoints.
All endpoints will appear under "MailTemplates" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/MailTemplates
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager
import hashlib
import uuid
from django.http import Http404

from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .models import MailTemplate
from .serializers import (
    MailTemplateSerializer,
    MailTemplateCreateSerializer,
    MailTemplateSearchRequestSerializer,
    MailTemplateDetailSerializer
)


@extend_schema(tags=['MailTemplates'])
class MailTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mail templates.
    All endpoints will appear under "MailTemplates" folder in Swagger UI.
    """
    queryset = MailTemplate.objects.all()
    serializer_class = MailTemplateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_value_regex = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9]+'  # Accept UUID or integer

    def get_queryset(self):
        """Return all mail templates."""
        return MailTemplate.objects.all().order_by('name', 'locale')

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Use different serializer for create and retrieve."""
        if self.action == 'create':
            return MailTemplateCreateSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return MailTemplateDetailSerializer
        return MailTemplateSerializer
    
    def get_object_by_id(self, id_value):
        """Helper method to get object by ID (UUID or integer)."""
        # Try to parse as UUID first
        try:
            lookup_uuid = uuid.UUID(str(id_value))
            return MailTemplate.objects.get(pk=lookup_uuid)
        except (ValueError, TypeError):
            # If not UUID, try as integer (hash-based lookup)
            try:
                lookup_int = int(id_value)
                # Find mail template by converting UUIDs to integers and matching
                for template in MailTemplate.objects.all():
                    template_id_hash = int(hashlib.md5(str(template.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
                    if template_id_hash == lookup_int:
                        return template
                raise Http404('No MailTemplate matches the given query.')
            except (ValueError, TypeError):
                raise Http404('Invalid ID format.')
    
    def get_object(self):
        """Override to support both UUID and integer IDs."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        return self.get_object_by_id(lookup_value)
    
    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_create',
        summary='Create a new mail template',
        description='Create a new mail template matching old Swagger format.',
        request=MailTemplateCreateSerializer,
        examples=[
            OpenApiExample(
                'Create mail template',
                value={
                    'name': 'string',
                    'from': 'string',
                    'to': 'string',
                    'subject': 'string',
                    'body': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Mail template created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new mail template matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input using old Swagger format serializer
            serializer = MailTemplateCreateSerializer(data=request_data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            # Create mail template
            mail_template = serializer.save()
            
            # Convert UUID to integer for response (using hash for consistent mapping)
            mail_template_id_hash = int(hashlib.md5(str(mail_template.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            
            # Return response matching old Swagger format
            return create_success_response(data=mail_template_id_hash, messages=[], status_code=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_dapper',
        summary='Get mail templates (dapper context)',
        description='Get mail templates in dapper context matching old Swagger format. Accepts optional id parameter.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Mail template ID (UUID or integer). If provided, returns the specific template. If not provided, returns null.'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Dapper context',
                examples=[
                    OpenApiExample(
                        'No ID provided',
                        value={
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    ),
                    OpenApiExample(
                        'With ID provided',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'mail temp',
                                'from': 'a',
                                'to': 'b',
                                'subject': 'asdf',
                                'body': 'asdfg',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Mail template not found'}
        }
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get mail templates in dapper context matching old Swagger format."""
        # Check if id parameter is provided
        id_param = request.query_params.get('id', None)
        
        if id_param:
            # If id is provided, return the specific mail template
            try:
                instance = self.get_object_by_id(id_param)
                serializer = MailTemplateDetailSerializer(instance, include_body=True)
                
                # Convert UUID to integer for response
                template_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
                data = serializer.data
                data['id'] = template_id_hash
                
                return create_success_response(data=data, messages=[])
            except Exception as e:
                error_detail = str(e)
                error_type = type(e).__name__
                
                if 'No MailTemplate matches' in error_detail or 'Http404' in error_type:
                    return create_error_response(
                        error_message=f'Mail template with ID "{id_param}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Mail template with ID "{id_param}" not found.']}
                    )
                
                return create_error_response(
                    error_message=f'An error occurred while processing the request: {error_detail}',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    errors={'error': [f'{error_type}: {error_detail}']}
                )
        else:
            # If no id is provided, return null (matching old Swagger)
            return create_success_response(data=None, messages=[])

    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_search',
        summary='Search MailTemplates using available Filters',
        description='Search MailTemplates using available Filters matching old Swagger format.',
        request=MailTemplateSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search mail templates',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'string',
                        'groupBy': ['string']
                    },
                    'keyword': 'string',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string']
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Paginated search results',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [],
                            'currentPage': 1,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 1,
                            'hasPreviousPage': False,
                            'hasNextPage': False,
                            'messages': None,
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search mail templates with pagination matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = MailTemplateSearchRequestSerializer(data=request_data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters (can be 0)
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Get keyword from request or advancedSearch
            keyword = validated_data.get('keyword') or ''
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword') or keyword
            
            # Build query
            qs = MailTemplate.objects.all()
            
            # Apply keyword search
            if keyword:
                qs = qs.filter(
                    Q(name__icontains=keyword) |
                    Q(subject__icontains=keyword) |
                    Q(body__icontains=keyword) |
                    Q(template_type__icontains=keyword) |
                    Q(locale__icontains=keyword)
                )
            
            # Apply orderBy if provided
            order_by = validated_data.get('orderBy', [])
            valid_order_fields = ['name', 'subject', 'body', 'template_type', 'locale', 'created_at', 'updated_at']
            if order_by:
                # Filter valid fields and add '-' prefix for descending if needed
                order_fields = []
                for field in order_by:
                    if field and field.strip():
                        field_clean = field.strip().lstrip('-')
                        if field_clean in valid_order_fields:
                            if field.startswith('-'):
                                order_fields.append(f'-{field_clean}')
                            else:
                                order_fields.append(field_clean)
                if order_fields:
                    qs = qs.order_by(*order_fields)
                else:
                    qs = qs.order_by('name', 'locale')
            else:
                qs = qs.order_by('name', 'locale')
            
            # Get total count
            total_count = qs.count()
            items_data = []
            
            # Calculate pagination
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
                # Handle pageNumber 0 - treat as page 1
                effective_page = page_number if page_number > 0 else 1
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
                
                # Apply pagination
                start = (effective_page - 1) * page_size
                end = start + page_size
                items = qs[start:end]
                serializer = self.get_serializer(items, many=True)
                items_data = serializer.data
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                has_previous = False
                has_next = False
                serializer = self.get_serializer(qs, many=True)
                items_data = serializer.data
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 1 if empty, as per old Swagger example)
            response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 1)
            
            response_data = {
                'data': items_data,
                'currentPage': effective_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': response_page_size,
                'hasPreviousPage': has_previous,
                'hasNextPage': has_next,
                'messages': None,  # Old Swagger shows null, not empty array
                'succeeded': True
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_all',
        summary='Get all mail templates',
        description='Retrieves all mail templates matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of mail templates',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [{
                                'id': 1,
                                'name': 'mail temp',
                                'from': 'a',
                                'to': 'b',
                                'subject': 'asdf',
                                'locale': 'string'
                            }],
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        """Get all mail templates matching old Swagger format (without body field)."""
        templates = MailTemplate.objects.filter(is_active=True).order_by('name', 'locale')
        serializer = MailTemplateDetailSerializer(templates, many=True, include_body=False)
        
        # Convert UUIDs to integers for response
        data = []
        for template, serialized_data in zip(templates, serializer.data):
            template_id_hash = int(hashlib.md5(str(template.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            serialized_data['id'] = template_id_hash
            data.append(serialized_data)
        
        return create_success_response(data=data, messages=[])
    
    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_retrieve',
        summary='Retrieve a mail template by ID',
        description='Retrieve a mail template by its ID matching old Swagger format. Accepts both UUID and integer IDs.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Mail template ID (UUID or integer)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Mail template details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'mail temp',
                                'from': 'a',
                                'to': 'b',
                                'subject': 'asdf',
                                'body': 'asdfg',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Mail template not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a mail template by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = MailTemplateDetailSerializer(instance)
            
            # Convert UUID to integer for response
            template_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            data = serializer.data
            data['id'] = template_id_hash
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No MailTemplate matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Mail template with ID "{self.kwargs.get(self.lookup_field)}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Mail template with ID "{self.kwargs.get(self.lookup_field)}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_update',
        summary='Update a mail template by ID',
        description='Update a mail template by its ID matching old Swagger format. Accepts both UUID and integer IDs.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Mail template ID (UUID or integer)'
            )
        ],
        request=MailTemplateCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Mail template updated',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'mail temp',
                                'from': 'a',
                                'to': 'b',
                                'subject': 'asdf',
                                'body': 'asdfg',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Mail template not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a mail template by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input
            serializer = MailTemplateCreateSerializer(data=request.data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = serializer.validated_data
            
            # Update instance
            instance.name = validated_data['name']
            instance.subject = validated_data['subject']
            instance.body = validated_data['body']
            instance.template_type = validated_data.get('name', '')  # Use name as template_type
            instance.locale = validated_data['locale']
            instance.save()
            
            # Return updated data
            response_serializer = MailTemplateDetailSerializer(instance)
            template_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            data = response_serializer.data
            data['id'] = template_id_hash
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No MailTemplate matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Mail template with ID "{self.kwargs.get(self.lookup_field)}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Mail template with ID "{self.kwargs.get(self.lookup_field)}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )
    
    @extend_schema(
        tags=['MailTemplates'],
        operation_id='mailtemplates_destroy',
        summary='Delete a mail template by ID',
        description='Delete a mail template by its ID matching old Swagger format. Accepts both UUID and integer IDs.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Mail template ID (UUID or integer)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Mail template deleted',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 1,
                                'name': 'mail temp',
                                'from': 'a',
                                'to': 'b',
                                'subject': 'asdf',
                                'body': 'asdfg',
                                'locale': 'string'
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'Mail template not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a mail template by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Get data before deletion
            response_serializer = MailTemplateDetailSerializer(instance)
            template_id_hash = int(hashlib.md5(str(instance.id).encode()).hexdigest()[:8], 16) % (10 ** 9)
            data = response_serializer.data
            data['id'] = template_id_hash
            
            # Delete instance
            instance.delete()
            
            return create_success_response(data=data, messages=[])
        except Exception as e:
            error_detail = str(e)
            error_type = type(e).__name__
            
            if 'No MailTemplate matches' in error_detail or 'Http404' in error_type:
                return create_error_response(
                    error_message=f'Mail template with ID "{self.kwargs.get(self.lookup_field)}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Mail template with ID "{self.kwargs.get(self.lookup_field)}" not found.']}
                )
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

