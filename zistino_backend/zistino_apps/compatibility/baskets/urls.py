"""
Baskets compatibility URL routes for Flutter apps.
All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Baskets

Flutter expects: /api/v1/baskets/{endpoint}
Backend has: /api/v1/baskets/ (via router, but needs compatibility routes for specific endpoints)

All endpoints are tagged with 'Baskets' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/baskets/{id} - Retrieves a basket by its ID
2. PUT /api/v1/baskets/{id} - Updates an existing basket by its ID
3. DELETE /api/v1/baskets/{id} - Deletes a basket by its ID
4. GET /api/v1/baskets/dapper - Get baskets (dapper context)
5. POST /api/v1/baskets - Creates a new basket
6. GET /api/v1/baskets/client - Get Basket of currently logged in user
7. POST /api/v1/baskets/client - Set Basket for currently logged in user
8. GET /api/v1/baskets/client/check - check Basket of currently logged in user
"""
from django.urls import path
from . import views as baskets_views

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS (Must come before {id} routes to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/baskets/client/check - Check basket of currently logged in user
    # Description: "check Basket of currently logged in user."
    path('client/check', baskets_views.BasketsClientCheckView.as_view(), name='baskets-client-check'),
    
    # GET /api/v1/baskets/client - Get basket of currently logged in user
    # Description: "Get Basket of currently logged in user."
    # POST /api/v1/baskets/client - Set basket for currently logged in user
    # Description: "Set Basket for currently logged in user."
    path('client', baskets_views.BasketsClientView.as_view(), name='baskets-client'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/baskets/dapper - Get baskets (dapper context)
    path('dapper', baskets_views.BasketsDapperView.as_view(), name='baskets-dapper'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS WITH ID
    # ============================================================================
    
    # GET /api/v1/baskets/{id} - Get basket by ID
    # PUT /api/v1/baskets/{id} - Update basket by ID
    # DELETE /api/v1/baskets/{id} - Delete basket by ID
    path('<int:pk>', baskets_views.BasketsDetailView.as_view(), name='baskets-detail'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (Must come last)
    # ============================================================================
    
    # POST /api/v1/baskets - Create a new basket
    # GET /api/v1/baskets - List/get current user's basket
    path('', baskets_views.BasketsListView.as_view(), name='baskets-list-create'),
]

