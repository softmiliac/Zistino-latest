from django.contrib import admin
from .models import Configuration, Localization, MailTemplate


@admin.register(Localization)
class LocalizationAdmin(admin.ModelAdmin):
    """Admin interface for Localization model."""
    list_display = ['key', 'resource_set', 'locale', 'is_active', 'created_at']
    list_filter = ['resource_set', 'locale', 'is_active', 'created_at']
    search_fields = ['key', 'value', 'resource_set']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['resource_set', 'key', 'locale']
    list_editable = ['is_active']


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for MailTemplate model."""
    list_display = ['name', 'template_type', 'locale', 'is_active', 'created_at']
    list_filter = ['template_type', 'locale', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'body', 'template_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['name', 'locale']
    list_editable = ['is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'locale', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'body'),
            'description': 'Email subject and body. Body can contain HTML or plain text.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    """Admin for configurations"""
    list_display = ('name', 'type', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'is_active'),
            'description': 'Type: 0 = Default/General, 1+ = Custom category (for grouping). Value: Must be valid JSON format.'
        }),
        ('Value (JSON Field)', {
            'fields': ('value',),
            'description': '''
            <strong>Value must be valid JSON format. Examples:</strong><br><br>
            <strong>Points:</strong> {"amount": 1}<br>
            <strong>Time Slots:</strong> {"start": 8, "end": 20, "split": 4}<br>
            <strong>Weight Ranges:</strong> [{"label": "2-5 kg", "value": "2-5", "min": 2, "max": 5}]<br>
            <strong>Price Rate:</strong> {"rate": 1000, "currency": "Rials"}<br>
            <strong>Payout Tiers:</strong> [{"min": 1, "max": 10, "rate": 100}]<br><br>
            Use double quotes (") not single quotes ('). Click "{}" button to format JSON.
            '''
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

