"""
Likes compatibility URL routes for Flutter apps.
All 4 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Likes

Flutter expects: /api/v1/likes/{endpoint}
All endpoints are tagged with 'Likes' to appear grouped in Swagger UI.

Endpoints:
1. POST /api/v1/likes/client - Like an item
2. DELETE /api/v1/likes/client/unlike - Unlike an item
3. GET /api/v1/likes/client/item/{ItemId}/type - Get like status for item
4. GET /api/v1/likes/client/{ProductId}/type - Get like status for product
"""
from django.urls import path
from . import views

urlpatterns = [
    # CLIENT ENDPOINTS WITH PATH PARAMETERS (Must come before other routes to avoid conflicts)
    # ItemId can be integer (0) or UUID - use str to accept both
    path('client/item/<str:ItemId>/type', views.LikesClientItemStatusView.as_view(), name='likes-client-item-status'),
    path('client/<uuid:ProductId>/type', views.LikesClientProductStatusView.as_view(), name='likes-client-product-status'),
    
    # CLIENT ENDPOINTS
    path('client/unlike', views.LikesClientUnlikeView.as_view(), name='likes-client-unlike'),
    path('client', views.LikesClientView.as_view(), name='likes-client'),
]

