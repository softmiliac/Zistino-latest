"""
Faqs compatibility URL routes for Flutter apps.
All 10 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Faqs

Flutter expects: /api/v1/faqs/{endpoint}
All endpoints are tagged with 'Faqs' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/faqs/{id} - Retrieves a FAQ by its ID
2. PUT /api/v1/faqs/{id} - Updates an existing FAQ by its ID
3. DELETE /api/v1/faqs/{id} - Deletes a FAQ by its ID
4. GET /api/v1/faqs/dapper - Get FAQs in dapper context
5. POST /api/v1/faqs/search - Search FAQs using available Filters
6. POST /api/v1/faqs - Creates a new FAQ
7. GET /api/v1/faqs/by-categoryid/{id} - Get FAQs by category ID
8. POST /api/v1/faqs/client/searchex - Client extended search
9. POST /api/v1/faqs/client/search - Client search
10. POST /api/v1/faqs/client/search/{take} - Client search with take parameter
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.FaqViewSet, basename='faq')

urlpatterns = [
    # CLIENT ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    path('by-categoryid/<int:id>', views.FaqsByCategoryIdView.as_view(), name='faqs-by-categoryid'),
    path('client/search/<int:take>', views.FaqsClientSearchTakeView.as_view(), name='faqs-client-search-take'),
    
    # CLIENT ENDPOINTS (Must come before router to avoid conflicts)
    path('client/searchex', views.FaqsClientSearchExView.as_view(), name='faqs-client-searchex'),
    path('client/search', views.FaqsClientSearchView.as_view(), name='faqs-client-search'),
    
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

