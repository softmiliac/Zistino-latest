"""
Orders compatibility URL routes for Flutter apps.
All 26 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Orders

Flutter expects: /api/v1/orders/{endpoint}
All endpoints are tagged with 'Orders' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/orders/{id} - Retrieve order by ID
2. PUT /api/v1/orders/{id} - Update order by ID
3. POST /api/v1/orders - Create new order
4. POST /api/v1/orders/search - Search orders (Admin)
5. POST /api/v1/orders/searchsp - Search orders SP (Admin)
6. POST /api/v1/orders/searchuser - Search orders by user (Admin)
7. POST /api/v1/orders/searchstatics - Search order statistics (Admin)
8. POST /api/v1/orders/admin/getbyuserid - Get orders by user ID (Admin)
9. GET /api/v1/orders/stats - Get order statistics (Admin)
10. GET /api/v1/orders/stats-by-resseller/{id} - Get stats by reseller (Admin)
11. GET /api/v1/orders/stats-by-user/{id} - Get stats by user (Admin)
12. POST /api/v1/orders/client/search - Client search orders
13. POST /api/v1/orders/client/searchsp - Client search orders SP
14. POST /api/v1/orders/client/customer/searchsp - Client customer search orders SP
15. GET /api/v1/orders/client/{id} - Get client order by ID
16. GET /api/v1/orders/client/orderandproductdetails/{id} - Get order and product details
17. GET /api/v1/orders/client/withcutomerinfo/{id} - Get order with customer info
18. POST /api/v1/orders/searchuser - Search orders by user
19. POST /api/v1/orders/checkinstock - Check products in stock
20. POST /api/v1/orders/handyorder - Create handy order
21. POST /api/v1/orders/by-date - Get orders by date
22. GET /api/v1/orders/test-send-sms - Test send SMS (Admin)
23. PUT /api/v1/orders/order-status/{id} - Update order status (Admin)
24. PUT /api/v1/orders/order-item-status/{id} - Update order item status (Admin)
25. GET /api/v1/orders/all - Get all orders (Admin)
26. POST /api/v1/orders/ordermapping - Order mapping
27. GET /api/v1/orders/orderzone/{lat}/{latlong} - Get order zone
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.OrdersViewSet, basename='order')

# Get router URLs and replace the detail route to accept both UUID and integer
router_urls = list(router.urls)
urlpatterns = []
for url_pattern in router_urls:
    # Replace the detail route (which uses uuid) with one that accepts str
    if hasattr(url_pattern, 'pattern') and '{id}' in str(url_pattern.pattern):
        # This is the detail route - replace it
        urlpatterns.append(
            path('<str:id>', views.OrdersViewSet.as_view({
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            }), name='order-detail')
        )
    else:
        # Keep other routes as-is
        urlpatterns.append(url_pattern)

# Add special endpoints with path parameters (Must come before router to avoid conflicts)
urlpatterns = [
    # ADMIN SEARCH ENDPOINTS (Must come before router to avoid conflicts)
    path('search', views.OrdersViewSet.as_view({'post': 'search'}), name='orders-search'),
    path('searchsp', views.OrdersViewSet.as_view({'post': 'searchsp'}), name='orders-searchsp'),
    path('searchuser', views.OrdersViewSet.as_view({'post': 'searchuser'}), name='orders-searchuser'),
    path('searchstatics', views.OrdersViewSet.as_view({'post': 'searchstatics'}), name='orders-searchstatics'),
    
    # CLIENT SEARCH ENDPOINTS (Must come before router to avoid conflicts)
    path('client/search', views.OrdersViewSet.as_view({'post': 'client_search'}), name='orders-client-search'),
    path('client/searchsp', views.OrdersViewSet.as_view({'post': 'client_searchsp'}), name='orders-client-searchsp'),
    path('client/customer/searchsp', views.OrdersViewSet.as_view({'post': 'client_customer_searchsp'}), name='orders-client-customer-searchsp'),
    
    # SPECIAL ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    path('orderzone/<str:lat>/<str:latlong>', views.OrdersOrderZoneView.as_view(), name='orders-orderzone'),
    path('stats-by-resseller/<str:id>', views.OrdersStatsByResellerView.as_view(), name='orders-stats-by-reseller'),
    path('stats-by-user/<str:id>', views.OrdersStatsByUserView.as_view(), name='orders-stats-by-user'),
    path('client/orderandproductdetails/<str:id>', views.OrdersClientOrderAndProductDetailsView.as_view(), name='orders-client-orderandproductdetails'),
    path('client/withcutomerinfo/<str:id>', views.OrdersClientWithCustomerInfoView.as_view(), name='orders-client-withcustomerinfo'),
    path('client/<str:id>', views.OrdersClientRetrieveView.as_view(), name='orders-client-retrieve'),
    path('order-status/<str:id>', views.OrdersOrderStatusUpdateView.as_view(), name='orders-order-status'),
    path('order-item-status/<str:id>', views.OrdersOrderItemStatusUpdateView.as_view(), name='orders-order-item-status'),
] + urlpatterns

