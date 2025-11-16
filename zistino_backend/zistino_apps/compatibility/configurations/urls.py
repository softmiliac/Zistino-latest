"""
Configurations compatibility URL routes for Flutter apps.
All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Configurations

Flutter expects: /api/v1/configurations/{endpoint}
All endpoints are tagged with 'Configurations' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/configurations/{id} - Retrieves a configuration by its ID
2. PUT /api/v1/configurations/{id} - Updates an existing configuration by its ID
3. DELETE /api/v1/configurations/{id} - Deletes a configuration by its ID
4. GET /api/v1/configurations/dapper - Get configurations (dapper context)
5. POST /api/v1/configurations/search - Search configurations using available Filters
6. POST /api/v1/configurations - Creates a new configuration
7. POST /api/v1/configurations/client/search - Search configurations for client
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ConfigurationViewSet, basename='configuration')

urlpatterns = [
    path('', include(router.urls)),
]

