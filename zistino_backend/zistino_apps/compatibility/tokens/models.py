"""
Models for Tokens compatibility layer.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets


class RefreshToken(models.Model):
    """Model for storing refresh tokens."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refresh_tokens'
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_revoked = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'compatibility'
        db_table = 'refresh_tokens'
        verbose_name = 'Refresh Token'
        verbose_name_plural = 'Refresh Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_revoked']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.token[:20]}..."
    
    @classmethod
    def generate_token(cls):
        """Generate a new refresh token."""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def create_for_user(cls, user, expiry_days=30):
        """Create a refresh token for a user."""
        token = cls.generate_token()
        expires_at = timezone.now() + timedelta(days=expiry_days)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
    
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired()
