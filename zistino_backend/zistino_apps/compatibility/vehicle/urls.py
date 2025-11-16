"""
URL patterns for Vehicle compatibility layer.
Provides all endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.VehicleViewSet, basename='vehicle')

urlpatterns = [
    # Custom endpoints (must come before router URLs to avoid conflicts)
    path('all', views.VehicleAllView.as_view(), name='vehicle-all'),
    path('job-id/<str:jobid>', views.VehicleGetByJobIdView.as_view(), name='vehicle-get-by-job-id'),
    
    # Router URLs (handles: GET/POST /api/v1/vehicle, GET/PUT/DELETE /api/v1/vehicle/{id})
    path('', include(router.urls)),
]

