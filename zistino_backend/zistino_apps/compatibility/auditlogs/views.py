"""
Compatibility views for AuditLogs endpoints.
Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/AuditLogs

All endpoints will appear under "AuditLogs" folder in Swagger UI.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .serializers import AuditLogCompatibilitySerializer


@extend_schema(
    tags=['AuditLogs'],
    operation_id='auditlogs_list',
    summary='Get audit logs',
    description='Get audit logs matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of audit logs',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': [
                            {
                                'id': 'string',
                                'userId': 'string',
                                'type': 'string',
                                'tableName': 'string',
                                'dateTime': '2025-11-12T05:54:27.832Z',
                                'oldValues': 'string',
                                'newValues': 'string',
                                'affectedColumns': 'string',
                                'primaryKey': 'string'
                            }
                        ]
                    }
                )
            ]
        ),
        401: {
            'description': 'Authentication required'
        }
    }
)
class AuditLogsViewSet(viewsets.ViewSet):
    """
    Compatibility viewset for audit logs endpoints.
    Returns audit logs matching old Swagger format.
    
    Note: Currently returns empty list. When AuditLog model is created,
    this will be updated to return actual audit logs.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Get audit logs matching old Swagger format.
        
        Returns empty list for now. To be implemented when AuditLog model is created.
        Expected structure:
        {
            "messages": ["string"],
            "succeeded": true,
            "data": [...]
        }
        """
        # TODO: When AuditLog model is created, implement:
        # from zistino_apps.audit.models import AuditLog
        # 
        # logs = AuditLog.objects.filter(user=request.user).order_by('-created_at')
        # serializer = AuditLogCompatibilitySerializer(logs, many=True)
        # return Response({
        #     'messages': ['string'],
        #     'succeeded': True,
        #     'data': serializer.data
        # }, status=status.HTTP_200_OK)
        
        # For now, return empty list with proper structure matching old Swagger format
        return Response({
            'messages': ['string'],
            'succeeded': True,
            'data': []
        }, status=status.HTTP_200_OK)

