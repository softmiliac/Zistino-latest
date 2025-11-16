"""
Brands compatibility URL routes for Flutter apps.
All 12 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Brands

Flutter expects: /api/v1/brands/{endpoint}
All endpoints are tagged with 'Brands' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/brands/{id} - Retrieves a brand by its ID
2. PUT /api/v1/brands/{id} - Updates an existing brand by its ID
3. DELETE /api/v1/brands/{id} - Deletes a brand by its ID
4. GET /api/v1/brands/dapper - Get brands (dapper context)
5. POST /api/v1/brands/search - Search brands using available Filters
6. POST /api/v1/brands/searchwithdescription - Search brands with description
7. POST /api/v1/brands - Creates a new brand
8. POST /api/v1/brands/generate-random - Generate random brands
9. DELETE /api/v1/brands/delete-random - Delete random brands
10. GET /api/v1/brands/all - Retrieves all brands
11. GET /api/v1/brands/client/all - Get All Brands (client)
12. GET /api/v1/brands/client/description/all - Get All Brands with descriptions (client)
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.BrandViewSet, basename='brand')

urlpatterns = [
    path('', include(router.urls)),
]

