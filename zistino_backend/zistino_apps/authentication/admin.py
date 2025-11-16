from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.forms import AdminAuthenticationForm
from django import forms
from .models import User, VerificationCode


class PhoneNumberAdminAuthenticationForm(AdminAuthenticationForm):
    """Custom admin login form that uses phone_number instead of username"""
    username = forms.CharField(
        label='Phone Number',
        max_length=15,
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': '+989056761466'})
    )

    def clean_username(self):
        """Clean phone_number field"""
        phone_number = self.cleaned_data.get('username')
        if phone_number:
            # Normalize phone number (remove spaces, etc.)
            phone_number = phone_number.strip()
        return phone_number


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    list_display = ('id', 'phone_number', 'username', 'email', 'first_name', 'last_name', 
                    'is_active', 'is_active_driver', 'is_driver', 'is_staff', 'date_joined')
    list_display_links = ('id', 'phone_number', 'username')  # Make ID clickable
    list_filter = ('is_active', 'is_active_driver', 'is_driver', 'is_staff', 
                   'is_superuser', 'email_confirmed', 'country', 'city')
    search_fields = ('id', 'phone_number', 'username', 'email', 'first_name', 'last_name', 
                     'company_name', 'national_id')
    ordering = ('-date_joined',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'date_joined', 'last_login')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('User ID', {
            'fields': ('id',)
        }),
        ('Phone Authentication', {
            'fields': ('phone_number', 'is_active_driver',)
        }),
        ('Profile Information', {
            'fields': ('image_url', 'email_confirmed', 'birth_date', 'national_id',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'vat_number', 'representative', 
                      'representative_by', 'sheba', 'bank_name',)
        }),
        ('Location', {
            'fields': ('language', 'country', 'city',)
        }),
        ('Driver Information', {
            'fields': ('is_driver', 'driver_license_number', 
                      'vehicle_type', 'vehicle_plate',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at',)
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Required Fields', {
            'fields': ('phone_number', 'username', 'email', 'password1', 'password2',)
        }),
    )


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """Admin for phone verification codes"""
    list_display = ('phone_number', 'code', 'is_used', 'is_expired_status', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('phone_number', 'code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def is_expired_status(self, obj):
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Expired'


# Override admin site to use custom login form
admin.site.login_form = PhoneNumberAdminAuthenticationForm


# Token admin is already registered by rest_framework.authtoken; avoid duplicate menu entry

