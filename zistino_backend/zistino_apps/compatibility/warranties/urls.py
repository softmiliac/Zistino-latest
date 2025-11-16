"""
URL patterns for Warranties compatibility layer.
Provides all 9 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.WarrantiesViewSet, basename='warranties')

urlpatterns = [
    # Custom endpoints (must come before router to avoid conflicts)
    path('dapper', views.WarrantiesDapperView.as_view(), name='warranties-dapper'),
    path('all', views.WarrantiesAllView.as_view(), name='warranties-all'),
    path('client/searchwithdescription', views.WarrantiesClientSearchWithDescriptionView.as_view(), name='warranties-client-searchwithdescription'),
    
    # Router URLs (handles: GET/POST /api/v1/warranties, GET/PUT/DELETE /api/v1/warranties/{id})
    path('', include(router.urls)),
]

