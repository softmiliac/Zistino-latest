"""
Models for RepairRequests compatibility layer.
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class RepairRequest(models.Model):
    """Repair Request model matching old Swagger format."""
    GENDER_CHOICES = [
        (0, 'Not Specified'),
        (1, 'Male'),
        (2, 'Female'),
    ]
    
    USER_TYPE_CHOICES = [
        (0, 'Individual'),
        (1, 'Company'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        (0, 'Standard'),
        (1, 'Urgent'),
        (2, 'Emergency'),
    ]
    
    DELIVERY_MODE_CHOICES = [
        (0, 'Pickup'),
        (1, 'Delivery'),
        (2, 'On-Site'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='repair_requests')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='repair_requests')
    
    # Request details
    duration = models.IntegerField(default=0, help_text='Estimated duration in minutes')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text='Total price')
    tracking_code = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text='Tracking code for the repair request')
    steps = models.IntegerField(default=0, help_text='Number of steps')
    delivery_information = models.TextField(blank=True, null=True, help_text='Delivery information')
    note = models.TextField(blank=True, null=True, help_text='Additional notes')
    
    # User information
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    address = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Company information
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Request metadata
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=0)
    request_type = models.IntegerField(choices=REQUEST_TYPE_CHOICES, default=0)
    delivery_mode = models.IntegerField(choices=DELIVERY_MODE_CHOICES, default=0)
    delivery_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_archived = models.BooleanField(default=False, help_text='Whether the repair request is archived')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'repair_requests'
        verbose_name = 'Repair Request'
        verbose_name_plural = 'Repair Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Repair Request {self.id} - {self.full_name or self.user}"


class RepairRequestDetail(models.Model):
    """Repair Request Detail model for nested repair request details."""
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='repair_request_details')
    problem = models.ForeignKey('products.Problem', on_delete=models.SET_NULL, null=True, blank=True, related_name='repair_request_details')
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text='Price for this detail')
    start_repair_date = models.DateTimeField(blank=True, null=True, help_text='Start repair date')
    end_repair_date = models.DateTimeField(blank=True, null=True, help_text='End repair date')
    is_canceled = models.BooleanField(default=False, help_text='Whether this detail is canceled')
    cancelation_description = models.TextField(blank=True, null=True, help_text='Cancellation description')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'repair_request_details'
        verbose_name = 'Repair Request Detail'
        verbose_name_plural = 'Repair Request Details'
        ordering = ['created_at']

    def __str__(self):
        return f"Repair Request Detail {self.id} - Request {self.repair_request.id}"


class RepairRequestStatus(models.Model):
    """Repair Request Status model for tracking status changes."""
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'In Progress'),
        (2, 'Completed'),
        (3, 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='repair_request_statuses')
    text = models.TextField(blank=True, null=True, help_text='Status text/description')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, help_text='Status code')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'repair_request_statuses'
        verbose_name = 'Repair Request Status'
        verbose_name_plural = 'Repair Request Statuses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Status {self.status} for Request {self.repair_request.id}"


class RepairRequestDocument(models.Model):
    """Repair Request Document model for storing documents related to repair requests."""
    id = models.AutoField(primary_key=True)
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='repair_request_documents')
    document = models.FileField(upload_to='repair_requests/documents/', blank=True, null=True, help_text='Document file')
    document_url = models.CharField(max_length=500, blank=True, null=True, help_text='Document URL if stored externally')
    description = models.TextField(blank=True, null=True, help_text='Document description')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'repair_request_documents'
        verbose_name = 'Repair Request Document'
        verbose_name_plural = 'Repair Request Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Document {self.id} for Request {self.repair_request.id}"


class RepairRequestMessage(models.Model):
    """Repair Request Message model for storing messages related to repair requests."""
    TYPE_CHOICES = [
        (0, 'User Message'),
        (1, 'Admin Message'),
        (2, 'System Message'),
    ]
    
    id = models.AutoField(primary_key=True)
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='repair_request_messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='repair_request_messages')
    message = models.TextField(help_text='Message content')
    type = models.IntegerField(choices=TYPE_CHOICES, default=0, help_text='Message type')
    is_admin = models.BooleanField(default=False, help_text='Whether message is from admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'repair_request_messages'
        verbose_name = 'Repair Request Message'
        verbose_name_plural = 'Repair Request Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message {self.id} for Request {self.repair_request.id}"
