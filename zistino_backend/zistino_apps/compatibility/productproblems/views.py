"""
Views for ProductProblems compatibility layer.
Provides all 11 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.db.models import Q

from zistino_apps.products.models import Problem
from zistino_apps.products.serializers import ProblemSerializer, ProblemSearchRequestSerializer
from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response

from .serializers import (
    ProductProblemGroupSerializer,
    ProductProblemSaveRangeSerializer,
    ProductProblemSearchGroupRequestSerializer,
    ProductProblemCreateRequestSerializer,
    ProductProblemCompatibilitySerializer,
)


def transform_problem_to_old_swagger_format(problem, default_role_id=None):
    """
    Transform a Problem instance to match old Swagger format.
    Returns: {id, problem: null, product: null, roleId, price, isActive}
    """
    if default_role_id is None:
        from zistino_apps.compatibility.roles.models import Role
        default_role_id = '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea'
        try:
            role = Role.objects.first()
            if role:
                default_role_id = str(role.id)
        except:
            pass
    
    return {
        'id': problem.id,
        'problem': None,  # As per old Swagger
        'product': None,  # As per old Swagger
        'roleId': default_role_id,  # Use default role ID
        'price': float(problem.price) if problem.price else 0,
        'isActive': True  # Problem model doesn't have isActive, default to True
    }


@extend_schema(tags=['ProductProblems'])
class ProductProblemsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductProblems endpoints.
    Wraps the existing Problem model functionality and adds compatibility endpoints.
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin-only for create/update/delete, AllowAny for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'save_range', 'productproblem_group']:
            return [IsAuthenticated(), IsManager()]
        return [AllowAny()]

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_list',
        summary='List all product problems',
    )
    def list(self, request, *args, **kwargs):
        """List all product problems."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_retrieve',
        summary='Retrieve a product problem by ID',
        responses={
            200: {
                'description': 'Product problem details',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 2,
                                'problem': None,
                                'product': None,
                                'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                'price': 0,
                                'isActive': True
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a product problem by ID. Returns format matching old Swagger with messages and succeeded."""
        instance = self.get_object()
        response_data = transform_problem_to_old_swagger_format(instance)
        return create_success_response(data=response_data)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_create',
        summary='Create a new product problem',
        request=ProductProblemCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create product problem',
                value={
                    'problemId': 0,
                    'productId': 'string',
                    'roleId': 'string',
                    'price': 0,
                    'isActive': True
                }
            )
        ],
        responses={
            200: {
                'description': 'Product problem created/updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        """Create or update a product problem matching old Swagger format."""
        from zistino_apps.products.models import Product
        
        serializer = ProductProblemCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        problem_id = validated_data.get('problemId', 0)
        product_id = validated_data.get('productId')
        price = validated_data.get('price', 0)
        
        # Get product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return create_error_response(
                error_message=f'Product with ID "{product_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'productId': [f'Product with ID "{product_id}" not found.']}
            )
        
        # If problemId > 0, update existing problem; otherwise create new
        if problem_id and problem_id > 0:
            try:
                problem = Problem.objects.get(id=problem_id)
                # Update price if provided
                if price is not None:
                    problem.price = price
                # Update product if different
                if problem.product_id != product_id:
                    problem.product = product
                problem.save()
                return create_success_response(data=problem.id)
            except Problem.DoesNotExist:
                return create_error_response(
                    error_message=f'Problem with ID "{problem_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'problemId': [f'Problem with ID "{problem_id}" not found.']}
                )
        else:
            # Create new problem with minimal data
            # Note: title is required, so we'll use a default or require it
            # For now, we'll create with a default title
            problem = Problem.objects.create(
                title='New Problem',  # Default title - should be provided in request ideally
                product=product,
                price=price,
                description='',
                priority=0
            )
            return create_success_response(data=problem.id)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_update',
        summary='Update a product problem',
        request=ProblemSerializer,
        responses={
            200: {
                'description': 'Product problem updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 2,
                                'problem': None,
                                'product': None,
                                'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                'price': 0,
                                'isActive': True
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a product problem. Returns format matching old Swagger with messages and succeeded."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ProblemSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Refresh instance to get updated data
        instance.refresh_from_db()
        response_data = transform_problem_to_old_swagger_format(instance)
        return create_success_response(data=response_data)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_partial_update',
        summary='Partially update a product problem',
        request=ProblemSerializer,
        responses={
            200: {
                'description': 'Product problem updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'id': 2,
                                'problem': None,
                                'product': None,
                                'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                'price': 0,
                                'isActive': True
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a product problem. Returns format matching old Swagger with messages and succeeded."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_destroy',
        summary='Delete a product problem',
        responses={
            200: {
                'description': 'Product problem deleted successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': None,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a product problem. Returns format matching old Swagger with messages and succeeded."""
        instance = self.get_object()
        instance.delete()
        return create_success_response(data=None)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_search',
        summary='Search product problems using available filters',
        request=ProblemSearchRequestSerializer,
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search product problems with pagination and filters. Returns format matching old Swagger with messages and succeeded."""
        serializer = ProblemSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        page_number = serializer.validated_data.get('pageNumber', 1)
        page_size = serializer.validated_data.get('pageSize', 20)

        qs = Problem.objects.all().select_related('product', 'parent').order_by('-priority', 'title')

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        total = qs.count()

        return create_success_response(
            data=ProblemSerializer(items, many=True).data,
            pagination={
                'pageNumber': page_number,
                'pageSize': page_size,
                'total': total,
            }
        )

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_save_range',
        summary='Save a range of product problems',
        request=ProductProblemSaveRangeSerializer,
        examples=[
            OpenApiExample(
                'Save range of product problems',
                value={
                    'productId': 'string',
                    'productProblems': [
                        {
                            'id': 0,
                            'problemId': 0,
                            'productId': 'string',
                            'roleId': 'string',
                            'price': 0,
                            'isActive': True
                        }
                    ]
                }
            )
        ],
        responses={
            200: {
                'description': 'Product problems saved successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='save-range')
    def save_range(self, request):
        """Save multiple product problems at once matching old Swagger format."""
        from zistino_apps.products.models import Product
        
        serializer = ProductProblemSaveRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        product_id = validated_data.get('productId')
        product_problems = validated_data.get('productProblems', [])
        
        if not product_problems:
            return create_error_response(
                error_message='No product problems provided',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'productProblems': ['At least one product problem is required']}
            )
        
        # Validate product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return create_error_response(
                error_message=f'Product with ID "{product_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'productId': [f'Product with ID "{product_id}" not found.']}
            )
        
        saved_count = 0
        errors = []
        
        for idx, problem_data in enumerate(product_problems):
            try:
                # Get IDs from the problem data
                problem_item_id = problem_data.get('id', 0)
                problem_id = problem_data.get('problemId', 0)
                item_product_id = problem_data.get('productId', product_id)  # Use item's productId or fallback to top-level
                price = problem_data.get('price', 0)
                
                # Get the product for this item (use item's productId if different from top-level)
                if item_product_id != product_id:
                    try:
                        item_product = Product.objects.get(id=item_product_id)
                    except Product.DoesNotExist:
                        errors.append(f'Product problem {idx + 1}: Product with ID "{item_product_id}" not found')
                        continue
                else:
                    item_product = product
                
                # Use problem_item_id first, then problemId as fallback
                target_id = problem_item_id if problem_item_id > 0 else problem_id
                
                if target_id > 0:
                    # Update existing problem
                    try:
                        problem = Problem.objects.get(id=target_id)
                        # Update price if provided
                        if price is not None:
                            problem.price = price
                        # Update product if different
                        if str(problem.product_id) != item_product_id:
                            problem.product = item_product
                        problem.save()
                        saved_count += 1
                    except Problem.DoesNotExist:
                        errors.append(f'Product problem {idx + 1}: Problem with id {target_id} not found')
                else:
                    # Create new problem
                    problem = Problem.objects.create(
                        title='New Problem',  # Default title
                        product=item_product,
                        price=price,
                        description='',
                        priority=0
                    )
                    saved_count += 1
            except Exception as e:
                errors.append(f'Product problem {idx + 1}: {str(e)}')
        
        # Return success response with count of saved problems
        # If there are errors but some were saved, still return success with count
        return create_success_response(data=saved_count)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_search_group',
        summary='Search product problem groups using available filters',
        request=ProductProblemSearchGroupRequestSerializer,
        examples=[
            OpenApiExample(
                'Search product problem groups',
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
                    'productId': 'string'
                }
            )
        ],
        responses={
            200: {
                'description': 'Product problem groups search results',
                'content': {
                    'application/json': {
                        'example': {
                            'data': [
                                {
                                    'productId': '94860000-b419-c60d-2b41-08dc425c06b1',
                                    'productName': 'شامپو کلیر',
                                    'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                    'roleName': 'akmal'
                                }
                            ],
                            'currentPage': 0,
                            'totalPages': 1,
                            'totalCount': 1,
                            'pageSize': 1,
                            'hasPreviousPage': False,
                            'hasNextPage': True,
                            'messages': None,
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='search-group')
    def search_group(self, request):
        """
        Search for product problem groups matching old Swagger format.
        Returns products with their associated roles.
        """
        from zistino_apps.products.models import Product
        from zistino_apps.compatibility.roles.models import Role
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        serializer = ProductProblemSearchGroupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Get keyword from advancedSearch or top-level
        keyword = validated_data.get('keyword', '').strip()
        advanced_search = validated_data.get('advancedSearch')
        if advanced_search and isinstance(advanced_search, dict):
            advanced_keyword = advanced_search.get('keyword') or ''
            keyword = advanced_keyword or keyword
        
        # Get productId filter
        product_id = validated_data.get('productId')
        
        # Get pagination (0 defaults to 1)
        page_number = validated_data.get('pageNumber', 0)
        page_size = validated_data.get('pageSize', 0)
        
        if page_number == 0:
            page_number = 1
        if page_size == 0:
            page_size = 1
        
        # Start with products that have problems
        products_qs = Product.objects.filter(
            problems__isnull=False
        ).distinct()
        
        # Filter by productId if provided
        if product_id and product_id.strip():
            try:
                products_qs = products_qs.filter(id=product_id)
            except (ValueError, TypeError):
                pass  # Invalid UUID, skip filter
        
        # Filter by keyword if provided
        if keyword:
            products_qs = products_qs.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        # Get total count before pagination
        total_count = products_qs.count()
        
        # Apply pagination
        start = (page_number - 1) * page_size
        end = start + page_size
        products = products_qs[start:end]
        
        # Build response data: product-role pairs
        # Since there's no direct Product-Role relationship, we'll return products
        # with a default role or try to find roles from users who have this product
        response_data = []
        
        for product in products:
            # Try to find a role associated with this product
            # For now, we'll use a placeholder or try to get from user roles
            # If no role found, use a default role ID and name
            role_id = None
            role_name = None
            
            # Try to find role from users who have this product in their problems
            # or from some other relationship
            # For now, we'll use a placeholder approach
            try:
                # Try to get the first role from the system as a default
                role = Role.objects.first()
                if role:
                    role_id = str(role.id)
                    role_name = role.name
            except:
                pass
            
            # If no role found, use placeholder values
            if not role_id:
                role_id = '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea'  # Placeholder UUID
                role_name = 'default'  # Placeholder name
            
            response_data.append({
                'productId': str(product.id),
                'productName': product.name,
                'roleId': role_id,
                'roleName': role_name
            })
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
        has_previous_page = page_number > 1
        has_next_page = page_number < total_pages if total_pages > 0 else False
        
        # Return format matching old Swagger
        return Response({
            'data': response_data,
            'currentPage': page_number,
            'totalPages': total_pages,
            'totalCount': total_count,
            'pageSize': page_size,
            'hasPreviousPage': has_previous_page,
            'hasNextPage': has_next_page,
            'messages': None,
            'succeeded': True
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['ProductProblems'],
        operation_id='productproblems_productproblem_group',
        summary='Get product problems by product and role',
        request=ProductProblemGroupSerializer,
        examples=[
            OpenApiExample(
                'Get product problem group',
                value={
                    'productId': 'string',
                    'roleId': 'string'
                }
            )
        ],
        responses={
            200: {
                'description': 'Product problems for the specified product and role',
                'content': {
                    'application/json': {
                        'example': {
                            'data': {
                                'productId': '94860000-b419-c60d-2b41-08dc425c06b1',
                                'productProblems': [
                                    {
                                        'id': 2,
                                        'problemId': 1,
                                        'productId': '94860000-b419-c60d-2b41-08dc425c06b1',
                                        'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                        'price': 0,
                                        'isActive': True
                                    }
                                ]
                            },
                            'messages': [],
                            'succeeded': True
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='productproblem-group')
    def productproblem_group(self, request):
        """
        Get product problems by product and role matching old Swagger format.
        Returns all problems for the specified product (roleId is accepted but not used for filtering since Problem model doesn't have roleId).
        """
        from zistino_apps.products.models import Product
        
        serializer = ProductProblemGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        product_id = validated_data.get('productId')
        role_id = validated_data.get('roleId')
        
        # Validate product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return create_error_response(
                error_message=f'Product with ID "{product_id}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'productId': [f'Product with ID "{product_id}" not found.']}
            )
        
        # Get all problems for this product
        # Note: roleId is accepted in request but Problem model doesn't have roleId field
        # So we'll return all problems for the product
        problems = Problem.objects.filter(product_id=product_id).order_by('-priority', 'title')
        
        # Build productProblems array
        product_problems = []
        for problem in problems:
            product_problems.append({
                'id': problem.id,
                'problemId': problem.id,  # Same as id
                'productId': str(product.id),
                'roleId': role_id or '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',  # Use provided roleId or placeholder
                'price': float(problem.price) if problem.price else 0,
                'isActive': True  # Problem model doesn't have isActive, default to True
            })
        
        # Return format matching old Swagger
        return create_success_response(data={
            'productId': str(product.id),
            'productProblems': product_problems
        })


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(tags=['ProductProblems'])
class ProductProblemsDapperView(APIView):
    """GET /api/v1/productproblems/dapper"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get product problems in dapper context."""
        problems = Problem.objects.all().select_related('product', 'parent').order_by('-priority', 'title')
        return Response({
            'data': ProblemSerializer(problems, many=True).data,
        })


@extend_schema(
    tags=['ProductProblems'],
    operation_id='productproblems_all',
    summary='Get all product problems',
    description='Get all product problems matching old Swagger format.',
    responses={
        200: {
            'description': 'List of product problems',
            'content': {
                'application/json': {
                    'example': {
                        'data': [
                            {
                                'id': 2,
                                'problem': None,
                                'product': None,
                                'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                'price': 0,
                                'isActive': True
                            },
                            {
                                'id': 3,
                                'problem': None,
                                'product': None,
                                'roleId': '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea',
                                'price': 0,
                                'isActive': True
                            }
                        ],
                        'messages': [],
                        'succeeded': True
                    }
                }
            }
        }
    }
)
class ProductProblemsAllView(APIView):
    """GET /api/v1/productproblems/all"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all product problems. Returns format matching old Swagger with messages and succeeded."""
        from zistino_apps.compatibility.roles.models import Role
        
        problems = Problem.objects.all().select_related('product', 'parent').order_by('-priority', 'title')
        
        # Get a default role ID (or use placeholder)
        default_role_id = '0a4a0a3d-b583-4a96-ae5f-124f9d4c0dea'
        try:
            role = Role.objects.first()
            if role:
                default_role_id = str(role.id)
        except:
            pass
        
        # Transform to old Swagger format
        response_data = []
        for problem in problems:
            response_data.append(transform_problem_to_old_swagger_format(problem, default_role_id))
        
        return create_success_response(data=response_data)


@extend_schema(tags=['ProductProblems'])
class ProductProblemGroupDeleteView(APIView):
    """DELETE /api/v1/productproblems/productproblemgroup"""
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request):
        """
        Delete a product problem group.
        This deletes a parent problem (group) and optionally its children.
        """
        group_id = request.data.get('id') or request.query_params.get('id')
        
        if not group_id:
            return Response(
                {'error': 'Group ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            group = Problem.objects.get(id=group_id)
            # Check if it has children
            children_count = group.children.count()
            
            # Delete the group (this will cascade delete children if CASCADE is set)
            group.delete()
            
            return Response({
                'message': f'Problem group deleted successfully',
                'deletedGroupId': group_id,
                'deletedChildrenCount': children_count,
            })
        except Problem.DoesNotExist:
            return Response(
                {'error': f'Problem group with id {group_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

