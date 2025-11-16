"""
Comments compatibility URL routes for Flutter apps.
All 16 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Comments

Flutter expects: /api/v1/comments/{endpoint}
All endpoints are tagged with 'Comments' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/comments/{id} - Retrieves a comment by its ID
2. PUT /api/v1/comments/{id} - Updates an existing comment by its ID
3. DELETE /api/v1/comments/{id} - Deletes a comment by its ID
4. GET /api/v1/comments/dapper - Get comments (dapper context)
5. POST /api/v1/comments/search - Search comments using available Filters
6. POST /api/v1/comments/searchadmin - Search comments using available Filters (admin)
7. POST /api/v1/comments - Creates a new comment
8. PUT /api/v1/comments/comment-status/{id} - Update comment status
9. POST /api/v1/comments/client - Create comment for client
10. POST /api/v1/comments/client/anonymous - Create anonymous comment
11. POST /api/v1/comments/client/search - Search comments for client
12. POST /api/v1/comments/client/searchrevers - Search comments in reverse order
13. POST /api/v1/comments/client/by-userid - Get comments by user ID
14. PUT /api/v1/comments/client/{id} - Update comment for client (uses standard PUT /api/v1/comments/{id})
15. DELETE /api/v1/comments/client/{id} - Delete comment for client (uses standard DELETE /api/v1/comments/{id})
16. POST /api/v1/comments/notifyme - Notify me about comments
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.CommentViewSet, basename='comment')

urlpatterns = [
    # ============================================================================
    # CLIENT ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    # ============================================================================
    
    # PUT/DELETE /api/v1/comments/client/{id} - Update/Delete comment for client
    path('client/<int:pk>', views.CommentClientDetailView.as_view(), name='comments-client-detail'),
    
    # ============================================================================
    # STANDARD REST ENDPOINTS (via router)
    # ============================================================================
    path('', include(router.urls)),
]

