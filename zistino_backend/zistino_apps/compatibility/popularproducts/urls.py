"""
PopularProducts compatibility URL routes for Flutter apps.

Note: This controller doesn't exist in the old Swagger, but Flutter app expects it.
We'll create basic endpoints similar to Products but for popular products.

Flutter expects: /api/v1/popularproducts/{endpoint}
All endpoints are tagged with 'PopularProducts' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/popularproducts/ - List popular products
2. GET /api/v1/popularproducts/{id} - Get popular product by ID
3. POST /api/v1/popularproducts/search - Search popular products
4. POST /api/v1/popularproducts/client/search - Client search popular products
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.PopularProductsViewSet, basename='popularproduct')

urlpatterns = [
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

