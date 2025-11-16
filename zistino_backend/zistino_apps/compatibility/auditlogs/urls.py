"""
AuditLogs compatibility URL routes for Flutter apps.
Single endpoint from Swagger: https://recycle.metadatads.com/swagger/index.html#/AuditLogs

Flutter expects: GET /api/audit-logs
Backend: To be implemented (currently placeholder view)

All endpoints are tagged with 'AuditLogs' to appear grouped in Swagger UI.
"""
from django.urls import path
from . import views as auditlogs_views

urlpatterns = [
    # ============================================================================
    # SINGLE ENDPOINT
    # ============================================================================
    
    # GET /api/v1/audit-logs - List all audit logs
    path('', auditlogs_views.AuditLogsViewSet.as_view({'get': 'list'}), name='auditlogs-list'),
]

