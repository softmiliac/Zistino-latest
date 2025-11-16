from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom User model - snake_case fields for API consistency"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True)
    is_active_driver = models.BooleanField(default=True)  # keep auth is_active untouched
    is_active = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    image_url = models.ImageField(upload_to='profiles/', blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True)
    vat_number = models.CharField(max_length=50, blank=True)
    representative = models.CharField(max_length=255, blank=True)
    sheba = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True)
    representative_by = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=10, default='fa')
    country = models.CharField(max_length=100, default='Iran')
    city = models.CharField(max_length=100, blank=True)
    # Additional driver-specific fields
    is_driver = models.BooleanField(default=True)
    driver_license_number = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=100, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class VerificationCode(models.Model):
    """Model for storing phone verification codes"""
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'verification_codes'
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()
