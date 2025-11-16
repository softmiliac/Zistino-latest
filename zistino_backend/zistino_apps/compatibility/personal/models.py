"""
User model is imported from authentication app.
This file is kept for compatibility but imports from authentication app.
"""
from django.contrib.auth import get_user_model

User = get_user_model()

__all__ = ['User']

