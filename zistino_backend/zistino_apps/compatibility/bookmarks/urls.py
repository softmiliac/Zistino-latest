"""
Bookmarks compatibility URL routes for Flutter apps.
All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Bookmarks

Flutter expects: /api/v1/bookmarks/{endpoint}
All endpoints are tagged with 'Bookmarks' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/bookmarks/{id} - Retrieves a bookmark by its ID
2. PUT /api/v1/bookmarks/{id} - Updates an existing bookmark by its ID
3. DELETE /api/v1/bookmarks/{id} - Deletes a bookmark by its ID
4. GET /api/v1/bookmarks/dapper - Get bookmarks (dapper context)
5. POST /api/v1/bookmarks/search - Search bookmarks using available Filters
6. POST /api/v1/bookmarks - Creates a new bookmark
7. GET /api/v1/bookmarks/client - Get Bookmarks of currently logged in user
8. POST /api/v1/bookmarks/client - Set Bookmark for currently logged in user
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('', include(router.urls)),
]

