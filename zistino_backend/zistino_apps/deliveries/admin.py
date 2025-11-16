from django.contrib import admin
from .models import Delivery, Trip, LocationUpdate, WeightShortfall, SurveyQuestion, SurveyAnswer, DeliverySurvey, DeliveryItem


class LocationUpdateInline(admin.TabularInline):
    """Inline for LocationUpdates in Trip admin"""
    model = LocationUpdate
    extra = 0
    readonly_fields = ('id', 'created_at')
    fields = ('latitude', 'longitude', 'speed', 'heading', 'altitude', 
              'satellites', 'hdop', 'gsm_signal', 'odometer', 'created_at')
    can_delete = False


class DeliveryItemInline(admin.TabularInline):
    """Inline for DeliveryItems in Delivery admin"""
    model = DeliveryItem
    extra = 1
    readonly_fields = ('id', 'created_at')
    fields = ('category', 'weight', 'created_at')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Admin for deliveries"""
    list_display = (
        'id', 'driver', 'order', 'status', 'customer_confirmation_status',
        'delivery_date', 'reminder_sms_sent', 'address', 'created_at'
    )
    list_filter = (
        'status', 'customer_confirmation_status', 'delivery_date',
        'reminder_sms_sent', 'created_at'
    )
    search_fields = ('id', 'driver__phone_number', 'driver__username', 
                     'order__id', 'address', 'phone_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('driver',)  # User field - searchable by phone number
    raw_id_fields = ('order',)  # Order field - keep as raw_id since Order admin has search_fields
    ordering = ('-created_at',)
    inlines = [DeliveryItemInline]  # Show delivery items inline
    
    fieldsets = (
        ('Delivery Information', {
            'fields': ('driver', 'order', 'status')
        }),
        ('Location', {
            'fields': ('address', 'phone_number', 'latitude', 'longitude')
        }),
        ('Details', {
            'fields': (
                'delivery_date', 'reminder_sms_sent', 'description',
                'license_plate_number', 'delivered_weight'
            )
        }),
        ('Customer Confirmation', {
            'fields': ('customer_confirmation_status', 'confirmed_at', 'denial_reason', 'cancel_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin for driver trips"""
    list_display = ('id', 'user', 'start_location_id', 'end_location_id', 
                   'distance', 'duration', 'average_speed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__phone_number', 'user__username', 'id')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user',)  # Better UI - shows searchable dropdown by phone number
    ordering = ('-created_at',)
    inlines = [LocationUpdateInline]
    
    # Add search_fields so Trip can be searched in autocomplete (for LocationUpdate)
    def get_search_fields(self, request):
        """Enable autocomplete search for Trip."""
        return ['id', 'user__phone_number', 'user__username']
    
    def save_formset(self, request, form, formset, change):
        """Ensure inline LocationUpdates inherit the Trip's user to avoid NULL user_id."""
        instances = formset.save(commit=False)
        parent_trip = form.instance
        for instance in instances:
            if isinstance(instance, LocationUpdate) and not instance.user_id:
                instance.user = parent_trip.user
            instance.save()
        formset.save_m2m()

    fieldsets = (
        ('Trip Information', {
            'fields': ('user', 'start_location_id', 'end_location_id')
        }),
        ('Statistics', {
            'fields': ('distance', 'duration', 'max_speed', 'average_speed', 'average_altitude')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    """Admin for location updates"""
    list_display = ('id', 'user', 'trip', 'latitude', 'longitude', 'speed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__phone_number', 'user__username', 'trip__id')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user', 'trip')  # Better UI - shows searchable dropdown by phone number and trip info
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Location Information', {
            'fields': ('user', 'trip', 'latitude', 'longitude', 'speed', 'heading')
        }),
        ('GPS Details', {
            'fields': ('altitude', 'satellites', 'hdop', 'gsm_signal', 'odometer')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(WeightShortfall)
class WeightShortfallAdmin(admin.ModelAdmin):
    """Admin for weight shortfalls"""
    list_display = ('id', 'user', 'estimated_range', 'minimum_weight', 'delivered_weight', 'shortfall_amount', 'is_deducted', 'created_at')
    list_filter = ('is_deducted', 'estimated_range', 'created_at')
    search_fields = ('user__phone_number', 'user__username', 'delivery__id', 'estimated_range')
    readonly_fields = ('id', 'created_at', 'deducted_at')
    autocomplete_fields = ('user', 'delivery', 'deducted_from_delivery')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user',)
        }),
        ('Shortfall Details', {
            'fields': ('delivery', 'estimated_range', 'minimum_weight', 'delivered_weight', 'shortfall_amount')
        }),
        ('Deduction Status', {
            'fields': ('is_deducted', 'deducted_from_delivery', 'deducted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


class SurveyAnswerInline(admin.TabularInline):
    """Inline for SurveyAnswers in DeliverySurvey admin"""
    model = SurveyAnswer
    extra = 0
    readonly_fields = ('id', 'created_at')
    fields = ('question', 'answer_value', 'created_at')
    can_delete = False


@admin.register(DeliverySurvey)
class DeliverySurveyAdmin(admin.ModelAdmin):
    """Admin for delivery surveys"""
    list_display = ('id', 'delivery', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('delivery__id', 'user__phone_number', 'user__username', 'comment')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('user', 'delivery')
    inlines = [SurveyAnswerInline]
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Survey Information', {
            'fields': ('delivery', 'user', 'rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """Admin for survey questions"""
    list_display = ('id', 'question_text', 'question_type', 'is_active', 'is_required', 'order', 'created_at')
    list_filter = ('question_type', 'is_active', 'is_required', 'created_at')
    search_fields = ('question_text',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('order', 'created_at')
    
    fieldsets = (
        ('Question Information', {
            'fields': ('question_text', 'question_type', 'options', 'is_active', 'is_required', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    """Admin for survey answers"""
    list_display = ('id', 'survey', 'question', 'answer_value', 'created_at')
    list_filter = ('question', 'created_at')
    search_fields = ('survey__delivery__id', 'question__question_text', 'answer_value')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('survey', 'question')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('survey', 'question', 'answer_value')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(DeliveryItem)
class DeliveryItemAdmin(admin.ModelAdmin):
    """Admin for delivery items (per-category weights)"""
    list_display = ('id', 'delivery', 'category', 'weight', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('delivery__id', 'category__name')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('delivery', 'category')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Delivery Item Information', {
            'fields': ('delivery', 'category', 'weight')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

