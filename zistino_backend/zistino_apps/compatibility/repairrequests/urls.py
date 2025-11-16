"""
URL patterns for RepairRequests compatibility layer.
Provides all 13 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.RepairRequestsViewSet, basename='repairrequests')

urlpatterns = [
    # Router URLs (handles: GET/PUT/DELETE /api/v1/repairrequests/{id}, POST /api/v1/repairrequests, and ViewSet actions)
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dapper', views.RepairRequestsDapperView.as_view(), name='repairrequests-dapper'),
    path('repairrequestmessagesbyrepairid/<int:id>', views.RepairRequestMessagesByRepairIdView.as_view(), name='repairrequests-messages-by-repair-id'),
    path('archiveasync/<int:id>', views.RepairRequestArchiveAsyncView.as_view(), name='repairrequests-archiveasync'),
]

