from django.db import models
import json
import uuid


class Localization(models.Model):
    """
    Localization model - stores translation key-value pairs.
    Organized by resource sets and locales.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, help_text='Translation key')
    value = models.TextField(help_text='Translated text')
    resource_set = models.CharField(max_length=100, help_text='Resource set name (e.g., "common", "errors")')
    locale = models.CharField(max_length=10, default='en', help_text='Language code (e.g., "en", "fa")')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'localizations'
        verbose_name = 'Localization'
        verbose_name_plural = 'Localizations'
        # Ensure unique key per resource set and locale
        unique_together = ['key', 'resource_set', 'locale']
        ordering = ['resource_set', 'key', 'locale']
        indexes = [
            models.Index(fields=['resource_set', 'locale', 'is_active']),
            models.Index(fields=['key', 'resource_set']),
            models.Index(fields=['locale', 'is_active']),
        ]

    def __str__(self):
        return f"{self.resource_set}.{self.key} ({self.locale})"


class MailTemplate(models.Model):
    """
    MailTemplate model - stores email templates for system emails.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text='Template name/identifier')
    subject = models.CharField(max_length=500, help_text='Email subject line')
    body = models.TextField(help_text='Email body (HTML or plain text)')
    template_type = models.CharField(
        max_length=50,
        help_text='Template type (e.g., "welcome", "order_confirmation", "password_reset")'
    )
    locale = models.CharField(max_length=10, default='en', help_text='Language code (e.g., "en", "fa")')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_templates'
        verbose_name = 'Mail Template'
        verbose_name_plural = 'Mail Templates'
        # Ensure unique name per locale
        unique_together = ['name', 'locale']
        ordering = ['name', 'locale']
        indexes = [
            models.Index(fields=['name', 'locale', 'is_active']),
            models.Index(fields=['template_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.locale})"


class Configuration(models.Model):
    """Configuration model for app settings - matches ConfigModel."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    type = models.IntegerField(default=0)
    # Store TimeModel as JSON: {"start": "", "end": "", "split": ""}
    value = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configurations'
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (type: {self.type})"

    def get_time_value(self):
        """Helper to get TimeModel structure."""
        if isinstance(self.value, dict):
            return {
                'start': self.value.get('start', ''),
                'end': self.value.get('end', ''),
                'split': self.value.get('split', '')
            }
        return {'start': '', 'end': '', 'split': ''}

    def set_time_value(self, start='', end='', split=''):
        """Helper to set TimeModel structure."""
        self.value = {'start': start, 'end': end, 'split': split}

