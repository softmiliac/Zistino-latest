"""
FileManager compatibility URL routes for Flutter apps.
All 6 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/FileManager

Flutter expects: /api/v1/filemanager/{endpoint}
All endpoints are tagged with 'FileManager' to appear grouped in Swagger UI.

Endpoints:
1. POST /api/v1/filemanager/search - Search Tags using available Filters
2. POST /api/v1/filemanager - Upload/create a file
3. DELETE /api/v1/filemanager/{id} - Delete a file by ID
4. GET /api/v1/filemanager/download-by-id - Download file by ID (query param: id)
5. GET /api/v1/filemanager/getuserfilelist - Get user file list (query param: userId)
6. GET /api/v1/filemanager/getmyfilelists - Get my file lists (for authenticated user)

Note: File management functionality needs to be implemented.
These are placeholder endpoints.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.FileManagerViewSet, basename='filemanager')

urlpatterns = [
    # SPECIAL ENDPOINTS (Must come before router to avoid conflicts)
    path('download-by-id', views.FileManagerDownloadByIdView.as_view(), name='filemanager-download-by-id'),
    path('getuserfilelist', views.FileManagerGetUserFileListView.as_view(), name='filemanager-get-user-file-list'),
    path('getmyfilelists', views.FileManagerGetMyFileListsView.as_view(), name='filemanager-get-my-file-lists'),
    
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

