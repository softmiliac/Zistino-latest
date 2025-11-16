"""
Views for TransactionWallet compatibility layer.
Provides all 10 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404

from zistino_apps.payments.models import Wallet, Transaction
from zistino_apps.payments.serializers import (
    WalletSerializer,
    TransactionSerializer,
    TransactionWalletSearchRequestSerializer,
)
from zistino_apps.payments.views import WalletViewSet, TransactionViewSet, AdminTransactionWalletSearchView
from zistino_apps.users.permissions import IsManager
from zistino_apps.authentication.models import User
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, OpenApiParameter
from datetime import datetime
from decimal import Decimal
from .serializers import (
    TransactionCreateRequestSerializer,
    DriverTransactionWalletTotalRequestSerializer,
    DriverTransactionWalletTotalByUserIdRequestSerializer,
    TransactionWalletTotalResponseSerializer,
    TransactionDetailResponseSerializer,
    TransactionWalletSearchRequestSerializer,
)


@extend_schema(tags=['TransactionWallet'])
class TransactionWalletViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TransactionWallet endpoints.
    Wraps the existing Wallet and Transaction views for compatibility.
    Note: This ViewSet works with Transaction model for CRUD operations.
    """
    queryset = Transaction.objects.all()
    serializer_class = WalletSerializer  # Keep for list, but we override CRUD methods
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        """Filter transactions based on user role."""
        if self.request.user.is_staff:
            return Transaction.objects.all()
        # For non-staff, return transactions for their wallet
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet)
    
    def get_object(self):
        """Override to handle both UUID and integer IDs for transactions."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs.get(lookup_url_kwarg)
        
        if not pk:
            return None
        
        # Try to get transaction by UUID first
        try:
            # Try parsing as UUID
            import uuid
            uuid.UUID(str(pk))
            return Transaction.objects.get(id=pk)
        except (Transaction.DoesNotExist, ValueError, TypeError):
            # If UUID parsing fails, try to find by integer hash
            # This is for backward compatibility with integer IDs
            import hashlib
            for txn in Transaction.objects.all():
                txn_id_str = str(txn.id).replace('-', '')
                txn_id_int = int(hashlib.md5(txn_id_str.encode()).hexdigest()[:8], 16) % 100000000
                if str(txn_id_int) == str(pk):
                    return txn
            
            # If not found, raise DoesNotExist
            raise Transaction.DoesNotExist(f'Transaction with ID "{pk}" not found.')

    @extend_schema(
        tags=['TransactionWallet'],
        operation_id='transactionwallet_list',
        summary='List all transaction wallets',
    )
    def list(self, request, *args, **kwargs):
        """List all transaction wallets."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['TransactionWallet'],
        operation_id='transactionwallet_retrieve',
        summary='Retrieve a transaction by ID',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Transaction details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "senderId": None,
                                "type": 0,
                                "price": 1110,
                                "coin": 0,
                                "exchangeRate": 0,
                                "finished": True,
                                "createdOn": "2025-11-10T18:22:23.6975578",
                                "status": 0,
                                "title": "string",
                                "description": "string"
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
        """Retrieve a transaction by ID matching old Swagger format."""
        try:
            transaction = self.get_object()
            serializer = TransactionDetailResponseSerializer(transaction)
            return create_success_response(data=serializer.data, messages=[])
        except Transaction.DoesNotExist:
            pk = kwargs.get('pk', 'unknown')
            return create_error_response(
                error_message=f'Transaction with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Transaction with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['TransactionWallet'],
        operation_id='transactionwallet_create',
        summary='Create a new transaction',
        request=TransactionCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Transaction (default)',
                value={
                    "userId": "string",
                    "senderId": "string",
                    "type": 0,
                    "price": 0,
                    "coin": 0,
                    "exchangeRate": 0,
                    "finished": True,
                    "createdOn": "2025-11-10T18:25:20.857Z",
                    "status": 0,
                    "title": "string",
                    "description": "string"
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Transaction created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 10012,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new transaction matching old Swagger format."""
        try:
            serializer = TransactionCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get user
            try:
                user = User.objects.get(id=validated_data['userId'])
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{validated_data["userId"]}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'userId': [f'User with ID "{validated_data["userId"]}" not found.']}
                )
            
            # Get or create wallet for user
            wallet, _ = Wallet.objects.get_or_create(user=user)
            
            # Map type (0=credit, 1=debit) to transaction_type
            transaction_type_map = {0: 'credit', 1: 'debit'}
            transaction_type = transaction_type_map.get(validated_data['type'], 'credit')
            
            # Map status (0=pending, 1=completed, 2=failed, 3=cancelled) to status
            status_map = {0: 'pending', 1: 'completed', 2: 'failed', 3: 'cancelled'}
            transaction_status = status_map.get(validated_data.get('status', 0), 'pending')
            
            # If finished is True, set status to completed
            if validated_data.get('finished', False):
                transaction_status = 'completed'
            
            # Create transaction
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=validated_data['price'],
                transaction_type=transaction_type,
                status=transaction_status,
                description=validated_data.get('description', '') or validated_data.get('title', ''),
                reference_id=validated_data.get('title', '') or '',
            )
            
            # Override created_at if createdOn is provided
            if validated_data.get('createdOn'):
                transaction.created_at = validated_data['createdOn']
                transaction.save(update_fields=['created_at'])
            
            # Return transaction ID (using integer hash for compatibility)
            # For now, return the UUID as string, but old Swagger expects integer
            # We'll use a hash-based approach to convert UUID to integer
            import hashlib
            transaction_id_str = str(transaction.id).replace('-', '')
            transaction_id_int = int(hashlib.md5(transaction_id_str.encode()).hexdigest()[:8], 16) % 100000000
            
            return create_success_response(data=transaction_id_int, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating transaction: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['TransactionWallet'],
        operation_id='transactionwallet_update',
        summary='Update a transaction',
        request=TransactionCreateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Transaction updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "senderId": None,
                                "type": 0,
                                "price": 1110,
                                "coin": 0,
                                "exchangeRate": 0,
                                "finished": True,
                                "createdOn": "2025-11-10T18:22:23.6975578",
                                "status": 0,
                                "title": "string",
                                "description": "string"
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
        """Update a transaction matching old Swagger format."""
        try:
            # Get transaction using get_object which handles both UUID and integer IDs
            transaction = self.get_object()
            
            serializer = TransactionCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get user if userId is provided
            if 'userId' in validated_data:
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    wallet, _ = Wallet.objects.get_or_create(user=user)
                    transaction.wallet = wallet
                except User.DoesNotExist:
                    return create_error_response(
                        error_message=f'User with ID "{validated_data["userId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'userId': [f'User with ID "{validated_data["userId"]}" not found.']}
                    )
            
            # Map type (0=credit, 1=debit) to transaction_type
            if 'type' in validated_data:
                transaction_type_map = {0: 'credit', 1: 'debit'}
                transaction.transaction_type = transaction_type_map.get(validated_data['type'], 'credit')
            
            # Map status
            if 'status' in validated_data or 'finished' in validated_data:
                status_map = {0: 'pending', 1: 'completed', 2: 'failed', 3: 'cancelled'}
                if validated_data.get('finished', False):
                    transaction.status = 'completed'
                elif 'status' in validated_data:
                    transaction.status = status_map.get(validated_data['status'], 'pending')
            
            # Update amount
            if 'price' in validated_data:
                transaction.amount = validated_data['price']
            
            # Update description and reference_id
            if 'description' in validated_data:
                transaction.description = validated_data['description'] or ''
            if 'title' in validated_data:
                transaction.reference_id = validated_data['title'] or ''
            
            # Update created_at if provided
            if validated_data.get('createdOn'):
                transaction.created_at = validated_data['createdOn']
            
            transaction.save()
            
            # Return updated transaction
            detail_serializer = TransactionDetailResponseSerializer(transaction)
            return create_success_response(data=detail_serializer.data, messages=[])
        except Transaction.DoesNotExist:
            return create_error_response(
                error_message=f'Transaction with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Transaction with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating transaction: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['TransactionWallet'],
        operation_id='transactionwallet_destroy',
        summary='Delete a transaction',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Transaction deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "senderId": None,
                                "type": 0,
                                "price": 1110,
                                "coin": 0,
                                "exchangeRate": 0,
                                "finished": True,
                                "createdOn": "2025-11-10T18:22:23.6975578",
                                "status": 0,
                                "title": "string",
                                "description": "string"
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
        """Delete a transaction matching old Swagger format."""
        try:
            # Get transaction using get_object which handles both UUID and integer IDs
            transaction = self.get_object()
            
            # Serialize before deletion
            serializer = TransactionDetailResponseSerializer(transaction)
            transaction_data = serializer.data
            
            # Delete transaction
            transaction.delete()
            
            return create_success_response(data=transaction_data, messages=[])
        except Transaction.DoesNotExist:
            return create_error_response(
                error_message=f'Transaction with ID "{kwargs.get("pk")}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Transaction with ID "{kwargs.get("pk")}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting transaction: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['TransactionWallet'],
        operation_id='transactionwallet_search',
        summary='Search transaction wallets using available filters',
        request=TransactionWalletSearchRequestSerializer,
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
                    "status": 0,
                    "type": 0,
                    "maxPrice": 0,
                    "minPrice": 0,
                    "startDate": "2025-11-10T19:06:43.534Z",
                    "endDate": "2025-11-10T19:06:43.534Z",
                    "finished": True
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
        """Search transaction wallets with pagination and filters matching old Swagger format."""
        try:
            serializer = TransactionWalletSearchRequestSerializer(data=request.data)
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
            qs = Transaction.objects.all().select_related('wallet', 'wallet__user')
            
            # Filter by userId
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    wallet, _ = Wallet.objects.get_or_create(user=user)
                    qs = qs.filter(wallet=wallet)
                except User.DoesNotExist:
                    pass  # If user not found, return empty results
            
            # Filter by status
            if validated_data.get('status') is not None:
                status_map = {0: 'pending', 1: 'completed', 2: 'failed', 3: 'cancelled'}
                status_value = status_map.get(validated_data['status'])
                if status_value:
                    qs = qs.filter(status=status_value)
            
            # Filter by type
            if validated_data.get('type') is not None:
                type_map = {0: 'credit', 1: 'debit'}
                type_value = type_map.get(validated_data['type'])
                if type_value:
                    qs = qs.filter(transaction_type=type_value)
            
            # Filter by finished
            if validated_data.get('finished') is not None:
                if validated_data['finished']:
                    qs = qs.filter(status='completed')
                else:
                    qs = qs.exclude(status='completed')
            
            # Filter by price range
            if validated_data.get('minPrice') is not None:
                qs = qs.filter(amount__gte=validated_data['minPrice'])
            if validated_data.get('maxPrice') is not None:
                qs = qs.filter(amount__lte=validated_data['maxPrice'])
            
            # Filter by date range
            if validated_data.get('startDate'):
                qs = qs.filter(created_at__gte=validated_data['startDate'])
            if validated_data.get('endDate'):
                qs = qs.filter(created_at__lte=validated_data['endDate'])
            
            # Apply keyword search
            keyword = validated_data.get('keyword', '').strip()
            if keyword:
                qs = qs.filter(
                    Q(description__icontains=keyword) |
                    Q(reference_id__icontains=keyword)
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
                        elif field.lower() in ['amount', 'price']:
                            mapped_field = 'amount'
                        elif field.lower() in ['status']:
                            mapped_field = 'status'
                        elif field.lower() in ['type', 'transaction_type']:
                            mapped_field = 'transaction_type'
                        
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
            
            # Serialize with detail serializer
            serializer = TransactionDetailResponseSerializer(items, many=True)
            
            # Return in old Swagger format
            return Response({
                'data': serializer.data,
                'currentPage': current_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
                'hasPreviousPage': has_previous_page,
                'hasNextPage': has_next_page,
                'messages': None,
                'succeeded': True
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching transactions: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['TransactionWallet'],
    operation_id='transactionwallet_search_client',
    summary='Search transaction wallets (client)',
    description='Search transaction wallets for the currently logged-in user.',
    request=TransactionWalletSearchRequestSerializer,
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
                "status": 0,
                "type": 0,
                "maxPrice": 0,
                "minPrice": 0,
                "startDate": "2025-11-10T19:06:43.534Z",
                "endDate": "2025-11-10T19:06:43.534Z",
                "finished": True
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
class TransactionWalletClientSearchView(APIView):
    """POST /api/v1/transactionwallet/search/client"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Search transaction wallets for the currently logged-in user matching old Swagger format."""
        try:
            serializer = TransactionWalletSearchRequestSerializer(data=request.data)
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
            
            # Get transactions for current user's wallet
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            qs = Transaction.objects.filter(wallet=wallet)
            
            # Filter by status
            if validated_data.get('status') is not None:
                status_map = {0: 'pending', 1: 'completed', 2: 'failed', 3: 'cancelled'}
                status_value = status_map.get(validated_data['status'])
                if status_value:
                    qs = qs.filter(status=status_value)
            
            # Filter by type
            if validated_data.get('type') is not None:
                type_map = {0: 'credit', 1: 'debit'}
                type_value = type_map.get(validated_data['type'])
                if type_value:
                    qs = qs.filter(transaction_type=type_value)
            
            # Filter by finished
            if validated_data.get('finished') is not None:
                if validated_data['finished']:
                    qs = qs.filter(status='completed')
                else:
                    qs = qs.exclude(status='completed')
            
            # Filter by price range
            if validated_data.get('minPrice') is not None:
                qs = qs.filter(amount__gte=validated_data['minPrice'])
            if validated_data.get('maxPrice') is not None:
                qs = qs.filter(amount__lte=validated_data['maxPrice'])
            
            # Filter by date range
            if validated_data.get('startDate'):
                qs = qs.filter(created_at__gte=validated_data['startDate'])
            if validated_data.get('endDate'):
                qs = qs.filter(created_at__lte=validated_data['endDate'])
            
            # Apply keyword filter
            keyword = validated_data.get('keyword', '').strip()
            if keyword:
                qs = qs.filter(
                    Q(description__icontains=keyword) |
                    Q(reference_id__icontains=keyword)
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
                        elif field.lower() in ['amount', 'price']:
                            mapped_field = 'amount'
                        elif field.lower() in ['status']:
                            mapped_field = 'status'
                        elif field.lower() in ['type', 'transaction_type']:
                            mapped_field = 'transaction_type'
                        
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
            
            # Serialize with detail serializer
            serializer = TransactionDetailResponseSerializer(items, many=True)
            
            # Return in old Swagger format
            return Response({
                'data': serializer.data,
                'currentPage': current_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
                'hasPreviousPage': has_previous_page,
                'hasNextPage': has_next_page,
                'messages': None,
                'succeeded': True
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching transactions: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['TransactionWallet'],
    operation_id='transactionwallet_mytransactionwallettotal',
    summary='Get my transaction wallet total',
    description='Get total transaction wallet amount for the currently logged-in user.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Transaction wallet total',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "price": 6110000,
                                "coin": None
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
class TransactionWalletMyTotalView(APIView):
    """GET /api/v1/transactionwallet/mytransactionwallettotal"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get wallet total for the currently logged-in user matching old Swagger format."""
        try:
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            
            # Return in old Swagger format
            return create_success_response(
                data=[{
                    'price': float(wallet.balance) if wallet.balance else None,
                    'coin': None
                }],
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['TransactionWallet'],
    operation_id='transactionwallet_mytransactionwallethistory',
    summary='Get my transaction wallet history',
    description='Get transaction history for the currently logged-in user.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Transaction history',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "userId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                "senderId": None,
                                "type": 0,
                                "price": -650000,
                                "coin": None,
                                "exchangeRate": 1,
                                "finished": True,
                                "createdOn": "2025-10-15T13:55:52.3890749",
                                "status": 1,
                                "title": None,
                                "description": None
                            },
                            {
                                "userId": "7b84eae6-aadf-43ca-895f-d47680ea0c51",
                                "senderId": None,
                                "type": 1,
                                "price": 250000,
                                "coin": None,
                                "exchangeRate": 1,
                                "finished": True,
                                "createdOn": "2025-10-15T13:55:18.7994144",
                                "status": 1,
                                "title": None,
                                "description": None
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
class TransactionWalletMyHistoryView(APIView):
    """GET /api/v1/transactionwallet/mytransactionwallethistory"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get transaction history for the currently logged-in user matching old Swagger format."""
        try:
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:100]
            
            # Serialize with compatibility serializer
            serializer = TransactionDetailResponseSerializer(transactions, many=True)
            
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['TransactionWallet'],
    operation_id='transactionwallet_drivertransactionwallettotal',
    summary='Get driver transaction wallet total',
    description='Get total transaction wallet amount for drivers with date range filter.',
    parameters=[
        OpenApiParameter(
            name='FromDate',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Start date filter (format: YYYY/MM/DD)'
        ),
        OpenApiParameter(
            name='Todate',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description='End date filter (format: YYYY/MM/DD)'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Transaction wallet total',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "price": None,
                                "coin": None
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
class TransactionWalletDriverTotalView(APIView):
    """GET /api/v1/transactionwallet/drivertransactionwallettotal"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get wallet total for the currently logged-in driver with date range filter."""
        try:
            # Parse date parameters
            from_date_str = request.query_params.get('FromDate', '').strip()
            to_date_str = request.query_params.get('Todate', '').strip()
            
            from_date = None
            to_date = None
            
            if from_date_str:
                try:
                    # Parse YYYY/MM/DD format
                    from_date = datetime.strptime(from_date_str, '%Y/%m/%d').date()
                except ValueError:
                    return create_error_response(
                        error_message=f'Invalid FromDate format. Expected YYYY/MM/DD, got: {from_date_str}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'FromDate': [f'Invalid date format. Expected YYYY/MM/DD.']}
                    )
            
            if to_date_str:
                try:
                    # Parse YYYY/MM/DD format
                    to_date = datetime.strptime(to_date_str, '%Y/%m/%d').date()
                except ValueError:
                    return create_error_response(
                        error_message=f'Invalid Todate format. Expected YYYY/MM/DD, got: {to_date_str}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'Todate': [f'Invalid date format. Expected YYYY/MM/DD.']}
                    )
            
            # Get wallet for current user
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            
            # Get transactions with date filter
            transactions = Transaction.objects.filter(wallet=wallet)
            
            if from_date:
                transactions = transactions.filter(created_at__date__gte=from_date)
            if to_date:
                transactions = transactions.filter(created_at__date__lte=to_date)
            
            # Calculate totals
            total_price = transactions.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            # Return in old Swagger format
            return create_success_response(
                data=[{
                    'price': float(total_price) if total_price else None,
                    'coin': None
                }],
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['TransactionWallet'],
    operation_id='transactionwallet_drivertransactionwallettotalbyuserid',
    summary='Get driver transaction wallet total by user ID',
    description='Get total transaction wallet amount for a specific driver by user ID with date range filter.',
    parameters=[
        OpenApiParameter(
            name='UserId',
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description='User ID (UUID)'
        ),
        OpenApiParameter(
            name='FromDate',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Start date filter (format: YYYY/MM/DD)'
        ),
        OpenApiParameter(
            name='Todate',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description='End date filter (format: YYYY/MM/DD)'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Transaction wallet total by user ID',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [
                            {
                                "price": None,
                                "coin": None
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
class TransactionWalletDriverTotalByUserIdView(APIView):
    """GET /api/v1/transactionwallet/drivertransactionwallettotalbyuserid"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get wallet total for a specific driver by user ID with date range filter."""
        try:
            # Get user ID from query parameters
            user_id_str = request.query_params.get('UserId', '').strip()
            if not user_id_str:
                return create_error_response(
                    error_message='UserId parameter is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'UserId': ['UserId parameter is required']}
                )
            
            try:
                user = User.objects.get(id=user_id_str)
            except User.DoesNotExist:
                return create_error_response(
                    error_message=f'User with ID "{user_id_str}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'UserId': [f'User with ID "{user_id_str}" not found.']}
                )
            
            # Parse date parameters
            from_date_str = request.query_params.get('FromDate', '').strip()
            to_date_str = request.query_params.get('Todate', '').strip()
            
            from_date = None
            to_date = None
            
            if from_date_str:
                try:
                    # Parse YYYY/MM/DD format
                    from_date = datetime.strptime(from_date_str, '%Y/%m/%d').date()
                except ValueError:
                    return create_error_response(
                        error_message=f'Invalid FromDate format. Expected YYYY/MM/DD, got: {from_date_str}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'FromDate': [f'Invalid date format. Expected YYYY/MM/DD.']}
                    )
            
            if to_date_str:
                try:
                    # Parse YYYY/MM/DD format
                    to_date = datetime.strptime(to_date_str, '%Y/%m/%d').date()
                except ValueError:
                    return create_error_response(
                        error_message=f'Invalid Todate format. Expected YYYY/MM/DD, got: {to_date_str}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'Todate': [f'Invalid date format. Expected YYYY/MM/DD.']}
                    )
            
            # Get wallet for user
            wallet, _ = Wallet.objects.get_or_create(user=user)
            
            # Get transactions with date filter
            transactions = Transaction.objects.filter(wallet=wallet)
            
            if from_date:
                transactions = transactions.filter(created_at__date__gte=from_date)
            if to_date:
                transactions = transactions.filter(created_at__date__lte=to_date)
            
            # Calculate totals
            total_price = transactions.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            # Return in old Swagger format
            return create_success_response(
                data=[{
                    'price': float(total_price) if total_price else None,
                    'coin': None
                }],
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

