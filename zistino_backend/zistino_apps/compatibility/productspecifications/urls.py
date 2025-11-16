"""
URL patterns for ProductSpecifications compatibility layer.
Provides all 7 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ProductSpecificationsViewSet, basename='productspecifications')

urlpatterns = [
    # Search endpoint (MUST come BEFORE router to avoid conflicts)
    path('search', views.ProductSpecificationsViewSet.as_view({'post': 'search'}), name='productspecifications-search'),
    
    # Custom endpoints (MUST come BEFORE router to avoid conflicts)
    path('dapper', views.ProductSpecificationsDapperView.as_view(), name='productspecifications-dapper'),
    path('clone/<int:id>', views.ProductSpecificationsCloneView.as_view(), name='productspecifications-clone'),
    
    # Router URLs (handles: GET/POST /api/v1/productspecifications, GET/PUT/DELETE /api/v1/productspecifications/{id})
    path('', include(router.urls)),
]

