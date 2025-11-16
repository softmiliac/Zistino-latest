from rest_framework import serializers
from .models import Wallet, Transaction, Coupon, DepositRequest


class WalletSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'user_name', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.DecimalField(source='wallet.balance', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'amount', 'transaction_type', 'status',
            'description', 'reference_id', 'created_at', 'wallet_balance'
        ]
        read_only_fields = ['id', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'key', 'amount', 'status', 'valid_from', 'valid_to',
            'usage_limit', 'used_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'used_count']


class TransactionWalletSearchRequestSerializer(serializers.Serializer):
    """Request serializer for transaction wallet search (admin endpoint)."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    advancedSearch = serializers.DictField(required=False, allow_null=True, help_text='Advanced search options (e.g., {"fields": ["userid"], "keyword": "user_id"})')


# ============================================
# DEPOSIT REQUEST SERIALIZERS
# ============================================

class DepositRequestSerializer(serializers.ModelSerializer):
    """Serializer for DepositRequest model."""
    userId = serializers.UUIDField(source='user.id', read_only=True)
    userPhone = serializers.CharField(source='user.phone_number', read_only=True)
    userName = serializers.SerializerMethodField()
    verifiedById = serializers.UUIDField(source='verified_by.id', read_only=True, allow_null=True)
    verifiedByName = serializers.SerializerMethodField()
    transactionId = serializers.UUIDField(source='transaction.id', read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    verifiedAt = serializers.DateTimeField(source='verified_at', read_only=True, allow_null=True)

    class Meta:
        model = DepositRequest
        fields = [
            'id', 'userId', 'userPhone', 'userName', 'amount', 'status',
            'reference_id', 'description', 'verifiedAt', 'verifiedById', 'verifiedByName',
            'transactionId', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'status', 'createdAt', 'updatedAt', 'verifiedAt', 'verifiedById', 'transactionId']

    def get_userName(self, obj):
        """Get user's full name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.phone_number
        return None

    def get_verifiedByName(self, obj):
        """Get verifier's full name."""
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}".strip() or obj.verified_by.phone_number
        return None


class DepositRequestCreateSerializer(serializers.Serializer):
    """Request serializer for creating deposit request."""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1, required=True, help_text='Amount to deposit in Rials')
    reference_id = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text='Bank receipt or reference number (optional)')


class DepositRequestSearchSerializer(serializers.Serializer):
    """Request serializer for deposit request search (admin endpoint)."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.CharField(required=False, allow_blank=True, help_text='Filter by status: pending, approved, rejected, cancelled')


class DepositApproveSerializer(serializers.Serializer):
    """Request serializer for approving deposit request."""
    reference_id = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text='Bank receipt or reference number (optional)')


class DepositRejectSerializer(serializers.Serializer):
    """Request serializer for rejecting deposit request."""
    description = serializers.CharField(required=False, allow_blank=True, help_text='Reason for rejection (optional)')


class ManagerPaymentRecordSerializer(serializers.Serializer):
    """Serializer for manager to record manual payment (credit/debit) for any user."""
    userId = serializers.UUIDField(required=True, help_text='Target user UUID (customer or driver)')
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True, help_text='Amount in currency units')
    transactionType = serializers.ChoiceField(choices=['credit', 'debit'], help_text='credit or debit')
    description = serializers.CharField(required=False, allow_blank=True, help_text='Optional description/reference')