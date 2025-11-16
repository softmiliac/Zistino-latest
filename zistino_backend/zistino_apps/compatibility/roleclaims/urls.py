"""
URL patterns for RoleClaims compatibility layer.
Provides all 7 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.RoleClaimsViewSet, basename='roleclaims')

urlpatterns = [
    # Router URLs (handles: GET/POST /api/v1/roleclaims, GET/DELETE /api/v1/roleclaims/{roleId} or {id})
    # Note: GET uses {roleId}, DELETE uses {id} - both handled by ViewSet with pk parameter
    path('', include(router.urls)),
    
    # Custom endpoints
    path('claimgroupres', views.RoleClaimsClaimGroupResView.as_view(), name='roleclaims-claimgroupres'),
    path('claimgroup', views.RoleClaimsClaimGroupView.as_view(), name='roleclaims-claimgroup'),
]

