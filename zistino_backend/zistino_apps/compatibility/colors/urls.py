"""
Colors compatibility URL routes for Flutter apps.
All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Colors

Flutter expects: /api/v1/colors/{endpoint}
All endpoints are tagged with 'Colors' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/colors/{id} - Retrieves a color by its ID
2. PUT /api/v1/colors/{id} - Updates an existing color by its ID
3. DELETE /api/v1/colors/{id} - Deletes a color by its ID
4. GET /api/v1/colors/dapper - Get colors (dapper context)
5. POST /api/v1/colors/search - Search colors using available Filters
6. POST /api/v1/colors - Creates a new color
7. GET /api/v1/colors/all - Retrieves all colors
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ColorViewSet, basename='color')

urlpatterns = [
    path('', include(router.urls)),
]

