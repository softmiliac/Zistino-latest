"""
URL patterns for Locations compatibility layer.
Provides all endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.LocationsViewSet, basename='locations')

urlpatterns = [
    # Custom endpoints (must come before router URLs to avoid conflicts)
    path('all', views.LocationsAllView.as_view(), name='locations-all'),
    path('job-id/<str:jobid>', views.LocationsGetByJobIdView.as_view(), name='locations-get-by-job-id'),
    
    # Router URLs (handles: GET/POST /api/v1/locations, GET/PUT/DELETE /api/v1/locations/{id})
    path('', include(router.urls)),
]

