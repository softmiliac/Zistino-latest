"""
CMS compatibility URL routes for Flutter apps.
All 10 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Cms

Flutter expects: /api/v1/cms/{endpoint}
All endpoints are tagged with 'Cms' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/cms/{id} - Retrieves a CMS item by its ID
2. PUT /api/v1/cms/{id} - Updates an existing CMS item by its ID
3. DELETE /api/v1/cms/{id} - Deletes a CMS item by its ID
4. GET /api/v1/cms/dapper - Get CMS (dapper context)
5. POST /api/v1/cms/search - Search CMS using available Filters
6. POST /api/v1/cms - Creates a new CMS item
7. GET /api/v1/cms/getmycms/{userid} - Get CMS by user ID
8. POST /api/v1/cms/getmycms - Get CMS for user
9. GET /api/v1/cms/client/by-name/{name} - Get CMS by name for client
10. GET /api/v1/cms/client/by-group-name/{groupName} - Get CMS by group name for client

Note: The following endpoints already exist in main urls.py and are kept there:
- GET /api/v1/cms/by-page
- GET /api/v1/cms/by-group-name (query param version)
- POST /api/v1/cms/page-view
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.CMSViewSet, basename='cms')

urlpatterns = [
    # ============================================================================
    # CUSTOM ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/cms/getmycms - Get CMS for authenticated user
    path('getmycms', views.CMSGetMyCMSView.as_view(), name='cms-getmycms'),
    
    # GET /api/v1/cms/getmycms/{userid} - Get CMS by user ID (accepts UUID as string)
    path('getmycms/<str:userid>', views.CMSGetMyCMSByUserIdView.as_view(), name='cms-getmycms-by-userid'),
    
    # GET /api/v1/cms/client/by-name/{name}
    path('client/by-name/<str:name>', views.CMSClientByNameView.as_view(), name='cms-client-by-name'),
    
    # GET /api/v1/cms/client/by-group-name/{groupName}
    path('client/by-group-name/<str:groupName>', views.CMSClientByGroupNameView.as_view(), name='cms-client-by-group-name'),
    
    # Router URLs (must come last)
    path('', include(router.urls)),
]

