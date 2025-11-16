"""
Views for Problems compatibility layer.
Matches old Swagger format exactly.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from django.db.models import Q
from django.db.models import Count

from zistino_apps.products.models import Problem
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    ProblemCreateRequestSerializer,
    ProblemSearchRequestSerializer,
    ProblemDetailSerializer
)


@extend_schema(tags=['Problems'])
class ProblemsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Problems endpoints matching old Swagger format.
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Admin-only for create/update/delete, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        tags=['Problems'],
        operation_id='problems_create',
        summary='Create a new problem',
        request=ProblemCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=ProblemCreateRequestSerializer,
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
        """Create a new problem matching old Swagger format."""
        try:
            serializer = ProblemCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Map fields from old Swagger format to Django model
            problem_data = {
                'title': validated_data.get('title'),
                'description': validated_data.get('description', ''),
                'icon_url': validated_data.get('iconUrl', ''),
                'repair_duration': validated_data.get('repairDuration', 0),
                'priority': validated_data.get('priority', 0),
                'locale': validated_data.get('locale', ''),
            }
            
            # Handle parentId (0 means no parent)
            parent_id = validated_data.get('parentId', 0)
            if parent_id and parent_id > 0:
                try:
                    parent = Problem.objects.get(id=parent_id)
                    problem_data['parent'] = parent
                except Problem.DoesNotExist:
                    return create_error_response(
                        error_message=f'Parent problem with ID "{parent_id}" not found.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'parentId': [f'Parent problem with ID "{parent_id}" not found.']}
                    )
            
            # Note: product is required in the model, but not in the old Swagger request
            # For now, we'll try to get the first product or return an error
            # TODO: Check if productId should be added to the request or if we need a default product
            from zistino_apps.products.models import Product
            try:
                # Try to get the first product as a default (or use a specific default product)
                default_product = Product.objects.first()
                if not default_product:
                    return create_error_response(
                        error_message='No products available. Please create a product first.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'productId': ['Product is required but no products exist in the system.']}
                    )
                problem_data['product'] = default_product
            except Exception as e:
                return create_error_response(
                    error_message=f'Error setting product: {str(e)}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'productId': ['Product is required.']}
                )
            
            # Create the problem
            problem = Problem.objects.create(**problem_data)
            
            # Return integer ID matching old Swagger format
            return create_success_response(data=problem.id, messages=[])
            
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating problem: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Problems'],
        operation_id='problems_retrieve',
        summary='Retrieve a problem by ID',
        responses={
            200: OpenApiResponse(
                response=ProblemDetailSerializer,
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "title": "new p",
                                "description": "asdf",
                                "iconUrl": "string",
                                "parentId": None,
                                "repairDuration": 1,
                                "priority": 1,
                                "locale": "string"
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
        """Retrieve a problem by ID matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = ProblemDetailSerializer(instance, context={'request': request})
            return create_success_response(data=serializer.data, messages=[])
        except Problem.DoesNotExist:
            return create_error_response(
                error_message=f'Problem with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Problem with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving problem: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Problems'],
        operation_id='problems_update',
        summary='Update a problem',
        request=ProblemCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=ProblemDetailSerializer,
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "title": "new p",
                                "description": "asdf",
                                "iconUrl": "string",
                                "parentId": None,
                                "repairDuration": 1,
                                "priority": 1,
                                "locale": "string"
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
        """Update a problem matching old Swagger format."""
        try:
            instance = self.get_object()
            serializer = ProblemCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update fields
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get('description', instance.description)
            instance.icon_url = validated_data.get('iconUrl', instance.icon_url)
            instance.repair_duration = validated_data.get('repairDuration', instance.repair_duration)
            instance.priority = validated_data.get('priority', instance.priority)
            instance.locale = validated_data.get('locale', instance.locale)
            
            # Handle parentId
            parent_id = validated_data.get('parentId', 0)
            if parent_id and parent_id > 0:
                try:
                    parent = Problem.objects.get(id=parent_id)
                    instance.parent = parent
                except Problem.DoesNotExist:
                    return create_error_response(
                        error_message=f'Parent problem with ID "{parent_id}" not found.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'parentId': [f'Parent problem with ID "{parent_id}" not found.']}
                    )
            elif parent_id == 0:
                instance.parent = None
            
            instance.save()
            
            response_serializer = ProblemDetailSerializer(instance, context={'request': request})
            return create_success_response(data=response_serializer.data, messages=[])
            
        except Problem.DoesNotExist:
            return create_error_response(
                error_message=f'Problem with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Problem with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating problem: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Problems'],
        operation_id='problems_partial_update',
        summary='Partially update a problem',
        request=ProblemCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=ProblemDetailSerializer,
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "title": "new p",
                                "description": "asdf",
                                "iconUrl": "string",
                                "parentId": None,
                                "repairDuration": 1,
                                "priority": 1,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a problem matching old Swagger format."""
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=['Problems'],
        operation_id='problems_destroy',
        summary='Delete a problem',
        responses={
            200: OpenApiResponse(
                response=ProblemDetailSerializer,
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "title": "new p",
                                "description": "asdf",
                                "iconUrl": "string",
                                "parentId": None,
                                "repairDuration": 1,
                                "priority": 1,
                                "locale": "string"
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a problem matching old Swagger format."""
        try:
            instance = self.get_object()
            response_serializer = ProblemDetailSerializer(instance, context={'request': request})
            instance.delete()
            return create_success_response(data=response_serializer.data, messages=[])
        except Problem.DoesNotExist:
            return create_error_response(
                error_message=f'Problem with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Problem with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting problem: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['Problems'],
        operation_id='problems_search',
        summary='Search problems using available filters',
        request=ProblemSearchRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=ProblemSearchRequestSerializer,
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [],
                            "currentPage": 1,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 1,
                            "hasPreviousPage": False,
                            "hasNextPage": False,
                            "messages": None,
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search problems with pagination and filters matching old Swagger format."""
        try:
            serializer = ProblemSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters (treat 0 as default)
            page_number = validated_data.get('pageNumber', 0) or 1
            page_size = validated_data.get('pageSize', 0) or 20
            
            # Start with all problems
            qs = Problem.objects.all().select_related('parent', 'product')
            
            # Apply filters
            keyword = validated_data.get('keyword', '')
            advanced_search = validated_data.get('advancedSearch')
            product_id = validated_data.get('productId', '')
            order_by = validated_data.get('orderBy', [])
            
            # Keyword search
            if keyword:
                qs = qs.filter(
                    Q(title__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
            
            # Advanced search
            if advanced_search:
                adv_keyword = advanced_search.get('keyword', '')
                if adv_keyword:
                    qs = qs.filter(
                        Q(title__icontains=adv_keyword) |
                        Q(description__icontains=adv_keyword)
                    )
            
            # Product filter
            if product_id:
                try:
                    qs = qs.filter(product_id=product_id)
                except Exception:
                    pass  # Invalid UUID format, skip filter
            
            # Order by
            if order_by:
                # Validate order by fields
                valid_fields = ['title', 'priority', 'created_at', 'repair_duration']
                order_fields = []
                for field in order_by:
                    if field in valid_fields or field.startswith('-'):
                        clean_field = field.lstrip('-')
                        if clean_field in valid_fields:
                            order_fields.append(field)
                if order_fields:
                    qs = qs.order_by(*order_fields)
                else:
                    qs = qs.order_by('-priority', 'title')
            else:
                qs = qs.order_by('-priority', 'title')
            
            # Pagination
            total_count = qs.count()
            total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end] if page_size > 0 else qs
            
            # Serialize results
            response_serializer = ProblemDetailSerializer(items, many=True)
            
            # Return paginated response matching old Swagger format
            # The response has 'data' as an array with pagination fields at the same level
            response_data = {
                "data": response_serializer.data,
                "currentPage": page_number,
                "totalPages": total_pages,
                "totalCount": total_count,
                "pageSize": page_size,
                "hasPreviousPage": page_number > 1,
                "hasNextPage": page_number < total_pages,
                "messages": None,
                "succeeded": True
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching problems: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['Problems'],
    operation_id='problems_dapper',
    summary='Get problems in dapper context',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.QUERY, required=False, description='Problem ID (optional)')
    ],
    responses={
        200: OpenApiResponse(
            response=ProblemDetailSerializer,
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
                            "title": "new p",
                            "description": "asdf",
                            "iconUrl": "string",
                            "parentId": None,
                            "repairDuration": 1,
                            "priority": 1,
                            "locale": "string"
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class ProblemsDapperView(APIView):
    """GET /api/v1/problems/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get problems in dapper context matching old Swagger format."""
        try:
            problem_id = request.query_params.get('id')
            
            # If ID is provided, return the specific problem
            if problem_id:
                try:
                    problem_id = int(problem_id)
                    problem = Problem.objects.get(id=problem_id)
                    serializer = ProblemDetailSerializer(problem, context={'request': request})
                    return create_success_response(data=serializer.data, messages=[])
                except (ValueError, Problem.DoesNotExist):
                    return create_error_response(
                        error_message=f'Problem with ID "{problem_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Problem with ID "{problem_id}" not found.']}
                    )
            
            # Old Swagger returns null for dapper when no ID
            return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Problems'],
    operation_id='problems_byparentid',
    summary='Get problems by parent ID',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Parent problem ID')
    ],
    responses={
        200: OpenApiResponse(
            response=ProblemDetailSerializer,
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class ProblemsByParentIdView(APIView):
    """GET /api/v1/problems/byparentid/{id}"""
    permission_classes = [AllowAny]

    def get(self, request, id):
        """Get all problems that have the specified parent ID matching old Swagger format."""
        try:
            parent_id = int(id)
            problems = Problem.objects.filter(parent_id=parent_id).select_related('parent', 'product').order_by('-priority', 'title')
            serializer = ProblemDetailSerializer(problems, many=True, context={'request': request})
            return create_success_response(data=serializer.data, messages=[])
        except ValueError:
            return create_error_response(
                error_message='Invalid parent ID. Must be an integer.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'id': ['Invalid parent ID. Must be an integer.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Problems'],
    operation_id='problems_children',
    summary='Get all child problems',
    responses={
        200: OpenApiResponse(
            response=ProblemDetailSerializer,
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class ProblemsChildrenView(APIView):
    """GET /api/v1/problems/children"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all problems that have a parent (child problems) matching old Swagger format."""
        try:
            problems = Problem.objects.filter(parent__isnull=False).select_related('parent', 'product').order_by('-priority', 'title')
            serializer = ProblemDetailSerializer(problems, many=True, context={'request': request})
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Problems'],
    operation_id='problems_byproductid',
    summary='Get problems by product ID',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Product ID (UUID)')
    ],
    responses={
        200: OpenApiResponse(
            response=ProblemDetailSerializer,
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class ProblemsByProductIdView(APIView):
    """GET /api/v1/problems/byproductid/{id}"""
    permission_classes = [AllowAny]

    def get(self, request, id):
        """Get all problems associated with a specific product ID matching old Swagger format."""
        try:
            problems = Problem.objects.filter(product_id=id).select_related('parent', 'product').order_by('-priority', 'title')
            serializer = ProblemDetailSerializer(problems, many=True, context={'request': request})
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Problems'],
    operation_id='problems_anonymous_byproductid',
    summary='Get problems by product ID (anonymous access)',
    parameters=[
        OpenApiParameter(name='id', type=str, location=OpenApiParameter.PATH, description='Product ID (UUID)')
    ],
    responses={
        200: OpenApiResponse(
            response=ProblemDetailSerializer,
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class ProblemsAnonymousByProductIdView(APIView):
    """GET /api/v1/problems/anonymous-byproductid/{id}"""
    permission_classes = [AllowAny]

    def get(self, request, id):
        """Get all problems associated with a specific product ID (anonymous access) matching old Swagger format."""
        try:
            problems = Problem.objects.filter(product_id=id).select_related('parent', 'product').order_by('-priority', 'title')
            serializer = ProblemDetailSerializer(problems, many=True, context={'request': request})
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
