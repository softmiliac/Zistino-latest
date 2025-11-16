"""
Localizations compatibility URL routes for Flutter apps.
All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Localizations

Flutter expects: /api/v1/localizations/{endpoint}
All endpoints are tagged with 'Localizations' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/localizations/{id} - Retrieves a localization by its ID
2. PUT /api/v1/localizations/{id} - Updates an existing localization by its ID
3. DELETE /api/v1/localizations/{id} - Deletes a localization by its ID
4. GET /api/v1/localizations/dapper - Get localizations (dapper context)
5. POST /api/v1/localizations/search - Search Localization using available Filters
6. POST /api/v1/localizations - Creates a new localization
7. GET /api/v1/localizations/resourcesets - Get resource sets
8. GET /api/v1/localizations/client/by-resourceset/{set} - Get localizations by resource set
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.LocalizationViewSet, basename='localization')

urlpatterns = [
    # CLIENT ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    path('client/by-resourceset/<str:set>', views.LocalizationsClientByResourceSetView.as_view(), name='localizations-client-by-resourceset'),
    
    # SPECIAL ENDPOINTS (Must come before router to avoid conflicts)
    path('resourcesets', views.LocalizationsResourceSetsView.as_view(), name='localizations-resourcesets'),
    
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

