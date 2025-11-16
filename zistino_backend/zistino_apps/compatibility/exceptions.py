"""
Global exception handler for compatibility layer.
Catches all exceptions and returns standardized error format.
"""
import uuid
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, DatabaseError
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError,
    AuthenticationFailed,
    PermissionDenied as DRFPermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
)
import logging

logger = logging.getLogger(__name__)


def get_error_source(exception):
    """Get the source/class name of the exception."""
    return f"{exception.__class__.__module__}.{exception.__class__.__name__}"


def compatibility_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized error format.
    
    Returns:
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
    """
    # Generate error ID
    error_id = str(uuid.uuid4())
    
    # Get the view and request from context
    view = context.get('view', None)
    request = context.get('request', None)
    
    # Default error message
    error_message = "An error occurred while processing the request."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    source = "Unknown"
    exception_message = str(exc)
    support_message = "Provide the ErrorId to the support team for further analysis."
    
    # Handle different exception types
    if isinstance(exc, Http404):
        error_message = "Resource not found."
        status_code = status.HTTP_404_NOT_FOUND
        source = get_error_source(exc)
        exception_message = "Not Found"
        support_message = "The requested resource does not exist."
        
    elif isinstance(exc, DRFValidationError):
        # DRF ValidationError - format field errors
        error_message = "Validation error occurred."
        status_code = status.HTTP_400_BAD_REQUEST
        source = get_error_source(exc)
        exception_message = "Validation Error"
        
        # Format validation errors
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                # Field errors
                error_list = []
                for field, errors in exc.detail.items():
                    if isinstance(errors, list):
                        error_list.extend([f"{field}: {error}" for error in errors])
                    else:
                        error_list.append(f"{field}: {errors}")
                if error_list:
                    error_message = "; ".join(error_list)
            elif isinstance(exc.detail, list):
                error_message = "; ".join([str(e) for e in exc.detail])
            else:
                error_message = str(exc.detail)
        
    elif isinstance(exc, ValidationError):
        # Django ValidationError
        error_message = "Validation error occurred."
        status_code = status.HTTP_400_BAD_REQUEST
        source = get_error_source(exc)
        exception_message = "Validation Error"
        if hasattr(exc, 'message_dict'):
            error_list = []
            for field, errors in exc.message_dict.items():
                if isinstance(errors, list):
                    error_list.extend([f"{field}: {error}" for error in errors])
                else:
                    error_list.append(f"{field}: {errors}")
            if error_list:
                error_message = "; ".join(error_list)
        elif hasattr(exc, 'messages'):
            error_message = "; ".join([str(m) for m in exc.messages])
        else:
            error_message = str(exc)
            
    elif isinstance(exc, AuthenticationFailed):
        error_message = "Authentication failed."
        status_code = status.HTTP_401_UNAUTHORIZED
        source = get_error_source(exc)
        exception_message = "Authentication Failed."
        support_message = "Please provide valid authentication credentials."
        
    elif isinstance(exc, DRFPermissionDenied) or isinstance(exc, PermissionDenied):
        error_message = "Permission denied."
        status_code = status.HTTP_403_FORBIDDEN
        source = get_error_source(exc)
        exception_message = "Permission Denied"
        support_message = "You do not have permission to perform this action."
        
    elif isinstance(exc, NotFound):
        error_message = "Resource not found."
        status_code = status.HTTP_404_NOT_FOUND
        source = get_error_source(exc)
        exception_message = "Not Found"
        support_message = "The requested resource does not exist."
        
    elif isinstance(exc, MethodNotAllowed):
        # MethodNotAllowed may not have .method attribute in all DRF versions
        method = getattr(exc, 'method', getattr(exc, 'allowed_methods', ['Unknown']))
        if isinstance(method, list):
            method = ', '.join(method) if method else 'Unknown'
        error_message = f"Method '{method}' not allowed."
        status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        source = get_error_source(exc)
        exception_message = "Method Not Allowed"
        support_message = "The HTTP method used is not allowed for this endpoint."
        
    elif isinstance(exc, NotAcceptable):
        error_message = "Not acceptable."
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        source = get_error_source(exc)
        exception_message = "Not Acceptable"
        
    elif isinstance(exc, UnsupportedMediaType):
        error_message = "Unsupported media type."
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        source = get_error_source(exc)
        exception_message = "Unsupported Media Type"
        
    elif isinstance(exc, Throttled):
        error_message = "Request was throttled."
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        source = get_error_source(exc)
        exception_message = "Throttled"
        support_message = "Too many requests. Please try again later."
        
    elif isinstance(exc, IntegrityError):
        error_message = "Database integrity error occurred."
        status_code = status.HTTP_400_BAD_REQUEST
        source = get_error_source(exc)
        exception_message = "Integrity Error"
        # Extract meaningful error message
        error_str = str(exc)
        if "UNIQUE constraint" in error_str or "duplicate key" in error_str.lower():
            error_message = "A record with this information already exists."
        elif "FOREIGN KEY constraint" in error_str or "foreign key" in error_str.lower():
            error_message = "Referenced record does not exist."
        else:
            error_message = "Database constraint violation occurred."
        support_message = "Please check your input data and try again."
        
    elif isinstance(exc, DatabaseError):
        error_message = "Database error occurred."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        source = get_error_source(exc)
        exception_message = "Database Error"
        support_message = "A database error occurred. Please contact support."
        
    elif isinstance(exc, APIException):
        # Other DRF API exceptions
        error_message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
        status_code = exc.status_code if hasattr(exc, 'status_code') else status.HTTP_500_INTERNAL_SERVER_ERROR
        source = get_error_source(exc)
        exception_message = exc.__class__.__name__
        
    else:
        # Unknown exception - log the full traceback
        error_message = "An unexpected error occurred."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        source = get_error_source(exc)
        exception_message = str(exc)
        # Log the full traceback for debugging
        logger.error(
            f"Unhandled exception: {exc.__class__.__name__}",
            exc_info=True,
            extra={
                'error_id': error_id,
                'view': view.__class__.__name__ if view else None,
                'request_path': request.path if request else None,
            }
        )
    
    # Build response
    response_data = {
        "messages": [error_message],
        "succeeded": False,
        "data": None,
        "source": source,
        "exception": exception_message,
        "errorId": error_id,
        "supportMessage": support_message,
        "statusCode": status_code
    }
    
    return Response(response_data, status=status_code)

