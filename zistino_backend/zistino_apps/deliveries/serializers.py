from rest_framework import serializers
from .models import Delivery, Trip, LocationUpdate, DeliverySurvey, DeliveryItem, WeightShortfall, SurveyQuestion, SurveyAnswer
from zistino_apps.products.models import Category
from django.utils import timezone
from datetime import datetime


class DeliverySerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    order_id = serializers.CharField(source='order.id', read_only=True)
    time_slot_formatted = serializers.SerializerMethodField()
    navigation_url = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = [
            'id', 'driver', 'driver_name', 'order', 'order_id', 'status',
            'latitude', 'longitude', 'address', 'phone_number', 'delivery_date',
            'time_slot_formatted', 'navigation_url',
            'delivered_weight', 'reminder_sms_sent', 'description',
            'license_plate_number', 'customer_confirmation_status', 'denial_reason', 'confirmed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'driver', 'created_at', 'updated_at']

    def get_time_slot_formatted(self, obj):
        """Format delivery_date as time slot string (e.g., '8 AM to 12 PM')."""
        if not obj.delivery_date:
            return None
        
        try:
            from zistino_apps.configurations.models import Configuration
            
            # Get delivery time configuration
            config = Configuration.objects.filter(
                name__icontains='delivery_time',
                is_active=True
            ).first()
            
            # Default values if config not found
            start_hour_default = 8
            end_hour_default = 20
            split_default = 4
            
            if config and config.value:
                start_hour_default = int(config.value.get('start', 8))
                end_hour_default = int(config.value.get('end', 20))
                split_default = int(config.value.get('split', 4))
        except Exception:
            # Fallback to defaults if any error
            start_hour_default = 8
            end_hour_default = 20
            split_default = 4
        
        delivery_time = obj.delivery_date
        hour = delivery_time.hour
        
        # Calculate time slot based on configuration
        # Generate slots: e.g., 8-12, 12-16, 16-20 if split=4
        slots = []
        current = start_hour_default
        while current < end_hour_default:
            slot_end = min(current + split_default, end_hour_default)
            slots.append((current, slot_end))
            current = slot_end
        
        # Find which slot the delivery hour belongs to
        start_hour = start_hour_default
        end_hour = end_hour_default
        
        for slot_start, slot_end in slots:
            if slot_start <= hour < slot_end:
                start_hour = slot_start
                end_hour = slot_end
                break
        
        # Format hours (AM/PM)
        def format_hour(h):
            if h == 0:
                return "12 AM"
            elif h < 12:
                return f"{h} AM"
            elif h == 12:
                return "12 PM"
            else:
                return f"{h - 12} PM"
        
        start_str = format_hour(start_hour)
        end_str = format_hour(end_hour)
        
        return f"{start_str} to {end_str}"

    def get_navigation_url(self, obj):
        """Generate Google Maps navigation URL from latitude/longitude."""
        if not obj.latitude or not obj.longitude:
            return None
        
        # Generate Google Maps navigation URL
        # Format: https://www.google.com/maps/dir/?api=1&destination=lat,lng
        lat = float(obj.latitude)
        lng = float(obj.longitude)
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            'id', 'user', 'start_location_id', 'end_location_id', 'distance', 'duration',
            'max_speed', 'average_speed', 'average_altitude', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = [
            'id', 'user', 'trip', 'latitude', 'longitude', 'speed', 'heading', 'altitude',
            'satellites', 'hdop', 'gsm_signal', 'odometer', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class DeliveryFollowupRequestSerializer(serializers.Serializer):
    """Serializer for delivery followup request - matches DriverDeliveryModel fields."""
    id = serializers.IntegerField(required=False, allow_null=True)
    # Order ID can be UUID (string) or integer - accept both
    orderId = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='order_id')
    deliveryDate = serializers.DateTimeField(required=False, allow_null=True, source='delivery_date')
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.IntegerField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        fields = ['id', 'orderId', 'deliveryDate', 'description', 'status', 'latitude', 'longitude']


class DeliverySearchRequestSerializer(serializers.Serializer):
    """Request serializer for admin delivery search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.IntegerField(required=False, allow_null=True, help_text='Filter by delivery status (optional)')


class DeliveryTransferRequestSerializer(serializers.Serializer):
    """Request serializer for transferring delivery to another driver."""
    driverId = serializers.CharField(required=True, help_text='New driver UUID')


class DeliveryDenyRequestSerializer(serializers.Serializer):
    """Request serializer for customer to deny delivery with reason."""
    denial_reason = serializers.CharField(required=True, help_text='Reason for denying the delivery (required when denying)')


class SurveyAnswerSerializer(serializers.ModelSerializer):
    """Serializer for survey answers."""
    questionId = serializers.UUIDField(source='question.id', read_only=True)
    questionText = serializers.CharField(source='question.question_text', read_only=True)
    questionType = serializers.CharField(source='question.question_type', read_only=True)
    answerValue = serializers.CharField(source='answer_value', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = SurveyAnswer
        fields = ['id', 'questionId', 'questionText', 'questionType', 'answerValue', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class DeliverySurveySerializer(serializers.ModelSerializer):
    """Serializer for delivery survey/feedback."""
    delivery_id = serializers.UUIDField(source='delivery.id', read_only=True)
    driver_id = serializers.UUIDField(source='delivery.driver.id', read_only=True)
    driver_phone = serializers.CharField(source='delivery.driver.phone_number', read_only=True)
    answers = SurveyAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = DeliverySurvey
        fields = ['id', 'delivery_id', 'driver_id', 'driver_phone', 'rating', 'comment', 'answers', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SurveyAnswerRequestSerializer(serializers.Serializer):
    """Request serializer for a single survey answer."""
    questionId = serializers.UUIDField(required=True, help_text='ID of the survey question')
    answerValue = serializers.CharField(required=True, help_text='Answer value (text, rating number, yes/no, etc.)')


class DeliverySurveyRequestSerializer(serializers.Serializer):
    """Request serializer for submitting delivery survey."""
    rating = serializers.IntegerField(required=True, min_value=1, max_value=5, help_text='Rating from 1 to 5 (1=worst, 5=best)')
    comment = serializers.CharField(required=False, allow_blank=True, help_text='Optional comment/feedback')
    answers = SurveyAnswerRequestSerializer(required=False, many=True, help_text='Answers to survey questions')


class DeliveryLicensePlateRequestSerializer(serializers.Serializer):
    """Request serializer for driver to set license plate number."""
    license_plate_number = serializers.CharField(required=True, max_length=20, help_text='License plate number of the delivery vehicle')


class DeliveryNonDeliveryRequestSerializer(serializers.Serializer):
    """Request serializer for driver to record non-delivery with reason."""
    reason = serializers.CharField(required=True, help_text='Reason for non-delivery (e.g., customer unavailable, wrong address)')


class DeliveryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.UUIDField(source='category.id', read_only=True)

    class Meta:
        model = DeliveryItem
        fields = ['id', 'delivery', 'category_id', 'category_name', 'weight', 'created_at', 'updated_at']
        read_only_fields = ['id', 'delivery', 'category_id', 'category_name', 'created_at', 'updated_at']


class DeliveryItemUpsertSerializer(serializers.Serializer):
    """Upsert a single delivery item by category id and weight."""
    categoryId = serializers.UUIDField(required=True, help_text='Category UUID')
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text='Weight in kg')


class DeliveryItemsBulkRequestSerializer(serializers.Serializer):
    """Bulk set all items for a delivery (replaces existing)."""
    items = DeliveryItemUpsertSerializer(many=True, required=True)


class ManagerTelephoneRequestItemSerializer(serializers.Serializer):
    productName = serializers.CharField(required=True, help_text='Waste item name/category label')
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text='Weight in kg')
    quantity = serializers.IntegerField(required=False, min_value=1, default=1)


class WeightShortfallSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(source='user.id', read_only=True)
    userPhone = serializers.CharField(source='user.phone_number', read_only=True)
    deliveryId = serializers.UUIDField(source='delivery.id', read_only=True, allow_null=True)
    deductedFromDeliveryId = serializers.UUIDField(source='deducted_from_delivery.id', read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    deductedAt = serializers.DateTimeField(source='deducted_at', read_only=True, allow_null=True)
    shortfallAmount = serializers.SerializerMethodField()
    
    class Meta:
        model = WeightShortfall
        fields = [
            'id', 'userId', 'userPhone', 'deliveryId', 'estimated_range',
            'minimum_weight', 'delivered_weight', 'shortfallAmount',
            'is_deducted', 'deductedFromDeliveryId', 'createdAt', 'deductedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'deductedAt']
    
    def get_shortfallAmount(self, obj):
        """Return shortfall amount as formatted string."""
        return f"{obj.shortfall_amount:.2f}"


class WeightRangeMinimumConfigSerializer(serializers.Serializer):
    """Serializer for configuring minimum weights per weight range."""
    ranges = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text='List of weight ranges with minimum weights. Example: [{"value": "2-5", "min": 2}, {"value": "5-10", "min": 5}]'
    )


class ManagerTelephoneRequestSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(required=True, help_text='Customer phone number')
    fullName = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    preferredDeliveryDate = serializers.DateTimeField(required=False, allow_null=True)
    createDelivery = serializers.BooleanField(required=False, default=True)
    items = ManagerTelephoneRequestItemSerializer(many=True, required=False)


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """Serializer for survey questions."""
    questionId = serializers.UUIDField(source='id', read_only=True)
    questionText = serializers.CharField(source='question_text')
    questionType = serializers.CharField(source='question_type')
    isActive = serializers.BooleanField(source='is_active')
    isRequired = serializers.BooleanField(source='is_required')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = SurveyQuestion
        fields = ['questionId', 'questionText', 'questionType', 'options', 'isActive', 'isRequired', 'order', 'createdAt', 'updatedAt']
        read_only_fields = ['questionId', 'createdAt', 'updatedAt']


class SurveyQuestionCreateSerializer(serializers.Serializer):
    """Request serializer for creating a survey question."""
    questionText = serializers.CharField(required=True, max_length=500, help_text='Question text displayed to customer')
    questionType = serializers.ChoiceField(required=True, choices=[('rating', 'Rating (1-5)'), ('text', 'Text Answer'), ('yes_no', 'Yes/No'), ('multiple_choice', 'Multiple Choice')], help_text='Type of question: rating, text, yes_no, multiple_choice')
    options = serializers.ListField(required=False, allow_null=True, child=serializers.CharField(), help_text='Options for multiple choice questions (JSON array)')
    isActive = serializers.BooleanField(required=False, default=True, help_text='Whether this question is currently active')
    isRequired = serializers.BooleanField(required=False, default=False, help_text='Whether this question is required')
    order = serializers.IntegerField(required=False, default=0, help_text='Display order (lower numbers appear first)')


class SurveyQuestionUpdateSerializer(serializers.Serializer):
    """Request serializer for updating a survey question."""
    questionText = serializers.CharField(required=False, max_length=500, help_text='Question text displayed to customer')
    questionType = serializers.ChoiceField(required=False, choices=[('rating', 'Rating (1-5)'), ('text', 'Text Answer'), ('yes_no', 'Yes/No'), ('multiple_choice', 'Multiple Choice')], help_text='Type of question')
    options = serializers.ListField(required=False, allow_null=True, child=serializers.CharField(), help_text='Options for multiple choice questions')
    isActive = serializers.BooleanField(required=False, help_text='Whether this question is currently active')
    isRequired = serializers.BooleanField(required=False, help_text='Whether this question is required')
    order = serializers.IntegerField(required=False, help_text='Display order')


class ManagerDriverSatisfactionRequestSerializer(serializers.Serializer):
    """Request serializer for manager to view driver satisfaction."""
    driverId = serializers.UUIDField(required=False, allow_null=True, help_text='Filter by specific driver ID (optional)')
    startDate = serializers.DateField(required=False, allow_null=True, help_text='Start date for filtering (YYYY-MM-DD)')
    endDate = serializers.DateField(required=False, allow_null=True, help_text='End date for filtering (YYYY-MM-DD)')
    pageNumber = serializers.IntegerField(required=False, default=1, min_value=1, help_text='Page number (1-indexed)')
    pageSize = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100, help_text='Number of items per page')