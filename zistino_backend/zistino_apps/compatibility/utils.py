"""
Utility functions for compatibility layer.
Provides response wrappers to match old Swagger format.
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, List, Optional, Dict
import secrets
from datetime import datetime, timedelta
from django.utils import timezone


def create_success_response(
    data: Any,
    messages: Optional[List[str]] = None,
    status_code: int = status.HTTP_200_OK,
    pagination: Optional[Dict[str, Any]] = None
) -> Response:
    """
    Create a success response matching old Swagger format.
    
    Format:
    {
        "data": {...},
        "messages": [],  # Default to empty array
        "succeeded": true,
        "currentPage": 1,  # if pagination provided
        "totalPages": 1,   # if pagination provided
        ...
    }
    """
    # Default to empty array for messages (matching new Swagger format)
    # If None is explicitly passed, use empty array
    # If a list is passed, use it (even if empty)
    if messages is None:
        messages_value = []
    else:
        messages_value = messages
    
    response_data = {
        "data": data,
        "messages": messages_value,
        "succeeded": True
    }
    
    # Add pagination fields if provided
    if pagination:
        response_data.update(pagination)
    
    return Response(
        response_data,
        status=status_code
    )


def create_authentication_error_response() -> Response:
    """
    Create an authentication error response matching old Swagger format exactly.
    
    Format:
    {
        "source": "Oxygen.Infrastructure.Identity.Startup+<>c",
        "exception": "Authentication Failed.",
        "errorId": "uuid",
        "supportMessage": "Provide the ErrorId to the support team for further analysis.",
        "statusCode": 401,
        "succeeded": false
    }
    """
    import uuid
    return Response(
        {
            "source": "Django.REST.Framework",
            "exception": "Authentication Failed.",
            "errorId": str(uuid.uuid4()),
            "supportMessage": "Provide the ErrorId to the support team for further analysis.",
            "statusCode": 401,
            "succeeded": False
        },
        status=status.HTTP_401_UNAUTHORIZED
    )


def create_error_response(
    error_message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_type: Optional[str] = None,
    errors: Optional[Dict[str, List[str]]] = None,
    detail: Optional[str] = None,
    instance: Optional[str] = None,
    source: Optional[str] = None,
    exception: Optional[str] = None,
    error_id: Optional[str] = None,
    support_message: Optional[str] = None
) -> Response:
    """
    Create an error response matching old Swagger format.
    
    Always returns standardized format:
    {
        "messages": ["string"],
        "succeeded": false,
        "data": null,
        "source": "string",
        "exception": "string",
        "errorId": "string",
        "supportMessage": "string",
        "statusCode": 0
    }
    
    For 400 validation errors, also includes:
    {
        "type": "string",
        "title": "string",
        "status": 400,
        "detail": "string",
        "instance": "string",
        "errors": {
            "field1": ["error1", "error2"],
            "field2": ["error3"]
        }
    }
    """
    import uuid
    
    # Generate error ID if not provided
    if error_id is None:
        error_id = str(uuid.uuid4())
    
    # Default values
    if source is None:
        source = "Django.REST.Framework"
    if exception is None:
        exception = error_message
    if support_message is None:
        support_message = "Provide the ErrorId to the support team for further analysis."
    
    # Build base response
    response_data = {
        "messages": [error_message],
        "succeeded": False,
        "data": None,
        "source": source,
        "exception": exception,
        "errorId": error_id,
        "supportMessage": support_message,
        "statusCode": status_code
    }
    
    # For 400 validation errors, add additional fields for backward compatibility
    if status_code == status.HTTP_400_BAD_REQUEST and (errors or detail):
        response_data.update({
            "type": error_type or "https://tools.ietf.org/html/rfc7231#section-6.5.1",
            "title": "One or more validation errors occurred.",
            "status": status_code,
            "detail": detail or error_message,
            "instance": instance or "",
            "errors": errors or {}
        })
    
    return Response(response_data, status=status_code)


def generate_refresh_token() -> str:
    """Generate a random refresh token string."""
    return secrets.token_urlsafe(32)


def calculate_refresh_token_expiry() -> datetime:
    """Calculate refresh token expiry time (30 days from now)."""
    return timezone.now() + timedelta(days=30)

