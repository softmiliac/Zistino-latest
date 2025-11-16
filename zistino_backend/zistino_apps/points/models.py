from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count
import uuid
import random
import string

User = get_user_model()


class UserPoints(models.Model):
    """User points balance and lifetime tracking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_points')
    balance = models.IntegerField(default=0, help_text='Current available points')
    lifetime_earned = models.IntegerField(default=0, help_text='Total points earned in lifetime')
    lifetime_spent = models.IntegerField(default=0, help_text='Total points spent in lifetime')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_points'
        verbose_name = 'User Points'
        verbose_name_plural = 'User Points'
        ordering = ['-balance']

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance} points"

    def add_points(self, amount, source='manual', description='', reference_id=''):
        """Add points to user balance."""
        self.balance += amount
        self.lifetime_earned += amount
        self.save()
        
        # Create transaction record
        PointTransaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='earned',
            source=source,
            description=description,
            reference_id=reference_id,
            balance_after=self.balance
        )
        return self.balance

    def spend_points(self, amount, source='manual', description='', reference_id=''):
        """Deduct points from user balance."""
        if self.balance < amount:
            raise ValueError('Insufficient points')
        
        self.balance -= amount
        self.lifetime_spent += amount
        self.save()
        
        # Create transaction record
        PointTransaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='spent',
            source=source,
            description=description,
            reference_id=reference_id,
            balance_after=self.balance
        )
        return self.balance


class PointTransaction(models.Model):
    """Track all point transactions (earned and spent)."""
    TRANSACTION_TYPE_CHOICES = [
        ('earned', 'Earned'),
        ('spent', 'Spent'),
    ]
    
    SOURCE_CHOICES = [
        ('order', 'Order'),
        ('referral', 'Referral'),
        ('lottery', 'Lottery'),
        ('manual', 'Manual'),
        ('welcome_bonus', 'Welcome Bonus'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField(help_text='Point amount (positive for earned, represents deduction for spent)')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, help_text='Source of transaction')
    reference_id = models.CharField(max_length=100, blank=True, help_text='Reference to order/referral/lottery ID')
    description = models.TextField(blank=True, help_text='Transaction description')
    balance_after = models.IntegerField(help_text='User balance after this transaction')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'point_transactions'
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.phone_number} - {self.transaction_type} {self.amount} points ({self.source})"


class ReferralCode(models.Model):
    """User referral codes - separate model to avoid modifying User model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_code_obj')
    code = models.CharField(max_length=20, unique=True, help_text='Unique referral code')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referral_codes'
        verbose_name = 'Referral Code'
        verbose_name_plural = 'Referral Codes'

    def __str__(self):
        return f"{self.user.phone_number} - {self.code}"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create referral code for user."""
        code_obj, created = cls.objects.get_or_create(
            user=user,
            defaults={'code': cls._generate_code()}
        )
        return code_obj

    @staticmethod
    def _generate_code():
        """Generate unique referral code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not ReferralCode.objects.filter(code=code).exists():
                return code


class Referral(models.Model):
    """Track referral relationships and bonuses."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('awarded', 'Points Awarded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_given', 
                                help_text='User who gave the referral (the person who shared their referral code). This user will receive points when referred user completes first order.')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_received', 
                                help_text='User who was referred (the person who used the referral code during registration). This is the new user.')
    referral_code = models.CharField(max_length=20, help_text='Referral code that was used during registration (e.g., "ABC12345")')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    referrer_points_awarded = models.BooleanField(default=False, help_text='Whether referrer received points')
    referred_bonus_awarded = models.BooleanField(default=False, help_text='Whether referred user received welcome bonus')
    completed_at = models.DateTimeField(blank=True, null=True, help_text='When referral was completed (first order)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referrals'
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = [['referrer', 'referred']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer.phone_number} → {self.referred.phone_number} ({self.status})"


class Lottery(models.Model):
    """Lottery model for managing lotteries."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('drawn', 'Drawn'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text='Lottery title')
    description = models.TextField(blank=True, help_text='Lottery description')
    prize_name = models.CharField(max_length=255, help_text='Prize name (e.g., Electric Scooter)')
    prize_image = models.CharField(max_length=500, blank=True, help_text='Prize image URL')
    ticket_price_points = models.IntegerField(default=100, help_text='Points required per ticket')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(help_text='Lottery start date')
    end_date = models.DateTimeField(help_text='Lottery end date')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lottery_wins', help_text='Winner user')
    winner_ticket_id = models.UUIDField(null=True, blank=True, help_text='Winning ticket ID')
    drawn_at = models.DateTimeField(blank=True, null=True, help_text='When winner was drawn')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_lotteries', help_text='Admin who created lottery')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lotteries'
        verbose_name = 'Lottery'
        verbose_name_plural = 'Lotteries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.prize_name} ({self.status})"

    @property
    def total_tickets(self):
        """Get total tickets sold for this lottery."""
        return self.lottery_tickets.count()

    @property
    def total_participants(self):
        """Get total unique participants."""
        return self.lottery_tickets.values('user').distinct().count()


class LotteryTicket(models.Model):
    """Lottery tickets purchased by users."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, related_name='lottery_tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lottery_tickets')
    ticket_count = models.IntegerField(default=1, help_text='Number of tickets purchased')
    points_spent = models.IntegerField(help_text='Total points spent for these tickets')
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False, help_text='Whether this ticket won')

    class Meta:
        db_table = 'lottery_tickets'
        verbose_name = 'Lottery Ticket'
        verbose_name_plural = 'Lottery Tickets'
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.user.phone_number} - {self.ticket_count} ticket(s) for {self.lottery.title}"
