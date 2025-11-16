"""
CouponUses compatibility URL routes for Flutter apps.
All 5 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/CouponUses

Flutter expects: /api/v1/couponuses/{endpoint}
All endpoints are tagged with 'CouponUses' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/couponuses/{id} - Retrieves a coupon use by its ID
2. PUT /api/v1/couponuses/{id} - Updates an existing coupon use by its ID
3. DELETE /api/v1/couponuses/{id} - Deletes a coupon use by its ID
4. POST /api/v1/couponuses/search - Search coupon uses using available Filters
5. POST /api/v1/couponuses - Creates a new coupon use
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.CouponUseViewSet, basename='couponuse')

urlpatterns = [
    path('', include(router.urls)),
]

