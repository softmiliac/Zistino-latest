from rest_framework import serializers
from .models import (
    UserPoints, PointTransaction, ReferralCode, Referral,
    Lottery, LotteryTicket
)


class UserPointsSerializer(serializers.ModelSerializer):
    """Serializer for UserPoints model."""
    userId = serializers.UUIDField(source='user.id', read_only=True)
    userPhone = serializers.CharField(source='user.phone_number', read_only=True)
    userName = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    lifetimeEarned = serializers.IntegerField(source='lifetime_earned', read_only=True)
    lifetimeSpent = serializers.IntegerField(source='lifetime_spent', read_only=True)

    class Meta:
        model = UserPoints
        fields = [
            'id', 'userId', 'userPhone', 'userName', 'balance',
            'lifetimeEarned', 'lifetimeSpent', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']

    def get_userName(self, obj):
        """Get user's full name."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.phone_number
        return None


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointTransaction model."""
    userId = serializers.UUIDField(source='user.id', read_only=True)
    userPhone = serializers.CharField(source='user.phone_number', read_only=True)
    transactionType = serializers.CharField(source='transaction_type', read_only=True)
    referenceId = serializers.CharField(source='reference_id', allow_blank=True, required=False)
    balanceAfter = serializers.IntegerField(source='balance_after', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = PointTransaction
        fields = [
            'id', 'userId', 'userPhone', 'amount', 'transactionType',
            'source', 'referenceId', 'description', 'balanceAfter', 'createdAt'
        ]
        read_only_fields = ['id', 'createdAt']


class ReferralCodeSerializer(serializers.ModelSerializer):
    """Serializer for ReferralCode model."""
    userId = serializers.UUIDField(source='user.id', read_only=True)
    userPhone = serializers.CharField(source='user.phone_number', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = ReferralCode
        fields = ['id', 'userId', 'userPhone', 'code', 'createdAt']
        read_only_fields = ['id', 'code', 'createdAt']


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for Referral model."""
    referrerId = serializers.UUIDField(source='referrer.id', read_only=True)
    referrerPhone = serializers.CharField(source='referrer.phone_number', read_only=True)
    referrerName = serializers.SerializerMethodField()
    referredId = serializers.UUIDField(source='referred.id', read_only=True)
    referredPhone = serializers.CharField(source='referred.phone_number', read_only=True)
    referredName = serializers.SerializerMethodField()
    referrerPointsAwarded = serializers.BooleanField(source='referrer_points_awarded', read_only=True)
    referredBonusAwarded = serializers.BooleanField(source='referred_bonus_awarded', read_only=True)
    completedAt = serializers.DateTimeField(source='completed_at', read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Referral
        fields = [
            'id', 'referrerId', 'referrerPhone', 'referrerName',
            'referredId', 'referredPhone', 'referredName', 'referral_code',
            'status', 'referrerPointsAwarded', 'referredBonusAwarded',
            'completedAt', 'createdAt'
        ]
        read_only_fields = ['id', 'createdAt', 'completedAt']

    def get_referrerName(self, obj):
        """Get referrer's full name."""
        if obj.referrer:
            return f"{obj.referrer.first_name} {obj.referrer.last_name}".strip() or obj.referrer.phone_number
        return None

    def get_referredName(self, obj):
        """Get referred user's full name."""
        if obj.referred:
            return f"{obj.referred.first_name} {obj.referred.last_name}".strip() or obj.referred.phone_number
        return None


class LotterySerializer(serializers.ModelSerializer):
    """Serializer for Lottery model."""
    prizeName = serializers.CharField(source='prize_name')
    prizeImage = serializers.CharField(source='prize_image', allow_blank=True, required=False)
    ticketPricePoints = serializers.IntegerField(source='ticket_price_points')
    startDate = serializers.DateTimeField(source='start_date')
    endDate = serializers.DateTimeField(source='end_date')
    winnerId = serializers.UUIDField(source='winner.id', read_only=True, allow_null=True)
    winnerName = serializers.SerializerMethodField()
    winnerTicketId = serializers.UUIDField(source='winner_ticket_id', read_only=True, allow_null=True)
    drawnAt = serializers.DateTimeField(source='drawn_at', read_only=True, allow_null=True)
    createdById = serializers.UUIDField(source='created_by.id', read_only=True, allow_null=True)
    totalTickets = serializers.IntegerField(read_only=True)
    totalParticipants = serializers.IntegerField(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Lottery
        fields = [
            'id', 'title', 'description', 'prizeName', 'prizeImage',
            'ticketPricePoints', 'status', 'startDate', 'endDate',
            'winnerId', 'winnerName', 'winnerTicketId', 'drawnAt',
            'createdById', 'totalTickets', 'totalParticipants',
            'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'totalTickets', 'totalParticipants', 'createdAt', 'updatedAt', 'drawnAt']

    def get_winnerName(self, obj):
        """Get winner's full name."""
        if obj.winner:
            return f"{obj.winner.first_name} {obj.winner.last_name}".strip() or obj.winner.phone_number
        return None


class LotteryTicketSerializer(serializers.ModelSerializer):
    """Serializer for LotteryTicket model."""
    lotteryId = serializers.UUIDField(source='lottery.id', read_only=True)
    lotteryTitle = serializers.CharField(source='lottery.title', read_only=True)
    lotteryPrizeName = serializers.CharField(source='lottery.prize_name', read_only=True)
    userId = serializers.UUIDField(source='user.id', read_only=True)
    userPhone = serializers.CharField(source='user.phone_number', read_only=True)
    ticketCount = serializers.IntegerField(source='ticket_count')
    pointsSpent = serializers.IntegerField(source='points_spent')
    purchaseDate = serializers.DateTimeField(source='purchase_date', read_only=True)
    isWinner = serializers.BooleanField(source='is_winner', read_only=True)

    class Meta:
        model = LotteryTicket
        fields = [
            'id', 'lotteryId', 'lotteryTitle', 'lotteryPrizeName',
            'userId', 'userPhone', 'ticketCount', 'pointsSpent',
            'purchaseDate', 'isWinner'
        ]
        read_only_fields = ['id', 'purchaseDate', 'isWinner']


# Request serializers
class BuyTicketsSerializer(serializers.Serializer):
    """Request serializer for buying lottery tickets."""
    ticket_count = serializers.IntegerField(required=True, min_value=1, help_text='Number of tickets to buy')


class ReferralCodeRequestSerializer(serializers.Serializer):
    """Request serializer for using referral code during registration."""
    referral_code = serializers.CharField(required=True, max_length=20, help_text='Referral code to use')


class LotterySearchRequestSerializer(serializers.Serializer):
    """Request serializer for lottery search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    status = serializers.CharField(required=False, allow_blank=True, help_text='Filter by status: draft, active, ended, drawn, cancelled')


class PointTransactionSearchRequestSerializer(serializers.Serializer):
    """Request serializer for point transaction search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    source = serializers.CharField(required=False, allow_blank=True, help_text='Filter by source: order, referral, lottery, manual')


class ReferralSearchRequestSerializer(serializers.Serializer):
    """Request serializer for referral search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.CharField(required=False, allow_blank=True, help_text='Filter by status: pending, completed, awarded')


class DrawWinnerSerializer(serializers.Serializer):
    """Request serializer for drawing lottery winner."""
    method = serializers.ChoiceField(
        choices=['random', 'manual'],
        required=False,
        default='random',
        help_text='Draw method: random (automatic) or manual (admin selects)'
    )
    winner_ticket_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text='Ticket ID if method is manual (required for manual)'
    )

