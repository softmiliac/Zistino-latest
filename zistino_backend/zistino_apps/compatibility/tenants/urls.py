"""
URL patterns for Tenants compatibility layer.
Provides all 6 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.TenantsViewSet, basename='tenants')

urlpatterns = [
    # Custom endpoints (must come before router to avoid conflicts)
    path('upgrade', views.TenantsUpgradeView.as_view(), name='tenants-upgrade'),
    # Use str to accept both UUID and key, but these endpoints use ID
    path('<str:id>/deactivate', views.TenantsDeactivateView.as_view(), name='tenants-deactivate'),
    path('<str:id>/activate', views.TenantsActivateView.as_view(), name='tenants-activate'),
    
    # Router URLs (handles: GET/POST /api/v1/tenants, GET /api/v1/tenants/{key})
    # Note: retrieve() uses pk as key (lookup_field='key')
    path('', include(router.urls)),
]

