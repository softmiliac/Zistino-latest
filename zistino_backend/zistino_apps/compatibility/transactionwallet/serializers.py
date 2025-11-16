"""
Serializers for TransactionWallet endpoints.
These import from payments app serializers and add compatibility request/response serializers.
"""
from rest_framework import serializers
from zistino_apps.payments.serializers import (
    WalletSerializer,
    TransactionSerializer,
    TransactionWalletSearchRequestSerializer,
)

# Reuse WalletSerializer, TransactionSerializer, and TransactionWalletSearchRequestSerializer from payments app
# These are already compatible with Flutter app expectations


class TransactionCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating transaction matching old Swagger format."""
    userId = serializers.CharField(required=True, help_text='User ID (UUID string)')
    senderId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Sender ID (UUID string)')
    type = serializers.IntegerField(required=True, help_text='Transaction type (0=credit, 1=debit)')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text='Transaction price/amount')
    coin = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Coin amount')
    exchangeRate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True, default=0, help_text='Exchange rate')
    finished = serializers.BooleanField(required=False, default=False, help_text='Whether transaction is finished')
    createdOn = serializers.DateTimeField(required=False, allow_null=True, help_text='Transaction creation date')
    status = serializers.IntegerField(required=False, default=0, help_text='Transaction status (0=pending, 1=completed, 2=failed, 3=cancelled)')
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Transaction title')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Transaction description')


class DriverTransactionWalletTotalRequestSerializer(serializers.Serializer):
    """Request serializer for getting driver wallet total."""
    pass  # Empty request body


class DriverTransactionWalletTotalByUserIdRequestSerializer(serializers.Serializer):
    """Request serializer for getting driver wallet total by user ID."""
    userId = serializers.UUIDField(required=True)


class TransactionWalletTotalResponseSerializer(serializers.Serializer):
    """Response serializer for transaction wallet total."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    coin = serializers.IntegerField(allow_null=True, required=False)


class TransactionWalletSearchRequestSerializer(serializers.Serializer):
    """Request serializer for transaction wallet search matching old Swagger format."""
    advancedSearch = serializers.DictField(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0)
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0)
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True
    )
    userId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='User ID (UUID string)')
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Transaction status (0=pending, 1=completed, 2=failed, 3=cancelled)')
    type = serializers.IntegerField(required=False, allow_null=True, help_text='Transaction type (0=credit, 1=debit)')
    maxPrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True, help_text='Maximum price filter')
    minPrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True, help_text='Minimum price filter')
    startDate = serializers.DateTimeField(required=False, allow_null=True, help_text='Start date filter')
    endDate = serializers.DateTimeField(required=False, allow_null=True, help_text='End date filter')
    finished = serializers.BooleanField(required=False, allow_null=True, help_text='Filter by finished status')


class TransactionDetailResponseSerializer(serializers.Serializer):
    """Response serializer for transaction details matching old Swagger format."""
    userId = serializers.CharField(source='wallet.user.id', read_only=True)
    senderId = serializers.CharField(allow_null=True, required=False, default=None)
    type = serializers.SerializerMethodField()
    price = serializers.DecimalField(source='amount', max_digits=10, decimal_places=2, read_only=True)
    coin = serializers.IntegerField(allow_null=True, required=False, default=None)
    exchangeRate = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False, default=1)
    finished = serializers.SerializerMethodField()
    createdOn = serializers.DateTimeField(source='created_at', read_only=True)
    status = serializers.SerializerMethodField()
    title = serializers.CharField(source='reference_id', allow_null=True, required=False, read_only=True)
    description = serializers.CharField(allow_null=True, required=False, read_only=True)
    
    def get_type(self, obj):
        """Map transaction_type to integer (0=credit, 1=debit)."""
        type_map = {'credit': 0, 'debit': 1}
        return type_map.get(obj.transaction_type, 0)
    
    def get_finished(self, obj):
        """Map status to finished boolean."""
        return obj.status == 'completed'
    
    def get_status(self, obj):
        """Map status string to integer (0=pending, 1=completed, 2=failed, 3=cancelled)."""
        status_map = {'pending': 0, 'completed': 1, 'failed': 2, 'cancelled': 3}
        return status_map.get(obj.status, 0)

