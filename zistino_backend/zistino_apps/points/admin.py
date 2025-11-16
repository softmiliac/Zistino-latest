from django.contrib import admin
from .models import (
    UserPoints, PointTransaction, ReferralCode, Referral,
    Lottery, LotteryTicket
)


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    """Admin for UserPoints model."""
    list_display = ('id', 'user', 'user_phone', 'balance', 'lifetime_earned', 'lifetime_spent', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__phone_number', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('user',)
    
    def user_phone(self, obj):
        """Display user phone number."""
        return obj.user.phone_number if obj.user else '-'
    user_phone.short_description = 'Phone Number'


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """Admin for PointTransaction model."""
    list_display = ('id', 'user_phone', 'amount', 'transaction_type', 'source', 'reference_id', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'source', 'created_at')
    search_fields = ('user__phone_number', 'description', 'reference_id', 'id')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user',)
    
    def user_phone(self, obj):
        """Display user phone number."""
        return obj.user.phone_number if obj.user else '-'
    user_phone.short_description = 'Phone Number'


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    """Admin for ReferralCode model."""
    list_display = ('id', 'user', 'user_phone', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('code', 'user__phone_number', 'user__username')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user',)
    
    def user_phone(self, obj):
        """Display user phone number."""
        return obj.user.phone_number if obj.user else '-'
    user_phone.short_description = 'Phone Number'
    
    def save_model(self, request, obj, form, change):
        """Auto-generate code if not provided and object is new."""
        if not change:  # Creating new object
            if not obj.code or obj.code.strip() == '':
                obj.code = ReferralCode._generate_code()
        super().save_model(request, obj, form, change)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    """Admin for Referral model."""
    list_display = ('id', 'referrer_phone', 'referred_phone', 'referral_code', 'status', 'referrer_points_awarded', 'completed_at', 'created_at')
    list_filter = ('status', 'referrer_points_awarded', 'referred_bonus_awarded', 'created_at', 'completed_at')
    search_fields = ('referrer__phone_number', 'referred__phone_number', 'referral_code', 'id')
    readonly_fields = ('id', 'created_at', 'completed_at')
    autocomplete_fields = ('referrer', 'referred')
    
    fieldsets = (
        ('Referral Relationship', {
            'fields': ('referrer', 'referred', 'referral_code'),
            'description': 'Referrer: User who shared referral code (gets points). Referred: New user who used the code. Referral Code: Code used during registration.'
        }),
        ('Status & Points', {
            'fields': ('status', 'referrer_points_awarded', 'referred_bonus_awarded', 'completed_at'),
            'description': 'Status: pending (waiting for first order), completed (first order done), awarded (points given). Points are awarded when referred user completes first order.'
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at')
        }),
    )
    
    def referrer_phone(self, obj):
        """Display referrer phone number."""
        return obj.referrer.phone_number if obj.referrer else '-'
    referrer_phone.short_description = 'Referrer Phone'
    
    def referred_phone(self, obj):
        """Display referred user phone number."""
        return obj.referred.phone_number if obj.referred else '-'
    referred_phone.short_description = 'Referred Phone'


@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    """Admin for Lottery model."""
    list_display = ('id', 'title', 'prize_name', 'status', 'ticket_price_points', 'total_tickets_display', 'total_participants_display', 'winner_phone', 'created_at')
    list_filter = ('status', 'created_at', 'drawn_at')
    search_fields = ('title', 'prize_name', 'description', 'id')
    readonly_fields = ('id', 'total_tickets', 'total_participants', 'created_at', 'updated_at', 'drawn_at')
    autocomplete_fields = ('winner', 'created_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'prize_name', 'prize_image', 'ticket_price_points')
        }),
        ('Status & Dates', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Winner', {
            'fields': ('winner', 'winner_ticket_id', 'drawn_at')
        }),
        ('Statistics', {
            'fields': ('total_tickets', 'total_participants')
        }),
        ('Metadata', {
            'fields': ('created_by', 'id', 'created_at', 'updated_at')
        }),
    )
    
    def total_tickets_display(self, obj):
        """Display total tickets."""
        return obj.total_tickets
    total_tickets_display.short_description = 'Total Tickets'
    
    def total_participants_display(self, obj):
        """Display total participants."""
        return obj.total_participants
    total_participants_display.short_description = 'Participants'
    
    def winner_phone(self, obj):
        """Display winner phone number."""
        return obj.winner.phone_number if obj.winner else '-'
    winner_phone.short_description = 'Winner Phone'


@admin.register(LotteryTicket)
class LotteryTicketAdmin(admin.ModelAdmin):
    """Admin for LotteryTicket model."""
    list_display = ('id', 'lottery_title', 'user_phone', 'ticket_count', 'points_spent', 'is_winner', 'purchase_date')
    list_filter = ('is_winner', 'purchase_date', 'lottery__status')
    search_fields = ('user__phone_number', 'lottery__title', 'lottery__prize_name', 'id')
    readonly_fields = ('id', 'purchase_date')
    autocomplete_fields = ('lottery', 'user')
    
    def lottery_title(self, obj):
        """Display lottery title."""
        return obj.lottery.title if obj.lottery else '-'
    lottery_title.short_description = 'Lottery'
    
    def user_phone(self, obj):
        """Display user phone number."""
        return obj.user.phone_number if obj.user else '-'
    user_phone.short_description = 'User Phone'

