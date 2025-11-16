from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from zistino_apps.users.permissions import IsManager
from django.db.models import Q, Sum
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

from .models import Wallet, Transaction, Coupon, BasketDiscount, DepositRequest
from .serializers import (
    WalletSerializer, TransactionSerializer, CouponSerializer,
    TransactionWalletSearchRequestSerializer,
    DepositRequestSerializer, DepositRequestCreateSerializer,
    DepositRequestSearchSerializer, DepositApproveSerializer, DepositRejectSerializer
)
from .sms_service import send_deposit_request_confirmation, send_deposit_confirmation, send_deposit_rejection, send_sms, add_melipayamak_pattern, send_sms_with_pattern, send_verification_code_pattern
from django.utils import timezone

from .serializers import ManagerPaymentRecordSerializer

@extend_schema(tags=['Payments'], exclude=True)  # Excluded: using compatibility layer instead
class WalletViewSet(viewsets.ModelViewSet):
    """ViewSet for managing wallets"""
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    @extend_schema(tags=['Customer'], operation_id='wallet_my_total')
    def my_total(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response({'total': wallet.balance})


@extend_schema(tags=['Payments'], exclude=True)  # Excluded: using compatibility layer instead
class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transactions"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)

    @extend_schema(tags=['Customer'], operation_id='wallet_my_history')
    def my_history(self, request):
        qs = Transaction.objects.filter(wallet__user=request.user).order_by('-created_at')[:100]
        return Response(TransactionSerializer(qs, many=True).data)

    @extend_schema(
        tags=['Customer'],
        operation_id='wallet_my_report',
        summary='Get credits and receipts report',
        description='Get summary report of total credits made and total receipts submitted. Credits are wallet credit transactions. Receipts are deposit requests with bank receipt reference numbers.',
        responses={
            200: {
                'description': 'Credits and receipts report',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Customer with credits and receipts',
                                'value': {
                                    'totalCredits': '250000.00',
                                    'creditCount': 5,
                                    'totalReceipts': '150000.00',
                                    'receiptCount': 3,
                                    'currency': 'Rials'
                                }
                            },
                            'example2': {
                                'summary': 'New customer with no transactions',
                                'value': {
                                    'totalCredits': '0.00',
                                    'creditCount': 0,
                                    'totalReceipts': '0.00',
                                    'receiptCount': 0,
                                    'currency': 'Rials'
                                }
                            },
                            'example3': {
                                'summary': 'Customer with credits but no receipts',
                                'value': {
                                    'totalCredits': '100000.00',
                                    'creditCount': 2,
                                    'totalReceipts': '0.00',
                                    'receiptCount': 0,
                                    'currency': 'Rials'
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='my-report')
    def my_report(self, request):
        """Get credits and receipts report for the logged-in customer."""
        user = request.user
        
        # Calculate total credits: sum of all credit transactions
        credit_transactions = Transaction.objects.filter(
            wallet__user=user,
            transaction_type='credit'
        )
        total_credits = credit_transactions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        credit_count = credit_transactions.count()
        
        # Calculate total receipts: sum of all deposit requests with receipt reference
        receipt_requests = DepositRequest.objects.filter(
            user=user,
            reference_id__isnull=False
        ).exclude(reference_id='')
        total_receipts = receipt_requests.aggregate(
            total=Sum('amount')
        )['total'] or 0
        receipt_count = receipt_requests.count()
        
        return Response({
            'totalCredits': str(total_credits),
            'creditCount': credit_count,
            'totalReceipts': str(total_receipts),
            'receiptCount': receipt_count,
            'currency': 'Rials'
        })


@extend_schema(tags=['Payments'])
class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Admin-only for create/update/delete/search, IsAuthenticated for read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search']:
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Admin'],
        operation_id='coupons_search',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'pageNumber': {'type': 'integer', 'default': 1},
                    'pageSize': {'type': 'integer', 'default': 20},
                }
            }
        },
        examples=[
            OpenApiExample(
                'Search coupons',
                value={
                    'pageNumber': 1,
                    'pageSize': 20
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Admin search endpoint for coupons with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        
        qs = Coupon.objects.all().order_by('-created_at')
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': CouponSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })

    @extend_schema(tags=['Customer'], operation_id='applycoupononbasket')
    def apply_on_basket(self, request):
        code = (request.data.get('code') or '').strip()
        if not code:
            return Response({'detail': 'code is required'}, status=400)
        try:
            coupon = Coupon.objects.get(key=code, status=1)
        except Coupon.DoesNotExist:
            return Response({'detail': 'invalid coupon'}, status=400)
        # For now just return coupon info; basket integration handled in baskets app
        return Response({'key': coupon.key, 'amount': coupon.amount, 'status': coupon.status})


# ============================================
# ADMIN ENDPOINTS - Separated for clarity
# ============================================
# These endpoints are for admin panel (is_staff=True)
# They provide admin-level access with search/pagination
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='transactionwallet_search',
    request=TransactionWalletSearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Search all transactions',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '',
                'advancedSearch': None
            }
        ),
        OpenApiExample(
            'Search by user ID',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '',
                'advancedSearch': {
                    'fields': ['userid'],
                    'keyword': '0641067f-df76-416c-98cd-6f89e43d3b3f'
                }
            }
        ),
        OpenApiExample(
            'Search by keyword',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': 'payment',
                'advancedSearch': None
            }
        )
    ]
)
class AdminTransactionWalletSearchView(APIView):
    """Admin search endpoint for wallet transactions with pagination and filtering."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search transactions with pagination and filters."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        advanced_search = request.data.get('advancedSearch')
        
        qs = Transaction.objects.all().select_related('wallet', 'wallet__user').order_by('-created_at')
        
        # Advanced search - filter by user ID if provided
        if advanced_search and isinstance(advanced_search, dict):
            fields = advanced_search.get('fields', [])
            search_keyword = advanced_search.get('keyword', '')
            
            if 'userid' in fields and search_keyword:
                # Filter by user ID
                qs = qs.filter(wallet__user_id=search_keyword)
        
        # Filter by keyword (search in description, reference_id, transaction type, status)
        if keyword:
            qs = qs.filter(
                Q(description__icontains=keyword) |
                Q(reference_id__icontains=keyword) |
                Q(transaction_type__icontains=keyword) |
                Q(status__icontains=keyword) |
                Q(wallet__user__phone_number__icontains=keyword) |
                Q(wallet__user__username__icontains=keyword)
            )
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': TransactionSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(
    tags=['Admin'],
    operation_id='couponuses_search',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pageNumber': {'type': 'integer', 'default': 1},
                'pageSize': {'type': 'integer', 'default': 20},
                'keyword': {'type': 'string', 'default': ''},
            }
        }
    },
    examples=[
        OpenApiExample(
            'Search coupon uses',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': ''
            }
        ),
        OpenApiExample(
            'Search by keyword',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': 'DISCOUNT10'
            }
        )
    ]
)
class AdminCouponUsesSearchView(APIView):
    """Admin search endpoint for coupon usage tracking (BasketDiscount records)."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search coupon uses (BasketDiscount records) with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        
        qs = BasketDiscount.objects.all().select_related('coupon', 'basket', 'basket__user').order_by('-created_at')
        
        # Filter by keyword (search in coupon key, user info)
        if keyword:
            qs = qs.filter(
                Q(coupon__key__icontains=keyword) |
                Q(basket__user__phone_number__icontains=keyword) |
                Q(basket__user__username__icontains=keyword)
            )
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        # Format response to match panel expectations
        coupon_uses_data = [{
            'id': bd.id,
            'couponId': bd.coupon.id,
            'couponKey': bd.coupon.key,
            'couponAmount': bd.coupon.amount,
            'userId': str(bd.basket.user.id) if bd.basket.user else None,
            'userPhone': bd.basket.user.phone_number if bd.basket.user else None,
            'amount': bd.amount,
            'createdAt': bd.created_at.isoformat() if bd.created_at else None,
        } for bd in items]
        
        return Response({
            'items': coupon_uses_data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


# ============================================
# DEPOSIT REQUEST ENDPOINTS
# ============================================
# Customer endpoints for deposit requests
# ============================================

@extend_schema(tags=['Deposit Request'])
class CustomerDepositRequestViewSet(viewsets.ViewSet):
    """ViewSet for customer deposit requests."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Deposit Request'],
        operation_id='deposit_request_create',
        summary='Create deposit request',
        description='Create a new deposit request. SMS confirmation will be sent automatically.',
        request=DepositRequestCreateSerializer,
        examples=[
            OpenApiExample(
                'Create deposit request',
                description='Request to deposit 100,000 Rials',
                value={
                    'amount': 100000
                }
            ),
            OpenApiExample(
                'Create deposit request with reference',
                description='Request with bank reference number',
                value={
                    'amount': 50000,
                    'reference_id': 'BANK-RECEIPT-12345'
                }
            )
        ],
        responses={
            201: {
                'description': 'Deposit request created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                            'amount': '100000.00',
                            'status': 'pending',
                            'reference_id': '',
                            'createdAt': '2024-01-15T10:30:00Z'
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'example': {
                            'amount': ['This field is required.']
                        }
                    }
                }
            }
        }
    )
    def create(self, request):
        """Create a new deposit request for the logged-in user."""
        serializer = DepositRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        reference_id = serializer.validated_data.get('reference_id', '')
        
        # Validate amount
        if amount <= 0:
            return Response(
                {'detail': 'Amount must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create deposit request
        deposit_request = DepositRequest.objects.create(
            user=request.user,
            amount=amount,
            reference_id=reference_id,
            status='pending'
        )
        
        # Send SMS confirmation
        try:
            send_deposit_request_confirmation(request.user.phone_number, amount)
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send SMS for deposit request {deposit_request.id}: {str(e)}")
        
        return Response(
            DepositRequestSerializer(deposit_request).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['Deposit Request'],
        operation_id='deposit_request_list',
        summary='List customer deposit requests',
        description='Get all deposit requests for the logged-in customer.',
        responses={
            200: {
                'description': 'List of deposit requests',
                'content': {
                    'application/json': {
                        'example': {
                            'items': [
                                {
                                    'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'amount': '100000.00',
                                    'status': 'pending',
                                    'createdAt': '2024-01-15T10:30:00Z'
                                },
                                {
                                    'id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                    'amount': '50000.00',
                                    'status': 'approved',
                                    'createdAt': '2024-01-14T09:00:00Z'
                                }
                            ],
                            'total': 2
                        }
                    }
                }
            }
        }
    )
    def list(self, request):
        """List all deposit requests for the logged-in user."""
        qs = DepositRequest.objects.filter(user=request.user).order_by('-created_at')
        serializer = DepositRequestSerializer(qs, many=True)
        return Response({
            'items': serializer.data,
            'total': qs.count()
        })

    @extend_schema(
        tags=['Deposit Request'],
        operation_id='deposit_request_retrieve',
        summary='Get deposit request details',
        description='Get details of a specific deposit request.',
        responses={
            200: {
                'description': 'Deposit request details',
                'content': {
                    'application/json': {
                        'example': {
                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                            'userId': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                            'amount': '100000.00',
                            'status': 'pending',
                            'reference_id': '',
                            'createdAt': '2024-01-15T10:30:00Z'
                        }
                    }
                }
            },
            404: {
                'description': 'Deposit request not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found'
                        }
                    }
                }
            }
        }
    )
    def retrieve(self, request, pk=None):
        """Get a specific deposit request by ID."""
        try:
            deposit_request = DepositRequest.objects.get(pk=pk, user=request.user)
        except DepositRequest.DoesNotExist:
            return Response(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(DepositRequestSerializer(deposit_request).data)


# ============================================
# ADMIN DEPOSIT REQUEST ENDPOINTS
# ============================================

@extend_schema(
    tags=['Deposit Request'],
    operation_id='deposit_request_search',
    request=DepositRequestSearchSerializer,
    examples=[
        OpenApiExample(
            'Search all deposit requests',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '',
                'status': ''
            }
        ),
        OpenApiExample(
            'Search pending requests',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '',
                'status': 'pending'
            }
        ),
        OpenApiExample(
            'Search by keyword',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '09121234567',
                'status': ''
            }
        )
    ]
)
class AdminDepositRequestSearchView(APIView):
    """Admin search endpoint for deposit requests."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search deposit requests with pagination and filters."""
        serializer = DepositRequestSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        page_number = serializer.validated_data.get('pageNumber', 1)
        page_size = serializer.validated_data.get('pageSize', 20)
        keyword = serializer.validated_data.get('keyword', '').strip()
        status_filter = serializer.validated_data.get('status', '').strip()
        
        qs = DepositRequest.objects.all().select_related('user', 'verified_by', 'transaction').order_by('-created_at')
        
        # Filter by status
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        # Filter by keyword (search in user phone, reference_id, description)
        if keyword:
            qs = qs.filter(
                Q(user__phone_number__icontains=keyword) |
                Q(user__username__icontains=keyword) |
                Q(reference_id__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': DepositRequestSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Deposit Request'])
class AdminDepositRequestViewSet(viewsets.ViewSet):
    """ViewSet for admin to manage deposit requests."""
    permission_classes = [IsAuthenticated, IsManager]

    @extend_schema(
        tags=['Deposit Request'],
        operation_id='deposit_request_approve',
        summary='Approve deposit request',
        description='Approve a deposit request. This will create a transaction, update wallet balance, and send SMS confirmation.',
        request=DepositApproveSerializer,
        examples=[
            OpenApiExample(
                'Approve deposit request',
                value={
                    'reference_id': 'BANK-RECEIPT-12345'
                }
            ),
            OpenApiExample(
                'Approve without reference',
                value={}
            )
        ],
        responses={
            200: {
                'description': 'Deposit request approved successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                            'status': 'approved',
                            'wallet_balance': '100000.00',
                            'transaction_id': '0641067f-df76-416c-98cd-6f89e43d3b3f'
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Deposit request is already approved'
                        }
                    }
                }
            },
            404: {
                'description': 'Deposit request not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Approve a deposit request."""
        try:
            deposit_request = DepositRequest.objects.get(pk=pk)
        except DepositRequest.DoesNotExist:
            return Response(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already processed
        if deposit_request.status != 'pending':
            return Response(
                {'detail': f'Deposit request is already {deposit_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request
        serializer = DepositApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference_id = serializer.validated_data.get('reference_id', '')
        
        # Get or create wallet for user
        wallet, _ = Wallet.objects.get_or_create(user=deposit_request.user)
        
        # Create transaction
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=deposit_request.amount,
            transaction_type='credit',
            status='completed',
            description=f'Deposit request {deposit_request.id}',
            reference_id=reference_id or deposit_request.reference_id
        )
        
        # Update wallet balance
        wallet.balance += deposit_request.amount
        wallet.save()
        
        # Update deposit request
        deposit_request.status = 'approved'
        deposit_request.verified_at = timezone.now()
        deposit_request.verified_by = request.user
        deposit_request.transaction = transaction
        if reference_id:
            deposit_request.reference_id = reference_id
        deposit_request.save()
        
        # Send SMS confirmation
        try:
            send_deposit_confirmation(
                deposit_request.user.phone_number,
                deposit_request.amount,
                wallet.balance
            )
        except Exception as e:
            logger.error(f"Failed to send SMS for deposit approval {deposit_request.id}: {str(e)}")
        
        return Response({
            **DepositRequestSerializer(deposit_request).data,
            'wallet_balance': str(wallet.balance),
            'transaction_id': str(transaction.id)
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Deposit Request'],
        operation_id='deposit_request_reject',
        summary='Reject deposit request',
        description='Reject a deposit request. Optional reason can be provided.',
        request=DepositRejectSerializer,
        examples=[
            OpenApiExample(
                'Reject deposit request',
                value={
                    'description': 'Insufficient funds or invalid reference'
                }
            ),
            OpenApiExample(
                'Reject without reason',
                value={}
            )
        ],
        responses={
            200: {
                'description': 'Deposit request rejected successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                            'status': 'rejected'
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Deposit request is already processed'
                        }
                    }
                }
            },
            404: {
                'description': 'Deposit request not found'
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """Reject a deposit request."""
        try:
            deposit_request = DepositRequest.objects.get(pk=pk)
        except DepositRequest.DoesNotExist:
            return Response(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already processed
        if deposit_request.status != 'pending':
            return Response(
                {'detail': f'Deposit request is already {deposit_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request
        serializer = DepositRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get('description', '')
        
        # Update deposit request
        deposit_request.status = 'rejected'
        deposit_request.verified_at = timezone.now()
        deposit_request.verified_by = request.user
        if reason:
            deposit_request.description = f"{deposit_request.description}\nRejection reason: {reason}".strip()
        deposit_request.save()
        
        # Send SMS notification (optional)
        try:
            send_deposit_rejection(
                deposit_request.user.phone_number,
                deposit_request.amount,
                reason if reason else None
            )
        except Exception as e:
            logger.error(f"Failed to send SMS for deposit rejection {deposit_request.id}: {str(e)}")
        
        return Response(DepositRequestSerializer(deposit_request).data, status=status.HTTP_200_OK)


# ============================================
# SMS TEST ENDPOINT
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='test_sms',
    summary='Test SMS sending',
    description='Admin endpoint to test SMS service. Sends a test SMS to verify Mizban SMS integration is working.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'phoneNumber': {'type': 'string', 'description': 'Phone number to send test SMS to (e.g., 09123456789 or +989123456789)'},
                'message': {'type': 'string', 'description': 'Custom message to send (optional, defaults to test message)'}
            },
            'required': ['phoneNumber']
        }
    },
    examples=[
        OpenApiExample(
            'Test SMS with default message',
            value={
                'phoneNumber': '09123456789'
            }
        ),
        OpenApiExample(
            'Test SMS with custom message',
            value={
                'phoneNumber': '+989123456789',
                'message': 'This is a custom test message from Zistino backend'
            }
        )
    ],
    responses={
        200: {
            'description': 'SMS test result',
            'content': {
                'application/json': {
                    'examples': {
                        'example1': {
                            'summary': 'SMS sent successfully',
                            'value': {
                                'success': True,
                                'message': 'SMS sent successfully',
                                'phoneNumber': '09123456789',
                                'sentMessage': 'Test SMS from Zistino backend - SMS service is working correctly!',
                                'note': 'Check the phone for received SMS. If credentials not configured, SMS is logged to console only.'
                            }
                        },
                        'example2': {
                            'summary': 'SMS failed',
                            'value': {
                                'success': False,
                                'message': 'Failed to send SMS',
                                'phoneNumber': '09123456789',
                                'error': 'Network error while sending SMS'
                            }
                        },
                        'example3': {
                            'summary': 'Credentials not configured',
                            'value': {
                                'success': True,
                                'message': 'SMS logged (credentials not configured)',
                                'phoneNumber': '09123456789',
                                'sentMessage': 'Test SMS from Zistino backend - SMS service is working correctly!',
                                'note': 'SMS credentials not configured in .env file. SMS was logged to console only. Please add MIZBAN_SMS_USERNAME and MIZBAN_SMS_PASSWORD to .env file.'
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'phoneNumber is required'
                    }
                }
            }
        }
    }
)
class TestSMSView(APIView):
    """Admin endpoint to test SMS sending."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Send test SMS."""
        phone_number = request.data.get('phoneNumber')
        custom_message = request.data.get('message')
        
        if not phone_number:
            return Response(
                {'detail': 'phoneNumber is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Default test message
        test_message = custom_message if custom_message else 'Test SMS from Zistino backend - SMS service is working correctly!'
        
        # Send SMS
        try:
            result, error_message = send_sms(phone_number, test_message)
            
            # Check which provider is configured
            from django.conf import settings
            melipayamak_configured = bool(settings.MELIPAYAMAK_USERNAME and settings.MELIPAYAMAK_API_KEY)
            mizban_configured = bool(settings.MIZBAN_SMS_USERNAME and settings.MIZBAN_SMS_PASSWORD) or bool(settings.MIZBAN_SMS_AUTH_TOKEN)
            has_credentials = melipayamak_configured or mizban_configured
            
            # Determine which provider was used
            if melipayamak_configured:
                provider = 'MeliPayamak'
                api_url = settings.MELIPAYAMAK_API_URL
                username_display = settings.MELIPAYAMAK_USERNAME[:3] + '***' if len(settings.MELIPAYAMAK_USERNAME) > 3 else '***'
            elif mizban_configured:
                provider = 'Mizban SMS'
                api_url = settings.MIZBAN_SMS_API_URL
                username_display = settings.MIZBAN_SMS_USERNAME[:3] + '***' if settings.MIZBAN_SMS_USERNAME and len(settings.MIZBAN_SMS_USERNAME) > 3 else '***'
            else:
                provider = 'None (Development Mode)'
                api_url = 'N/A'
                username_display = 'N/A'
            
            if result:
                if has_credentials:
                    return Response({
                        'success': True,
                        'message': 'SMS sent successfully',
                        'phoneNumber': phone_number,
                        'sentMessage': test_message,
                        'provider': provider,
                        'note': 'SMS accepted by API. Delivery typically takes 5-30 seconds. Check Django console for detailed API response. If not received after 2 minutes, check MeliPayamak dashboard for delivery status.',
                        'deliveryTime': 'Usually 5-30 seconds, can take up to 2 minutes'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': True,
                        'message': 'SMS logged (credentials not configured)',
                        'phoneNumber': phone_number,
                        'sentMessage': test_message,
                        'provider': provider,
                        'note': 'SMS credentials not configured in .env file. SMS was logged to console only. Please add MELIPAYAMAK or MIZBAN_SMS credentials to .env file and restart Django server.'
                    }, status=status.HTTP_200_OK)
            else:
                # Return detailed error message
                return Response({
                    'success': False,
                    'message': 'Failed to send SMS',
                    'phoneNumber': phone_number,
                    'error': error_message or 'Unknown error - check Django logs',
                    'provider': provider,
                    'note': 'SMS sending failed. Check the error message above and Django console/logs for more details.',
                    'debugInfo': {
                        'provider': provider,
                        'apiUrl': api_url,
                        'hasCredentials': has_credentials,
                        'username': username_display
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error testing SMS: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'message': 'Error while sending SMS',
                'phoneNumber': phone_number,
                'error': str(e),
                'note': 'Unexpected error occurred. Check Django logs for full traceback.'
            }, status=status.HTTP_200_OK)


# ============================================
# PATTERN REGISTRATION ENDPOINT
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='add_sms_pattern',
    summary='Add SMS pattern to MeliPayamak',
    description='Register a new SMS pattern (template) with MeliPayamak. Patterns are pre-approved message templates that can be used for sending SMS.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string', 'description': 'Pattern title/name (e.g., "Order Confirmation")'},
                'body': {'type': 'string', 'description': 'Pattern body with variables (e.g., "Your order #{order_id} has been confirmed. Total: {amount} Rials")'},
                'blackListId': {'type': 'integer', 'default': 1, 'description': 'Black list ID (default: 1)'}
            },
            'required': ['title', 'body']
        }
    },
    examples=[
        OpenApiExample(
            'Add order confirmation pattern',
            value={
                'title': 'Order Confirmation',
                'body': 'Your order #{order_id} has been confirmed. Total: {amount} Rials'
            }
        ),
        OpenApiExample(
            'Add deposit confirmation pattern',
            value={
                'title': 'Deposit Confirmation',
                'body': '{amount} Rials have been deposited into your account. Your current balance is {balance} Rials.'
            }
        )
    ],
    responses={
        200: {
            'description': 'Pattern registration result',
            'content': {
                'application/json': {
                    'examples': {
                        'example1': {
                            'summary': 'Pattern registered successfully',
                            'value': {
                                'success': True,
                                'message': 'Pattern registered successfully',
                                'patternId': 123456,
                                'title': 'Order Confirmation',
                                'body': 'Your order #{order_id} has been confirmed. Total: {amount} Rials'
                            }
                        },
                        'example2': {
                            'summary': 'Pattern registration failed',
                            'value': {
                                'success': False,
                                'message': 'Failed to register pattern',
                                'error': 'Invalid username or password (API key).'
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'title and body are required'
                    }
                }
            }
        }
    }
)
class AddSMSPatternView(APIView):
    """Admin endpoint to add SMS patterns to MeliPayamak."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Add SMS pattern to MeliPayamak."""
        title = request.data.get('title')
        body = request.data.get('body')
        black_list_id = request.data.get('blackListId', 1)
        
        if not title or not body:
            return Response(
                {'detail': 'title and body are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate blackListId
        try:
            black_list_id = int(black_list_id)
            if black_list_id != 1:
                return Response(
                    {'detail': 'blackListId must be 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'detail': 'blackListId must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add pattern
        try:
            success, pattern_id, error_message = add_melipayamak_pattern(
                title=title,
                body=body,
                black_list_id=black_list_id
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Pattern registered successfully',
                    'patternId': pattern_id,
                    'title': title,
                    'body': body,
                    'blackListId': black_list_id,
                    'note': f'Use pattern ID {pattern_id} to send SMS using this pattern. Save this ID for future use.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to register pattern',
                    'error': error_message,
                    'title': title,
                    'body': body
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error adding SMS pattern: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'message': 'Error while registering pattern',
                'error': str(e),
                'note': 'Unexpected error occurred. Check Django logs for full traceback.'
            }, status=status.HTTP_200_OK)


# ============================================
# SMS PATTERN TEST ENDPOINT
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='test_sms_pattern',
    summary='Test SMS sending with pattern',
    description='Test sending SMS using a registered MeliPayamak pattern. Pattern must be approved before use.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'phoneNumber': {'type': 'string', 'description': 'Phone number to send SMS to (e.g., 09123456789 or +989123456789)'},
                'patternId': {'type': 'integer', 'description': 'Pattern ID (BodyId) from MeliPayamak (e.g., 389656)'},
                'patternArgs': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'List of values to replace pattern variables. For pattern 389656: [userName, verificationCode, date, time]'
                },
                'useVerificationPattern': {
                    'type': 'boolean',
                    'default': False,
                    'description': 'If true, uses the Zistino verification code pattern (ID: 389656). Only requires userName and verificationCode.'
                },
                'userName': {'type': 'string', 'description': 'User name (for verification pattern)'},
                'verificationCode': {'type': 'string', 'description': 'Verification code (for verification pattern)'}
            },
            'required': ['phoneNumber']
        }
    },
    examples=[
        OpenApiExample(
            'Test verification code pattern (simplified)',
            value={
                'phoneNumber': '09123456789',
                'useVerificationPattern': True,
                'userName': 'علی احمدی',
                'verificationCode': '12345'
            }
        ),
        OpenApiExample(
            'Test custom pattern',
            value={
                'phoneNumber': '09123456789',
                'patternId': 389656,
                'patternArgs': ['علی احمدی', '12345', '1404/08/15', '14:30']
            }
        )
    ],
    responses={
        200: {
            'description': 'SMS pattern test result',
            'content': {
                'application/json': {
                    'examples': {
                        'example1': {
                            'summary': 'SMS sent successfully',
                            'value': {
                                'success': True,
                                'message': 'SMS sent successfully using pattern',
                                'patternId': 389656,
                                'phoneNumber': '09123456789'
                            }
                        },
                        'example2': {
                            'summary': 'SMS failed',
                            'value': {
                                'success': False,
                                'message': 'Failed to send SMS',
                                'error': 'Pattern not approved or invalid pattern ID'
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'phoneNumber is required'
                    }
                }
            }
        }
    }
)
class TestSMSPatternView(APIView):
    """Admin endpoint to test sending SMS with patterns."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Test sending SMS with pattern."""
        phone_number = request.data.get('phoneNumber')
        use_verification_pattern = request.data.get('useVerificationPattern', False)
        
        if not phone_number:
            return Response(
                {'detail': 'phoneNumber is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if use_verification_pattern:
                # Use the simplified verification code pattern
                user_name = request.data.get('userName', 'کاربر')
                verification_code = request.data.get('verificationCode', '12345')
                
                if not verification_code:
                    return Response(
                        {'detail': 'verificationCode is required when useVerificationPattern is true'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                success, error_message = send_verification_code_pattern(
                    phone_number=phone_number,
                    user_name=user_name,
                    verification_code=verification_code
                )
                
                pattern_id = 389656
                pattern_args = [user_name, verification_code]
            else:
                # Use custom pattern
                pattern_id = request.data.get('patternId')
                pattern_args = request.data.get('patternArgs', [])
                
                if not pattern_id:
                    return Response(
                        {'detail': 'patternId is required when useVerificationPattern is false'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if not isinstance(pattern_args, list):
                    return Response(
                        {'detail': 'patternArgs must be a list'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                success, error_message = send_sms_with_pattern(
                    phone_number=phone_number,
                    pattern_id=pattern_id,
                    pattern_args=pattern_args
                )
            
            if success:
                return Response({
                    'success': True,
                    'message': 'SMS sent successfully using pattern',
                    'patternId': pattern_id,
                    'patternArgs': pattern_args,
                    'phoneNumber': phone_number,
                    'note': 'Check the phone for received SMS. Make sure the pattern is approved in MeliPayamak dashboard.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to send SMS using pattern',
                    'error': error_message,
                    'patternId': pattern_id,
                    'patternArgs': pattern_args,
                    'phoneNumber': phone_number,
                    'note': 'Pattern might not be approved yet, or there might be an issue with the pattern ID or arguments.'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error testing SMS pattern: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'message': 'Error while sending SMS with pattern',
                'error': str(e),
                'note': 'Unexpected error occurred. Check Django logs for full traceback.'
            }, status=status.HTTP_200_OK)


# ============================================
# MANAGER ENDPOINTS - Credits Reports
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='manager_customer_credits',
    summary='View customer credits report',
    description='Manager view of customer credits aggregated by user. Shows total wallet balance and total credits received.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pageNumber': {'type': 'integer', 'default': 1},
                'pageSize': {'type': 'integer', 'default': 20},
                'keyword': {'type': 'string', 'default': ''},
                'userId': {'type': 'string', 'description': 'Optional: filter by specific user UUID'}
            }
        }
    },
    examples=[
        OpenApiExample('View all customers', value={'pageNumber': 1, 'pageSize': 20, 'keyword': ''}),
        OpenApiExample('Search by phone', value={'pageNumber': 1, 'pageSize': 20, 'keyword': '+98912'}),
        OpenApiExample('Filter by user', value={'pageNumber': 1, 'pageSize': 20, 'keyword': '', 'userId': 'user-uuid'})
    ],
    responses={
        200: {
            'description': 'Customer credits report',
            'content': {
                'application/json': {
                    'example': {
                        'items': [
                            {
                                'userId': 'user-uuid',
                                'phoneNumber': '+989121234567',
                                'fullName': 'John Doe',
                                'currentBalance': '150000.00',
                                'totalCredits': '250000.00',
                                'creditCount': 5,
                                'currency': 'Rials'
                            }
                        ],
                        'total': 100,
                        'pageNumber': 1,
                        'pageSize': 20
                    }
                }
            }
        }
    }
)
class ManagerCustomerCreditsView(APIView):
    """Manager endpoint to view customer credits aggregated by user."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Get customer credits report with pagination."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        user_id = request.data.get('userId')
        
        # Get users who have wallets or transactions
        qs = User.objects.filter(
            Q(wallet__isnull=False) | Q(wallet__transactions__isnull=False)
        ).distinct().order_by('-wallet__updated_at', '-id')
        
        # Filter by user ID if provided
        if user_id:
            qs = qs.filter(id=user_id)
        
        # Filter by keyword (phone, name)
        if keyword:
            qs = qs.filter(
                Q(phone_number__icontains=keyword) |
                Q(username__icontains=keyword) |
                Q(first_name__icontains=keyword) |
                Q(last_name__icontains=keyword)
            )
        
        # Pagination
        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        users = qs[start:end]
        
        # Build report
        items = []
        for user in users:
            wallet = getattr(user, 'wallet', None)
            current_balance = wallet.balance if wallet else 0
            
            # Calculate total credits
            credit_transactions = Transaction.objects.filter(
                wallet__user=user,
                transaction_type='credit',
                status='completed'
            )
            total_credits = credit_transactions.aggregate(total=Sum('amount'))['total'] or 0
            credit_count = credit_transactions.count()
            
            items.append({
                'userId': str(user.id),
                'phoneNumber': user.phone_number,
                'fullName': user.get_full_name() or f"{user.first_name} {user.last_name}".strip() or 'N/A',
                'currentBalance': f"{current_balance:.2f}",
                'totalCredits': f"{total_credits:.2f}",
                'creditCount': credit_count,
                'currency': 'Rials'
            })
        
        return Response({
            'items': items,
            'total': total,
            'pageNumber': page_number,
            'pageSize': page_size
        })


@extend_schema(
    tags=['Admin'],
    operation_id='manager_driver_credits',
    summary='View driver credits/payouts report',
    description='Manager view of driver payouts aggregated by driver. Shows total wallet balance and total payouts received from deliveries.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pageNumber': {'type': 'integer', 'default': 1},
                'pageSize': {'type': 'integer', 'default': 20},
                'keyword': {'type': 'string', 'default': ''},
                'driverId': {'type': 'string', 'description': 'Optional: filter by specific driver UUID'},
                'dateFrom': {'type': 'string', 'format': 'date-time', 'description': 'Optional: filter transactions from date'},
                'dateTo': {'type': 'string', 'format': 'date-time', 'description': 'Optional: filter transactions to date'}
            }
        }
    },
    examples=[
        OpenApiExample('View all drivers', value={'pageNumber': 1, 'pageSize': 20, 'keyword': ''}),
        OpenApiExample('Search by phone', value={'pageNumber': 1, 'pageSize': 20, 'keyword': '+98912'}),
        OpenApiExample('Filter by driver', value={'pageNumber': 1, 'pageSize': 20, 'keyword': '', 'driverId': 'driver-uuid'}),
        OpenApiExample('Filter by date range', value={
            'pageNumber': 1, 'pageSize': 20, 'keyword': '',
            'dateFrom': '2024-01-01T00:00:00Z', 'dateTo': '2024-01-31T23:59:59Z'
        })
    ],
    responses={
        200: {
            'description': 'Driver credits/payouts report',
            'content': {
                'application/json': {
                    'example': {
                        'items': [
                            {
                                'driverId': 'driver-uuid',
                                'phoneNumber': '+989121234567',
                                'fullName': 'Driver Name',
                                'currentBalance': '50000.00',
                                'totalPayouts': '150000.00',
                                'payoutCount': 10,
                                'totalDeliveries': 10,
                                'totalWeight': '150.50',
                                'currency': 'Rials'
                            }
                        ],
                        'total': 50,
                        'pageNumber': 1,
                        'pageSize': 20
                    }
                }
            }
        }
    }
)
class ManagerDriverCreditsView(APIView):
    """Manager endpoint to view driver payouts aggregated by driver."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Get driver payouts report with pagination."""
        from django.contrib.auth import get_user_model
        from zistino_apps.deliveries.models import Delivery
        User = get_user_model()
        
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        driver_id = request.data.get('driverId')
        date_from = request.data.get('dateFrom')
        date_to = request.data.get('dateTo')
        
        # Get drivers (users with is_driver=True) who have wallets or payout transactions
        qs = User.objects.filter(is_driver=True).filter(
            Q(wallet__isnull=False) | Q(wallet__transactions__isnull=False)
        ).distinct().order_by('-wallet__updated_at', '-id')
        
        # Filter by driver ID if provided
        if driver_id:
            qs = qs.filter(id=driver_id)
        
        # Filter by keyword (phone, name)
        if keyword:
            qs = qs.filter(
                Q(phone_number__icontains=keyword) |
                Q(username__icontains=keyword) |
                Q(first_name__icontains=keyword) |
                Q(last_name__icontains=keyword)
            )
        
        # Pagination
        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        drivers = qs[start:end]
        
        # Build report
        items = []
        for driver in drivers:
            wallet = getattr(driver, 'wallet', None)
            current_balance = wallet.balance if wallet else 0
            
            # Filter payout transactions (description contains "Driver payout")
            payout_qs = Transaction.objects.filter(
                wallet__user=driver,
                transaction_type='credit',
                status='completed',
                description__icontains='Driver payout'
            )
            
            # Apply date filters if provided
            if date_from:
                from django.utils.dateparse import parse_datetime
                dt_from = parse_datetime(date_from)
                if dt_from:
                    payout_qs = payout_qs.filter(created_at__gte=dt_from)
            
            if date_to:
                from django.utils.dateparse import parse_datetime
                dt_to = parse_datetime(date_to)
                if dt_to:
                    payout_qs = payout_qs.filter(created_at__lte=dt_to)
            
            total_payouts = payout_qs.aggregate(total=Sum('amount'))['total'] or 0
            payout_count = payout_qs.count()
            
            # Count deliveries and total weight (filter by delivery_date or created_at)
            delivery_qs = Delivery.objects.filter(
                driver=driver,
                customer_confirmation_status='confirmed',
                status='completed'
            )
            if date_from:
                from django.utils.dateparse import parse_datetime
                dt_from = parse_datetime(date_from)
                if dt_from:
                    delivery_qs = delivery_qs.filter(created_at__gte=dt_from)
            if date_to:
                from django.utils.dateparse import parse_datetime
                dt_to = parse_datetime(date_to)
                if dt_to:
                    delivery_qs = delivery_qs.filter(created_at__lte=dt_to)
            
            total_deliveries = delivery_qs.count()
            # Sum delivered_weight
            total_weight = delivery_qs.aggregate(total=Sum('delivered_weight'))['total'] or 0
            
            items.append({
                'driverId': str(driver.id),
                'phoneNumber': driver.phone_number,
                'fullName': driver.get_full_name() or f"{driver.first_name} {driver.last_name}".strip() or 'N/A',
                'currentBalance': f"{current_balance:.2f}",
                'totalPayouts': f"{total_payouts:.2f}",
                'payoutCount': payout_count,
                'totalDeliveries': total_deliveries,
                'totalWeight': f"{float(total_weight):.2f}",
                'currency': 'Rials'
            })
        
        return Response({
            'items': items,
            'total': total,
            'pageNumber': page_number,
            'pageSize': page_size
        })


@extend_schema(
    tags=['Admin'],
    operation_id='manager_payments_record',
    summary='Record manual payment (credit or debit) to a user',
    description='Manager records a manual wallet transaction for a customer or driver.',
    request=ManagerPaymentRecordSerializer,
    examples=[
        OpenApiExample('Credit customer', value={
            'userId': 'user-uuid', 'amount': '125000.00', 'transactionType': 'credit', 'description': 'Manual adjustment'}),
        OpenApiExample('Debit driver', value={
            'userId': 'driver-uuid', 'amount': '50000.00', 'transactionType': 'debit', 'description': 'Correction'})
    ],
    responses={
        200: {
            'description': 'Transaction recorded',
            'content': {'application/json': {'example': {
                'message': 'Transaction recorded',
                'userId': 'user-uuid',
                'newBalance': '350000.00',
                'transaction': {
                    'id': 'tx-uuid', 'amount': '125000.00', 'transaction_type': 'credit', 'status': 'completed'
                }
            }}}
        }
    }
)
class ManagerPaymentRecordView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        from django.contrib.auth import get_user_model
        from decimal import Decimal

        serializer = ManagerPaymentRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_id = data['userId']
        amount = data['amount']
        tx_type = data['transactionType']
        description = data.get('description', '')

        # Load user
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create or get wallet
        wallet, _ = Wallet.objects.get_or_create(user=user, defaults={'balance': Decimal('0.00')})

        # Adjust balance
        if tx_type == 'credit':
            wallet.balance = (wallet.balance or Decimal('0.00')) + amount
        else:
            wallet.balance = (wallet.balance or Decimal('0.00')) - amount
        wallet.save(update_fields=['balance'])

        # Record transaction
        tx = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=tx_type,
            status='completed',
            description=description or f'Manager {tx_type}'
        )

        return Response({
            'message': 'Transaction recorded',
            'userId': str(user.id),
            'newBalance': f"{wallet.balance:.2f}",
            'transaction': {
                'id': str(tx.id),
                'amount': f"{tx.amount:.2f}",
                'transaction_type': tx.transaction_type,
                'status': tx.status
            }
        }, status=status.HTTP_200_OK)
