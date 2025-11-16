"""
Coupons compatibility URL routes for Flutter apps.
All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Coupons

Flutter expects: /api/v1/coupons/{endpoint}
All endpoints are tagged with 'Coupons' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/coupons/{id} - Retrieves a coupon by its ID
2. PUT /api/v1/coupons/{id} - Updates an existing coupon by its ID
3. DELETE /api/v1/coupons/{id} - Deletes a coupon by its ID
4. GET /api/v1/coupons/dapper - Get coupons (dapper context)
5. POST /api/v1/coupons/search - Search coupons using available Filters
6. POST /api/v1/coupons - Creates a new coupon
7. GET /api/v1/coupons/generate-key - Generate coupon key
8. GET /api/v1/coupons/client/apply-on-basket/{key} - Apply coupon on basket for client
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.CouponViewSet, basename='coupon')

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/coupons/client/apply-on-basket/{key}
    path('client/apply-on-basket/<str:key>', views.CouponClientApplyOnBasketView.as_view(), name='coupons-client-apply-on-basket'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (via router)
    # ============================================================================
    path('', include(router.urls)),
]

