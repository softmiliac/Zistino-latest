"""
URL patterns for ProductSections compatibility layer.
Provides all 10 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ProductSectionsViewSet, basename='productsections')

urlpatterns = [
    # Router URLs (handles: GET/POST /api/v1/productsections, GET/PUT/DELETE /api/v1/productsections/{id})
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dapper', views.ProductSectionsDapperView.as_view(), name='productsections-dapper'),
    path('all', views.ProductSectionsAllView.as_view(), name='productsections-all'),
    path('by-group-name', views.ProductSectionsByGroupNameView.as_view(), name='productsections-by-group-name'),
    path('by-page', views.ProductSectionsByPageView.as_view(), name='productsections-by-page'),
]

