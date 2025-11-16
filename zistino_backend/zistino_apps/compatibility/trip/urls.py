"""
URL patterns for Trip compatibility layer.
Provides all endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.TripViewSet, basename='trip')

urlpatterns = [
    # Custom endpoints (must come before router URLs to avoid conflicts)
    path('all', views.TripAllView.as_view(), name='trip-all'),
    path('job-id/<str:jobid>', views.TripGetByJobIdView.as_view(), name='trip-get-by-job-id'),
    
    # Router URLs (handles: GET/POST /api/v1/trip, GET/PUT/DELETE /api/v1/trip/{id})
    path('', include(router.urls)),
]

