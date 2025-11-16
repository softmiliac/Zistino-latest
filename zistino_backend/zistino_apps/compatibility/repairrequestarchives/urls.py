"""
URL patterns for RepairRequestArchives compatibility layer.
Provides all 5 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.RepairRequestArchivesViewSet, basename='repairrequestarchives')

urlpatterns = [
    # Router URLs (handles: GET/DELETE /api/v1/repairrequestarchives/{id}, POST /api/v1/repairrequestarchives/search)
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dapper', views.RepairRequestArchivesDapperView.as_view(), name='repairrequestarchives-dapper'),
    path('getbyuserid', views.RepairRequestArchivesGetByUserIdView.as_view(), name='repairrequestarchives-getbyuserid'),
]

