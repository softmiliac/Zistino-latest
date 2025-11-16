from django.db import models
from django.contrib.auth import get_user_model
from zistino_apps.orders.models import Order
from zistino_apps.products.models import Category
import uuid

User = get_user_model()


class Delivery(models.Model):
    """Delivery model for driver assignments"""
    DELIVERY_STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CUSTOMER_CONFIRMATION_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('denied', 'Denied'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='assigned')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    delivery_date = models.DateTimeField(blank=True, null=True)
    delivered_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, help_text='Total weight actually collected/delivered in kg')
    reminder_sms_sent = models.BooleanField(default=False, blank=True, help_text='Whether reminder SMS has been sent 1 hour before delivery')
    description = models.TextField(blank=True)
    # New fields for customer confirmation feature
    license_plate_number = models.CharField(max_length=20, blank=True, null=True, help_text='License plate number of the delivery vehicle (entered by driver when completing delivery)')
    customer_confirmation_status = models.CharField(max_length=20, choices=CUSTOMER_CONFIRMATION_CHOICES, default='pending', help_text='Customer confirmation status: pending, confirmed, or denied')
    denial_reason = models.TextField(blank=True, null=True, help_text='Reason provided by customer if delivery is denied')
    cancel_reason = models.TextField(blank=True, null=True, help_text='Reason provided by customer if delivery is cancelled before completion')
    confirmed_at = models.DateTimeField(blank=True, null=True, help_text='Timestamp when customer confirmed the delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deliveries'
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return f"Delivery {self.id} - {self.driver.phone_number}"


class Trip(models.Model):
    """Driver trip session - matches TripRqm fields."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    start_location_id = models.IntegerField(default=0)
    end_location_id = models.IntegerField(default=0)
    distance = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    average_speed = models.IntegerField(default=0)
    average_altitude = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trips'
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        ordering = ['-created_at']

    def __str__(self):
        """Display trip with driver info and date."""
        driver_info = self.user.phone_number if self.user else 'Unknown'
        distance_str = f"{self.distance}km" if self.distance > 0 else "0km"
        date_str = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        return f"Trip #{self.id} - Driver: {driver_info} - {distance_str} ({date_str})"


class LocationUpdate(models.Model):
    """Location samples during trip - matches LocationsRqm fields."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_updates')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.IntegerField(default=0)
    heading = models.CharField(max_length=50, blank=True)
    altitude = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    satellites = models.IntegerField(default=0)
    hdop = models.IntegerField(default=0)
    gsm_signal = models.IntegerField(default=0)
    odometer = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_updates'
        verbose_name = 'Location Update'
        verbose_name_plural = 'Location Updates'


class DeliverySurvey(models.Model):
    """Survey/feedback model for completed deliveries after customer confirmation."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name='survey')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_surveys')
    rating = models.IntegerField(default=5, help_text='Rating from 1 to 5 (1=worst, 5=best)')
    comment = models.TextField(blank=True, help_text='Optional comment/feedback from customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_surveys'
        verbose_name = 'Delivery Survey'
        verbose_name_plural = 'Delivery Surveys'
        ordering = ['-created_at']

    def __str__(self):
        return f"Survey for Delivery {self.delivery.id} - Rating: {self.rating}"


class SurveyQuestion(models.Model):
    """Configurable survey questions for delivery feedback."""
    QUESTION_TYPE_CHOICES = [
        ('rating', 'Rating (1-5)'),
        ('text', 'Text Answer'),
        ('yes_no', 'Yes/No'),
        ('multiple_choice', 'Multiple Choice'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.CharField(max_length=500, help_text='Question text displayed to customer')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='rating', help_text='Type of question')
    options = models.JSONField(blank=True, null=True, help_text='Options for multiple choice questions (JSON array)')
    is_active = models.BooleanField(default=True, help_text='Whether this question is currently active')
    order = models.IntegerField(default=0, help_text='Display order (lower numbers appear first)')
    is_required = models.BooleanField(default=False, help_text='Whether this question is required')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_questions'
        verbose_name = 'Survey Question'
        verbose_name_plural = 'Survey Questions'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.question_text} ({self.question_type})"


class SurveyAnswer(models.Model):
    """Answers to survey questions for a specific delivery survey."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(DeliverySurvey, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_value = models.TextField(help_text='Answer value (text, rating number, yes/no, etc.)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'survey_answers'
        verbose_name = 'Survey Answer'
        verbose_name_plural = 'Survey Answers'
        unique_together = ('survey', 'question')
        ordering = ['question__order', 'created_at']

    def __str__(self):
        return f"Answer to {self.question.question_text}: {self.answer_value}"


class DeliveryItem(models.Model):
    """Per-group/category weight entries recorded by driver for a delivery."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='delivery_items')
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text='Weight in kg for this category in this delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_items'
        verbose_name = 'Delivery Item'
        verbose_name_plural = 'Delivery Items'
        unique_together = ('delivery', 'category')

    def __str__(self):
        return f"DeliveryItem {self.delivery_id} - {self.category.name}: {self.weight} kg"


class WeightShortfall(models.Model):
    """Tracks weight shortfall (negative balance) for customers when delivered weight is less than minimum."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_shortfalls')
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='shortfall', null=True, blank=True, help_text='Delivery that created this shortfall')
    estimated_range = models.CharField(max_length=20, help_text='Weight range selected by customer (e.g., "5-10")')
    minimum_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text='Minimum weight for the selected range in kg')
    delivered_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text='Actual weight delivered in kg')
    shortfall_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Shortfall amount (negative value) in kg')
    deducted_from_delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True, related_name='deducted_shortfalls', help_text='Delivery from which this shortfall was deducted')
    is_deducted = models.BooleanField(default=False, help_text='Whether this shortfall has been deducted from a subsequent delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    deducted_at = models.DateTimeField(null=True, blank=True, help_text='When this shortfall was deducted')

    class Meta:
        db_table = 'weight_shortfalls'
        verbose_name = 'Weight Shortfall'
        verbose_name_plural = 'Weight Shortfalls'
        ordering = ['-created_at']

    def __str__(self):
        return f"WeightShortfall {self.id} - User: {self.user.phone_number}, Amount: {self.shortfall_amount} kg"