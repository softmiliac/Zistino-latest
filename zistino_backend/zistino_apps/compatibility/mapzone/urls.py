"""
MapZone compatibility URL routes for Flutter apps.
All 9 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/MapZone

Flutter expects: /api/v1/mapzone/{endpoint}
All endpoints are tagged with 'MapZone' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/mapzone/{id} - Retrieves a zone by its ID
2. PUT /api/v1/mapzone/{id} - Updates an existing zone by its ID
3. DELETE /api/v1/mapzone/{id} - Deletes a zone by its ID
4. POST /api/v1/mapzone/search - Search MapZone using available Filters
5. POST /api/v1/mapzone/searchuserinzone - Search users in zone
6. POST /api/v1/mapzone/userinzone - Get zones for user
7. POST /api/v1/mapzone - Creates a new zone
8. POST /api/v1/mapzone/createuserinzone - Create user in zone
9. DELETE /api/v1/mapzone/userinzone/{id} - Delete user in zone
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.MapZoneViewSet, basename='mapzone')

urlpatterns = [
    # USER IN ZONE ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    path('userinzone/<int:id>', views.MapZoneUserInZoneDeleteView.as_view(), name='mapzone-userinzone-delete'),
    
    # SPECIAL ENDPOINTS (Must come before router to avoid conflicts)
    path('search', views.MapZoneViewSet.as_view({'post': 'search'}), name='mapzone-search'),
    path('searchuserinzone', views.MapZoneSearchUserInZoneView.as_view(), name='mapzone-searchuserinzone'),
    path('userinzone', views.MapZoneUserInZoneView.as_view(), name='mapzone-userinzone'),
    path('createuserinzone', views.MapZoneCreateUserInZoneView.as_view(), name='mapzone-createuserinzone'),
    
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

