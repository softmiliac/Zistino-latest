"""
Compatibility views for Faqs endpoints.
All endpoints will appear under "Faqs" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/Faqs
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from zistino_apps.products.models import FAQ
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    FaqSerializer,
    FaqSearchRequestSerializer,
    FaqClientSearchRequestSerializer,
    FaqClientSearchExRequestSerializer,
    FaqCreateRequestSerializer
)


@extend_schema(tags=['Faqs'])
class FaqViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing FAQs.
    All endpoints will appear under "Faqs" folder in Swagger UI.
    """
    queryset = FAQ.objects.all()
    serializer_class = FaqSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all FAQs."""
        return FAQ.objects.all().order_by('-created_at')

    def get_permissions(self):
        """Admin-only for create/update/delete/search, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['Faqs'],
        operation_id='faqs_create',
        summary='Create a new FAQ',
        description='Creates a new FAQ matching old Swagger format.',
        request=FaqCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create FAQ',
                value={
                    'categoryId': 0,
                    'title': 'string',
                    'description': 'string',
                    'locale': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='FAQ created successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 8,
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
        """Create FAQ matching old Swagger format. Returns FAQ ID."""
        try:
            # Validate input using old Swagger format serializer
            input_serializer = FaqCreateRequestSerializer(data=request.data)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = input_serializer.validated_data
            
            try:
                # Create FAQ
                faq = FAQ.objects.create(
                    question=validated_data.get('title'),
                    answer=validated_data.get('description', ''),
                    is_active=True
                )
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'faq': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while creating the FAQ: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return just the FAQ ID wrapped in standard response
            return create_success_response(data=faq.id)  # 200 OK to match old Swagger
        
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
        tags=['Faqs'],
        operation_id='faqs_dapper',
        summary='Get FAQs (dapper context)',
        description='Get FAQs in dapper context. Accepts optional id parameter.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Optional FAQ ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='FAQ data or null',
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
                        'ID provided',
                        value={
                            'data': {
                                'id': 1,
                                'title': 'string',
                                'description': 'string',
                                'categoryId': 0,
                                'categoryName': ''
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='dapper')
    def dapper(self, request):
        """Get FAQs in dapper context. Returns null if no id, or FAQ data if id provided."""
        faq_id = request.query_params.get('id')
        
        if faq_id:
            try:
                faq = FAQ.objects.get(id=int(faq_id))
                serializer = self.get_serializer(faq)
                return create_success_response(data=serializer.data)
            except (FAQ.DoesNotExist, ValueError):
                return create_success_response(data=None)
        
        return create_success_response(data=None)

    @extend_schema(
        tags=['Faqs'],
        operation_id='faqs_search',
        summary='Search Faq using available Filters',
        description='Search Faq using available Filters matching old Swagger format.',
        request=FaqSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search FAQs',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'string',
                        'groupBy': ['string']
                    },
                    'keyword': 'string',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string'],
                    'categoryId': 0
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
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search FAQs with pagination matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = FaqSearchRequestSerializer(data=request_data)
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
            qs = FAQ.objects.all().order_by('-created_at')

            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(question__icontains=keyword.strip()) |
                    Q(answer__icontains=keyword.strip())
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by and any(order_by):  # If orderBy has non-empty values
                # Validate fields exist in FAQ model
                valid_fields = ['id', 'question', 'answer', 'is_active', 'created_at']
                order_fields = []
                invalid_fields = []
                
                for field in order_by:
                    if field and field.strip():
                        # Remove leading minus for validation
                        field_name = field.strip().lstrip('-')
                        # Map old Swagger field names to Django field names
                        field_mapping = {
                            'title': 'question',
                            'description': 'answer',
                            'createdAt': 'created_at',
                        }
                        django_field = field_mapping.get(field_name, field_name)
                        if django_field in valid_fields:
                            # Add minus back if it was there
                            if field.strip().startswith('-'):
                                order_fields.append(f'-{django_field}')
                            else:
                                order_fields.append(django_field)
                        else:
                            invalid_fields.append(field.strip())
                
                if invalid_fields:
                    return create_error_response(
                        error_message=f'Invalid orderBy fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'orderBy': [f'Invalid fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}']}
                    )
                
                if order_fields:
                    try:
                        qs = qs.order_by(*order_fields)
                    except Exception:
                        # If ordering fails, use default
                        qs = qs.order_by('-created_at')
                else:
                    qs = qs.order_by('-created_at')
            else:
                # Default ordering
                qs = qs.order_by('-created_at')
            
            # Get total count
            total_count = qs.count()
            
            # Calculate pagination
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
                # Handle pageNumber 0 - treat as page 1
                effective_page = page_number if page_number > 0 else 1
                start = (effective_page - 1) * page_size
                end = start + page_size
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                start = 0
                end = None
                has_previous = False
                has_next = False
            
            # Get paginated results
            if end is not None:
                items = qs[start:end]
            else:
                items = qs[start:]
            
            # Serialize results
            item_serializer = FaqSerializer(items, many=True, context={'request': request})
            items_data = item_serializer.data
            
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
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            error_detail = str(e)
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            
            # Log the full error for debugging
            logger.error(f'FAQ search error: {error_type}: {error_detail}\n{error_traceback}')
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['Faqs'],
        operation_id='faqs_retrieve',
        summary='Retrieve a FAQ by ID',
        description='Retrieves a FAQ by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='FAQ ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='FAQ details',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 0,
                                'title': 'string',
                                'description': 'string',
                                'categoryId': 0,
                                'categoryName': ''
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'FAQ not found'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a FAQ by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return create_success_response(data=serializer.data)
        except FAQ.DoesNotExist:
            return create_error_response(
                error_message=f'FAQ with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'FAQ with ID "{kwargs.get("pk")}" not found.']}
            )

    @extend_schema(
        tags=['Faqs'],
        operation_id='faqs_update',
        summary='Update a FAQ by ID',
        description='Updates an existing FAQ by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='FAQ ID'
            )
        ],
        request=FaqCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='FAQ updated successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': {
                                'id': 0,
                                'title': 'string',
                                'description': 'string',
                                'categoryId': 0,
                                'categoryName': ''
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'FAQ not found'}
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a FAQ by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            
            # Validate input using old Swagger format serializer
            input_serializer = FaqCreateRequestSerializer(data=request.data)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = input_serializer.validated_data
            
            # Update FAQ fields
            if 'title' in validated_data:
                instance.question = validated_data.get('title')
            if 'description' in validated_data:
                instance.answer = validated_data.get('description', '')
            
            try:
                instance.save()
            except Exception as e:
                # Handle database integrity errors
                from django.db import IntegrityError
                error_detail = str(e)
                
                if isinstance(e, IntegrityError):
                    return create_error_response(
                        error_message='Database constraint violation. Please check your input.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'faq': ['Database constraint violation. Please check your input.']}
                    )
                else:
                    return create_error_response(
                        error_message=f'An error occurred while updating the FAQ: {error_detail}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errors={'error': [f'{type(e).__name__}: {error_detail}']}
                    )
            
            # Return updated FAQ in old Swagger format
            serializer = self.get_serializer(instance)
            return create_success_response(data=serializer.data)
        
        except FAQ.DoesNotExist:
            return create_error_response(
                error_message=f'FAQ with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'FAQ with ID "{kwargs.get("pk")}" not found.']}
            )
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
        tags=['Faqs'],
        operation_id='faqs_destroy',
        summary='Delete a FAQ by ID',
        description='Deletes a FAQ by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='FAQ ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='FAQ deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 0,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'FAQ not found'}
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a FAQ by ID matching old Swagger format. Returns FAQ ID."""
        try:
            instance = self.get_object()
            faq_id = instance.id
            instance.delete()  # Hard delete
            return create_success_response(data=faq_id)
        except FAQ.DoesNotExist:
            return create_error_response(
                error_message=f'FAQ with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'FAQ with ID "{kwargs.get("pk")}" not found.']}
            )
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
    tags=['Faqs'],
    operation_id='faqs_by_categoryid',
    summary='Get FAQs by category ID',
    description='Get FAQs that belong to a specific category matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Category ID'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of FAQs',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [],
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class FaqsByCategoryIdView(APIView):
    """GET /api/v1/faqs/by-categoryid/{id} - Get FAQs by category ID"""
    permission_classes = [AllowAny]

    def get(self, request, id):
        """Get FAQs by category ID matching old Swagger format."""
        # TODO: When FAQ model has category field, filter by it
        # For now, return all active FAQs
        faqs = FAQ.objects.filter(is_active=True).order_by('-created_at')
        serializer = FaqSerializer(faqs, many=True, context={'request': request})
        return create_success_response(data=serializer.data)


@extend_schema(
    tags=['Faqs'],
    operation_id='faqs_client_searchex',
    summary='Client extended search for FAQs',
    description='Extended search for FAQs (client endpoint) matching old Swagger format.',
    request=FaqClientSearchExRequestSerializer,
    examples=[
        OpenApiExample(
            'Client extended search',
            value={
                'advancedSearch': {
                    'fields': ['string'],
                    'keyword': 'string',
                    'groupBy': ['string']
                },
                'keyword': 'string',
                'pageNumber': 0,
                'pageSize': 0,
                'orderBy': ['string'],
                'categoryId': 0
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
        )
    }
)
class FaqsClientSearchExView(APIView):
    """POST /api/v1/faqs/client/searchex - Client extended search"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Extended search for FAQs matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = FaqClientSearchExRequestSerializer(data=request_data)
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
            
            # Build query (only active FAQs for client)
            qs = FAQ.objects.filter(is_active=True).order_by('-created_at')

            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(question__icontains=keyword.strip()) |
                    Q(answer__icontains=keyword.strip())
                )
            
            # Apply ordering
            order_by = validated_data.get('orderBy', [])
            if order_by and any(order_by):  # If orderBy has non-empty values
                # Validate fields exist in FAQ model
                valid_fields = ['id', 'question', 'answer', 'is_active', 'created_at']
                order_fields = []
                invalid_fields = []
                
                for field in order_by:
                    if field and field.strip():
                        # Remove leading minus for validation
                        field_name = field.strip().lstrip('-')
                        # Map old Swagger field names to Django field names
                        field_mapping = {
                            'title': 'question',
                            'description': 'answer',
                            'createdAt': 'created_at',
                        }
                        django_field = field_mapping.get(field_name, field_name)
                        if django_field in valid_fields:
                            # Add minus back if it was there
                            if field.strip().startswith('-'):
                                order_fields.append(f'-{django_field}')
                            else:
                                order_fields.append(django_field)
                        else:
                            invalid_fields.append(field.strip())
                
                if invalid_fields:
                    return create_error_response(
                        error_message=f'Invalid orderBy fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'orderBy': [f'Invalid fields: {", ".join(invalid_fields)}. Valid fields are: {", ".join(valid_fields)}']}
                    )
                
                if order_fields:
                    try:
                        qs = qs.order_by(*order_fields)
                    except Exception:
                        # If ordering fails, use default
                        qs = qs.order_by('-created_at')
                else:
                    qs = qs.order_by('-created_at')
            else:
                # Default ordering
                qs = qs.order_by('-created_at')
            
            # Get total count
            total_count = qs.count()
            
            # Calculate pagination
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
                # Handle pageNumber 0 - treat as page 1
                effective_page = page_number if page_number > 0 else 1
                start = (effective_page - 1) * page_size
                end = start + page_size
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                start = 0
                end = None
                has_previous = False
                has_next = False
            
            # Get paginated results
            if end is not None:
                items = qs[start:end]
            else:
                items = qs[start:]
            
            # Serialize results
            item_serializer = FaqSerializer(items, many=True, context={'request': request})
            items_data = item_serializer.data
            
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
    tags=['Faqs'],
    operation_id='faqs_client_search',
    summary='Client search for FAQs',
    description='Search for FAQs (client endpoint) matching old Swagger format.',
    request=FaqClientSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Client search',
            value={
                'categoryId': 0,
                'keyword': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Search results',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [],
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class FaqsClientSearchView(APIView):
    """POST /api/v1/faqs/client/search - Client search"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Search FAQs matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = FaqClientSearchRequestSerializer(data=request_data)
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
            
            # Get keyword
            keyword = validated_data.get('keyword') or ''
            
            # Build query (only active FAQs for client)
            qs = FAQ.objects.filter(is_active=True).order_by('-created_at')

            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(question__icontains=keyword.strip()) |
                    Q(answer__icontains=keyword.strip())
                )
            
            # Serialize results
            item_serializer = FaqSerializer(qs, many=True, context={'request': request})
            items_data = item_serializer.data
            
            # Build response matching old Swagger format
            return create_success_response(data=items_data)
        
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
    tags=['Faqs'],
    operation_id='faqs_client_search_take',
    summary='Client search for FAQs with take parameter',
    description='Search for FAQs with take parameter (client endpoint) matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='take',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description='Maximum number of results to return'
        )
    ],
    request=FaqClientSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Client search with take',
            value={
                'categoryId': 0,
                'keyword': 'string'
            }
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='Search results',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [],
                        'messages': [],
                        'succeeded': True
                    }
                )
            ]
        )
    }
)
class FaqsClientSearchTakeView(APIView):
    """POST /api/v1/faqs/client/search/{take} - Client search with take parameter"""
    permission_classes = [AllowAny]

    def post(self, request, take):
        """Search FAQs with take parameter (limit results) matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = FaqClientSearchRequestSerializer(data=request_data)
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
            
            # Get keyword
            keyword = validated_data.get('keyword') or ''
            
            # Build query (only active FAQs for client)
            qs = FAQ.objects.filter(is_active=True).order_by('-created_at')

            # Apply keyword search
            if keyword and keyword.strip():
                qs = qs.filter(
                    Q(question__icontains=keyword.strip()) |
                    Q(answer__icontains=keyword.strip())
                )
            
            # Limit to 'take' items
            try:
                take_int = int(take)
                qs = qs[:take_int]
            except (ValueError, TypeError):
                # If take is invalid, return all results
                pass
            
            items = list(qs)
            
            # Serialize results
            item_serializer = FaqSerializer(items, many=True, context={'request': request})
            items_data = item_serializer.data
            
            # Build response matching old Swagger format
            return create_success_response(data=items_data)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

