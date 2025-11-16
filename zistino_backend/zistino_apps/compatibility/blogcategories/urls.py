"""
BlogCategories compatibility URL routes for Flutter apps.
All 9 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogCategories

Flutter expects: /api/v1/blogcategories/{endpoint}
Backend has: /api/v1/content/blogcategories/ (via router, but needs compatibility routes)

All endpoints are tagged with 'BlogCategories' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/blogcategories/{id} - Retrieves a blog category by its ID
2. PUT /api/v1/blogcategories/{id} - Updates an existing blog category by its ID
3. DELETE /api/v1/blogcategories/{id} - Deletes a blog category by its ID
4. GET /api/v1/blogcategories/dapper - Get blog categories (dapper context)
5. POST /api/v1/blogcategories/search - Search blog categories using available Filters
6. POST /api/v1/blogcategories - Creates a new blog category
7. GET /api/v1/blogcategories/all - Retrieves all blog categories
8. GET /api/v1/blogcategories/client/all - Retrieves all blog categories for client-side use
9. GET /api/v1/blogcategories/client/categories - Retrieves categories for client-side use
"""
from django.urls import path
from . import views as blogcategories_views

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS (Must come before {id} routes to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/blogcategories/client/categories - Get categories for client
    path('client/categories', blogcategories_views.BlogCategoriesClientCategoriesView.as_view(), name='blogcategories-client-categories'),
    
    # GET /api/v1/blogcategories/client/all - Get all blog categories for client
    path('client/all', blogcategories_views.BlogCategoriesClientAllView.as_view(), name='blogcategories-client-all'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/blogcategories/dapper - Get blog categories (dapper context)
    path('dapper', blogcategories_views.BlogCategoriesDapperView.as_view(), name='blogcategories-dapper'),
    
    # POST /api/v1/blogcategories/search - Search blog categories
    path('search', blogcategories_views.BlogCategoriesSearchView.as_view(), name='blogcategories-search'),
    
    # GET /api/v1/blogcategories/all - Get all blog categories
    path('all', blogcategories_views.BlogCategoriesAllView.as_view(), name='blogcategories-all'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS WITH ID
    # ============================================================================
    
    # GET /api/v1/blogcategories/{id} - Get blog category by ID
    # PUT /api/v1/blogcategories/{id} - Update blog category by ID
    # DELETE /api/v1/blogcategories/{id} - Delete blog category by ID
    path('<int:id>', blogcategories_views.BlogCategoriesDetailView.as_view(), name='blogcategories-detail'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (Must come last)
    # ============================================================================
    
    # GET /api/v1/blogcategories/ - List all blog categories
    # POST /api/v1/blogcategories - Create a new blog category
    path('', blogcategories_views.BlogCategoriesListView.as_view(), name='blogcategories-list-create'),
]

