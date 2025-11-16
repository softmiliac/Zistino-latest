from django.contrib import admin
from .models import Address, Vehicle, Zone, UserZone


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin for user addresses"""
    list_display = ('full_name', 'user', 'city', 'province', 'country', 'phone_number', 'created_at')
    list_filter = ('country', 'province', 'city', 'created_at')
    search_fields = ('full_name', 'user__phone_number', 'user__username', 
                     'city', 'province', 'address', 'email', 'phone_number')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user',)  # Better UI - shows searchable dropdown by phone number
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone_number', 'address', 'description')
        }),
        ('Location', {
            'fields': ('city', 'province', 'country', 'zip_code', 'plate', 'unit',
                      'latitude', 'longitude')
        }),
        ('Company (Optional)', {
            'fields': ('company_name', 'company_number', 'vat_number'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Admin for driver vehicles"""
    list_display = ('model_make', 'plate_num', 'user', 'active', 'manufacturer', 'color', 'created_at')
    list_filter = ('active', 'manufacturer', 'bodytype', 'created_at')
    search_fields = ('plate_num', 'model_make', 'user__phone_number', 
                     'user__username', 'licence', 'registration_num', 'gps_device_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('user',)  # Better UI - shows searchable dropdown by phone number
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Vehicle Information', {
            'fields': ('model_make', 'plate_num', 'manufacturer', 'bodytype', 'color')
        }),
        ('Registration', {
            'fields': ('licence', 'registration_num', 'engine_size')
        }),
        ('Details', {
            'fields': ('tank', 'numoftyres', 'gps_device_id', 'active')
        }),
        ('Location & GPS Device', {
            'fields': ('latitude', 'longitude', 'protocol', 'port'),
            'description': 'GPS device communication settings. Protocol: TCP/UDP/HTTP. Port: Network port number (0 = not configured, use default).'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    """Admin for zones"""
    list_display = ('zone', 'zonepath', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('zone', 'zonepath', 'description', 'address')
    readonly_fields = ('id', 'created_at')
    ordering = ('zone',)


@admin.register(UserZone)
class UserZoneAdmin(admin.ModelAdmin):
    """Admin for user-zone relationships"""
    list_display = ('user', 'zone', 'last_modified_on')
    list_filter = ('zone', 'last_modified_on')
    search_fields = ('user__phone_number', 'user__username', 'zone__zone')
    readonly_fields = ('id', 'last_modified_on')
    autocomplete_fields = ('user', 'zone')
    ordering = ('-last_modified_on',)

