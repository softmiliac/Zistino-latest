"""
Addresses compatibility URL routes for Flutter apps.
All 11 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Addresses

Flutter expects: /api/v1/addresses/{endpoint}
All endpoints are tagged with 'Addresses' to appear grouped in Swagger UI.
"""
from django.urls import path
from . import views as addresses_views

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS (Must come before {id} routes to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/addresses/client/by-userid - Get addresses of currently logged in user
    path('client/by-userid', addresses_views.AddressesClientByUserIdView.as_view(), name='addresses-client-by-userid'),
    
    # GET /api/v1/addresses/client/{id} - Get address by ID for current user
    # PUT /api/v1/addresses/client/{id} - Update address for current user
    # DELETE /api/v1/addresses/client/{id} - Delete address for current user
    path('client/<int:pk>', addresses_views.AddressesClientDetailView.as_view(), name='addresses-client-detail'),
    
    # GET /api/v1/addresses/client - Get addresses of currently logged in user
    # POST /api/v1/addresses/client - Create address for currently logged in user
    path('client', addresses_views.AddressesClientView.as_view(), name='addresses-client'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/addresses/dapper - Get addresses (dapper context)
    path('dapper', addresses_views.AddressesDapperView.as_view(), name='addresses-dapper'),
    
    # GET /api/v1/addresses/by-userid - Get addresses by user ID
    path('by-userid', addresses_views.AddressesByUserIdView.as_view(), name='addresses-by-userid'),
    
    # POST /api/v1/addresses/search - Search addresses with filters
    path('search', addresses_views.AddressesSearchView.as_view(), name='addresses-search'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS WITH ID (Must come after special endpoints)
    # ============================================================================
    
    # GET /api/v1/addresses/{id} - Get address by ID
    # PUT /api/v1/addresses/{id} - Update address (full)
    # DELETE /api/v1/addresses/{id} - Delete address
    path('<int:pk>', addresses_views.AddressesDetailView.as_view(), name='addresses-detail'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (Must come last)
    # ============================================================================
    
    # GET /api/v1/addresses/ - List all addresses
    # POST /api/v1/addresses/ - Create address
    path('', addresses_views.AddressesListView.as_view(), name='addresses-list-create'),
]

