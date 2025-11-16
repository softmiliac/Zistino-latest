"""
Models for ContactUsMessages compatibility layer.
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class ContactUsMessage(models.Model):
    """Contact Us Message model matching old Swagger format."""
    TYPE_CHOICES = [
        (0, 'General Inquiry'),
        (1, 'Support Request'),
        (2, 'Complaint'),
        (3, 'Suggestion'),
        (4, 'Other'),
    ]
    
    RESPONSE_STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'In Progress'),
        (2, 'Resolved'),
        (3, 'Closed'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    json_ext = models.TextField(blank=True, null=True, help_text='JSON extension field for additional data')
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    response_status = models.IntegerField(choices=RESPONSE_STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact_us_messages'
        verbose_name = 'Contact Us Message'
        verbose_name_plural = 'Contact Us Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
