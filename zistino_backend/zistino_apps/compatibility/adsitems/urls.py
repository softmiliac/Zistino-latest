"""
AdsItems compatibility URL routes for Flutter apps.
All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/AdsItems

Flutter expects: /api/v1/adsitems/{endpoint}
Backend: To be implemented (currently placeholder views)

All endpoints are tagged with 'AdsItems' to appear grouped in Swagger UI.
"""
from django.urls import path
from . import views as adsitems_views

urlpatterns = [
    # ============================================================================
    # STANDARD REST ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/adsitems/ - List all ads items
    # POST /api/v1/adsitems - Create new ad item
    path('', adsitems_views.AdsItemsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='adsitems-list-create'),
    
    # GET /api/v1/adsitems/{id} - Get ad item by ID
    # PUT /api/v1/adsitems/{id} - Update ad item (full)
    # DELETE /api/v1/adsitems/{id} - Delete ad item
    path('<int:id>', adsitems_views.AdsItemsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='adsitems-detail'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/adsitems/dapper - Get ads items (dapper context)
    path('dapper', adsitems_views.AdsItemsViewSet.as_view({'get': 'dapper'}), name='adsitems-dapper'),
    
    # POST /api/v1/adsitems/search - Search ads items using filters
    # Description: "Search AdsItems using available Filters."
    path('search', adsitems_views.AdsItemsViewSet.as_view({'post': 'search'}), name='adsitems-search'),
    
    # ============================================================================
    # CLIENT ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/adsitems/client/by-zoneid/{id} - Get ads items by zone ID for client
    path('client/by-zoneid/<int:id>', adsitems_views.AdsItemsViewSet.as_view({'get': 'client_by_zoneid'}), name='adsitems-client-by-zoneid'),
]

