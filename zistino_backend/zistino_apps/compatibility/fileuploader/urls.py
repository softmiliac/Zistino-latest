"""
FileUploader compatibility URL routes for Flutter apps.
All 5 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/FileUploader

Flutter expects: /api/v1/fileuploader/{endpoint}
All endpoints are tagged with 'FileUploader' to appear grouped in Swagger UI.

Endpoints:
1. POST /api/v1/fileuploader - Upload/create a file
2. GET /api/v1/fileuploader - Get list of files
3. POST /api/v1/fileuploader/groupname - Group files by name
4. POST /api/v1/fileuploader/generatetoken/{fileid} - Generate token for a file
5. GET /api/v1/fileuploader/file/{token} - Get file by token (public access)

Note: File upload functionality needs to be implemented.
These are placeholder endpoints.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.FileUploaderViewSet, basename='fileuploader')

urlpatterns = [
    # SPECIAL ENDPOINTS WITH PATH PARAMETERS (Must come before router to avoid conflicts)
    path('generatetoken/<int:id>', views.FileUploaderGenerateTokenView.as_view(), name='fileuploader-generate-token'),
    path('file/<str:token>', views.FileUploaderFileByTokenView.as_view(), name='fileuploader-file-by-token'),
    
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

