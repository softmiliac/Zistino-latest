"""
AdsZones compatibility URL routes for Flutter apps.
All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/AdsZones

Flutter expects: /api/v1/adszones/{endpoint}
Backend: To be implemented (currently placeholder views)

All endpoints are tagged with 'AdsZones' to appear grouped in Swagger UI.
"""
from django.urls import path
from . import views as adszones_views

urlpatterns = [
    # ============================================================================
    # STANDARD REST ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/adszones/ - List all ads zones
    # POST /api/v1/adszones - Create new ad zone
    path('', adszones_views.AdsZonesViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='adszones-list-create'),
    
    # GET /api/v1/adszones/{id} - Get ad zone by ID
    # PUT /api/v1/adszones/{id} - Update ad zone (full)
    # DELETE /api/v1/adszones/{id} - Delete ad zone
    path('<int:id>', adszones_views.AdsZonesViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='adszones-detail'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/adszones/dapper - Get ads zones (dapper context)
    path('dapper', adszones_views.AdsZonesViewSet.as_view({'get': 'dapper'}), name='adszones-dapper'),
    
    # POST /api/v1/adszones/search - Search ads zones using filters
    # Description: "Search AdsZones using available Filters."
    path('search', adszones_views.AdsZonesViewSet.as_view({'post': 'search'}), name='adszones-search'),
    
    # GET /api/v1/adszones/all - Get all ads zones
    path('all', adszones_views.AdsZonesViewSet.as_view({'get': 'all'}), name='adszones-all'),
]

