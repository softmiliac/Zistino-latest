"""
URL patterns for Roles compatibility layer.
Provides all 10 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.RolesViewSet, basename='roles')

urlpatterns = [
    # Router URLs (handles: GET/DELETE /api/v1/roles/{id}, POST /api/v1/roles, and ViewSet actions)
    path('', include(router.urls)),
    
    # Custom endpoints
    path('count', views.RolesCountView.as_view(), name='roles-count'),
    path('all', views.RolesAllView.as_view(), name='roles-all'),
    path('permissionslist', views.RolesPermissionsListView.as_view(), name='roles-permissionslist'),
]

