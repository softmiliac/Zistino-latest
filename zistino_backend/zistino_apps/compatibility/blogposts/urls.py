"""
BlogPosts compatibility URL routes for Flutter apps.
All endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogPosts

Flutter expects: /api/v1/blogposts/{endpoint}
Backend has: /api/v1/content/blogposts/ (via router, but needs compatibility routes)

All endpoints are tagged with 'BlogPosts' to appear grouped in Swagger UI.
"""
from django.urls import path
from . import views as blogposts_views

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS (Must come before {id} routes to avoid conflicts)
    # ============================================================================
    
    # GET /api/v1/blogposts/client/byslug/{slug} - Get blog post by slug for client
    path('client/byslug/<slug:slug>', blogposts_views.BlogPostsClientBySlugView.as_view(), name='blogposts-client-byslug'),
    
    # GET /api/v1/blogposts/client/recents/{count} - Get recent blog posts for client
    path('client/recents/<int:count>', blogposts_views.BlogPostsClientRecentsView.as_view(), name='blogposts-client-recents'),
    
    # POST /api/v1/blogposts/client/search - Search blog posts for client
    path('client/search', blogposts_views.BlogPostsClientSearchView.as_view(), name='blogposts-client-search'),
    
    # ============================================================================
    # SPECIAL ENDPOINTS
    # ============================================================================
    
    # GET /api/v1/blogposts/by-parentid/{id} - Get blog posts by parent/category ID
    path('by-parentid/<int:id>', blogposts_views.BlogPostsByParentIdView.as_view(), name='blogposts-by-parentid'),
    
    # GET /api/v1/blogposts/dapper - Get blog posts (dapper context)
    path('dapper', blogposts_views.BlogPostsDapperView.as_view(), name='blogposts-dapper'),
    
    # GET /api/v1/blogposts/all - Get all blog posts
    path('all', blogposts_views.BlogPostsAllView.as_view(), name='blogposts-all'),
    
    # ============================================================================
    # SEARCH ENDPOINTS
    # ============================================================================
    
    # POST /api/v1/blogposts/search - Search blog posts (admin)
    path('search', blogposts_views.BlogPostsSearchView.as_view(), name='blogposts-search'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS WITH ID
    # ============================================================================
    
    # GET /api/v1/blogposts/{id} - Get blog post by ID
    # PUT /api/v1/blogposts/{id} - Update blog post by ID
    # DELETE /api/v1/blogposts/{id} - Delete blog post by ID
    path('<int:id>', blogposts_views.BlogPostsDetailView.as_view(), name='blogposts-detail'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (Must come last)
    # ============================================================================
    
    # GET /api/v1/blogposts/ - List all blog posts
    # POST /api/v1/blogposts - Create a new blog post
    path('', blogposts_views.BlogPostsListView.as_view(), name='blogposts-list-create'),
]

