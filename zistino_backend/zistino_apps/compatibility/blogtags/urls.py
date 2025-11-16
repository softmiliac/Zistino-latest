"""
BlogTags compatibility URL routes for Flutter apps.
All endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogTags

Flutter expects: /api/v1/blogtags/{endpoint}
Backend has: /api/v1/content/blogtags/ (via router, but needs compatibility routes)

All endpoints are tagged with 'BlogTags' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/blogtags/{id} - Retrieves a blog tag by its ID
2. PUT /api/v1/blogtags/{id} - Updates an existing blog tag by its ID
3. DELETE /api/v1/blogtags/{id} - Deletes a blog tag by its ID
4. GET /api/v1/blogtags/dapper - Get blog tags (dapper context)
5. POST /api/v1/blogtags/search - Search blog tags using available Filters
6. GET /api/v1/blogtags/ - List all blog tags
7. POST /api/v1/blogtags - Creates a new blog tag
8. GET /api/v1/blogtags/all - Retrieves all blog tags
9. GET /api/v1/blogtags/client/all - Retrieves all blog tags for client-side use
"""
from django.urls import path
from . import views as blogtags_views

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS (Must come before {id} routes to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/blogtags/client/all - Get all blog tags for client
    path('client/all', blogtags_views.BlogTagsClientAllView.as_view(), name='blogtags-client-all'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/blogtags/dapper - Get blog tags (dapper context)
    path('dapper', blogtags_views.BlogTagsDapperView.as_view(), name='blogtags-dapper'),
    
    # POST /api/v1/blogtags/search - Search blog tags
    path('search', blogtags_views.BlogTagsSearchView.as_view(), name='blogtags-search'),
    
    # GET /api/v1/blogtags/all - Get all blog tags
    path('all', blogtags_views.BlogTagsAllView.as_view(), name='blogtags-all'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS WITH ID
    # ============================================================================
    
    # GET /api/v1/blogtags/{id} - Get blog tag by ID
    # PUT /api/v1/blogtags/{id} - Update blog tag by ID
    # DELETE /api/v1/blogtags/{id} - Delete blog tag by ID
    path('<int:id>', blogtags_views.BlogTagsDetailView.as_view(), name='blogtags-detail'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (Must come last)
    # ============================================================================
    
    # GET /api/v1/blogtags/ - List all blog tags
    # POST /api/v1/blogtags - Create a new blog tag
    path('', blogtags_views.BlogTagsListView.as_view(), name='blogtags-list-create'),
]

