"""
Compatibility views for FileManager endpoints.
All endpoints will appear under "FileManager" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/FileManager
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from zistino_apps.users.permissions import IsManager
import base64
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    FileSerializer,
    FileSearchRequestSerializer,
    FileDownloadRequestSerializer,
    FileUploadRequestSerializer,
    FileDetailSerializer
)


@extend_schema(tags=['FileManager'])
class FileManagerViewSet(viewsets.ViewSet):
    """
    ViewSet for managing files.
    All endpoints will appear under "FileManager" folder in Swagger UI.
    
    Note: This is a placeholder implementation. File management needs to be implemented.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Admin-only for all operations."""
        return [IsAuthenticated(), IsManager()]

    @extend_schema(
        tags=['FileManager'],
        operation_id='filemanager_list',
        summary='Get list of all uploaded files',
        description='Get list of all uploaded files matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of files',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [{
                                'id': 1,
                                'fileName': 'example.jpg',
                                'fileUrl': '/media/uploads/20251109_123456_123456_example.jpg',
                                'fileSize': 1024,
                                'mimeType': 'image/jpeg',
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'createdAt': '2025-11-09T12:34:56.789Z'
                            }],
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def list(self, request):
        """Get list of all uploaded files matching old Swagger format."""
        try:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            
            if not os.path.exists(upload_dir):
                return create_success_response(data=[], messages=[])
            
            # List all files in uploads directory
            files_data = []
            files = []
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    files.append((filename, file_path))
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
            
            # Get MIME type helper
            import mimetypes
            
            # Build file data for each file
            for index, (filename, file_path) in enumerate(files, start=1):
                file_size = os.path.getsize(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                
                # Get modification time as creation time
                mod_time = os.path.getmtime(file_path)
                created_at = timezone.datetime.fromtimestamp(mod_time, tz=timezone.get_current_timezone())
                
                file_data = {
                    'id': index,  # 1-based index
                    'fileName': filename,
                    'fileUrl': f"/media/uploads/{filename}",
                    'fileSize': file_size,
                    'mimeType': mime_type,
                    'userId': str(request.user.id) if request.user.is_authenticated else None,
                    'createdAt': created_at.isoformat()
                }
                files_data.append(file_data)
            
            # Return response matching old Swagger format
            return create_success_response(data=files_data, messages=[])
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['FileManager'],
        operation_id='filemanager_search',
        summary='Search Files using available Filters',
        description='Search Files using available Filters matching old Swagger format.',
        request=FileSearchRequestSerializer,
        examples=[
            OpenApiExample(
                'Search files',
                value={
                    'advancedSearch': {
                        'fields': ['string'],
                        'keyword': 'string',
                        'groupBy': ['string']
                    },
                    'keyword': 'string',
                    'pageNumber': 0,
                    'pageSize': 0,
                    'orderBy': ['string'],
                    'fromDate': '2025-11-09T19:41:02.787Z',
                    'toDate': '2025-11-09T19:41:02.787Z',
                    'folder': 'string'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Paginated search results',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [],
                            'currentPage': 1,
                            'totalPages': 0,
                            'totalCount': 0,
                            'pageSize': 1,
                            'hasPreviousPage': False,
                            'hasNextPage': False,
                            'messages': None,
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[IsAuthenticated, IsManager])
    def search(self, request):
        """Search files with pagination matching old Swagger format."""
        try:
            # Handle empty request body - request.data is read-only, so use get() or empty dict
            request_data = request.data if request.data else {}
            
            # Validate input
            serializer = FileSearchRequestSerializer(data=request_data)
            if not serializer.is_valid():
                errors = {}
                for field, error_list in serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters (can be 0)
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Get keyword from request or advancedSearch
            keyword = validated_data.get('keyword') or ''
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and advanced_search.get('keyword'):
                keyword = advanced_search.get('keyword') or keyword
            
            # TODO: When File model is created, implement actual search:
            # from zistino_apps.files.models import File
            # qs = File.objects.all().order_by('-created_at')
            # if keyword:
            #     qs = qs.filter(fileName__icontains=keyword.strip())
            # if from_date:
            #     qs = qs.filter(created_at__gte=from_date)
            # if to_date:
            #     qs = qs.filter(created_at__lte=to_date)
            # if folder:
            #     qs = qs.filter(folder=folder.strip())
            
            # For now, return empty paginated response
            total_count = 0
            items_data = []
            
            # Calculate pagination
            if page_size > 0:
                total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
                # Handle pageNumber 0 - treat as page 1
                effective_page = page_number if page_number > 0 else 1
                has_previous = effective_page > 1
                has_next = effective_page < total_pages
            else:
                # If pageSize is 0, return all results
                total_pages = 0
                effective_page = 1
                has_previous = False
                has_next = False
            
            # Build response matching old Swagger format
            # If pageSize is 0, show actual number of items returned (or 1 if empty, as per old Swagger example)
            response_page_size = page_size if page_size > 0 else (len(items_data) if items_data else 1)
            
            response_data = {
                'data': items_data,
                'currentPage': effective_page,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': response_page_size,
                'hasPreviousPage': has_previous,
                'hasNextPage': has_next,
                'messages': None,  # Old Swagger shows null, not empty array
                'succeeded': True
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['FileManager'],
        operation_id='filemanager_create',
        summary='Upload a file',
        description='Upload a new file matching old Swagger format.',
        request=FileUploadRequestSerializer,
        examples=[
            OpenApiExample(
                'Upload file',
                value={
                    'image': {
                        'name': 'string',
                        'extension': 'string',
                        'data': 'string'
                    }
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='File uploaded successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': None,
                            'messages': [''],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request):
        """Upload a new file matching old Swagger format."""
        try:
            # Validate input using old Swagger format serializer
            input_serializer = FileUploadRequestSerializer(data=request.data)
            if not input_serializer.is_valid():
                errors = {}
                for field, error_list in input_serializer.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return create_error_response(
                    error_message='Validation failed',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=errors
                )
            
            validated_data = input_serializer.validated_data
            image_data = validated_data.get('image', {})
            
            # Extract image information
            file_name = image_data.get('name', 'file')
            extension = image_data.get('extension', '')
            data_value = image_data.get('data', '')
            
            # Handle placeholder "string" value - return success with empty message
            if data_value == 'string' or not data_value or data_value.strip() == '':
                # Return success response with empty message (matching old Swagger format)
                return Response({
                    'data': None,
                    'messages': [''],
                    'succeeded': True
                }, status=status.HTTP_200_OK)
            
            file_content = None
            
            # Check if data is a file path (contains slashes) or base64 data
            if '/' in data_value or '\\' in data_value:
                # Try to read file from media directory
                file_path = data_value
                found_file_path = None
                
                if not os.path.isabs(file_path):
                    # Try different locations in order:
                    # 1. Directly in media root (e.g., "categories/boldAkm.jpg" -> media/categories/boldAkm.jpg)
                    media_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    if os.path.exists(media_file_path) and os.path.isfile(media_file_path):
                        found_file_path = media_file_path
                    else:
                        # 2. In uploads subdirectory (e.g., "categories/boldAkm.jpg" -> media/uploads/categories/boldAkm.jpg)
                        upload_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_path)
                        if os.path.exists(upload_file_path) and os.path.isfile(upload_file_path):
                            found_file_path = upload_file_path
                        else:
                            # 3. Just the filename in uploads (e.g., "boldAkm.jpg" -> media/uploads/boldAkm.jpg)
                            filename_only = os.path.basename(file_path)
                            upload_filename_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename_only)
                            if os.path.exists(upload_filename_path) and os.path.isfile(upload_filename_path):
                                found_file_path = upload_filename_path
                else:
                    # Absolute path
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        found_file_path = file_path
                
                if found_file_path:
                    try:
                        with open(found_file_path, 'rb') as f:
                            file_content = f.read()
                    except Exception as e:
                        return create_error_response(
                            error_message=f'Error reading file: {str(e)}',
                            status_code=status.HTTP_400_BAD_REQUEST,
                            errors={'image.data': [f'Error reading file: {str(e)}']}
                        )
                else:
                    return create_error_response(
                        error_message=f'File not found: {file_path}. Searched in: {os.path.join(settings.MEDIA_ROOT, file_path)}, {os.path.join(settings.MEDIA_ROOT, "uploads", file_path)}',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'image.data': [f'File not found: {file_path}']}
                    )
            else:
                # Try to decode as base64 data
                try:
                    # Remove data URL prefix if present (e.g., "data:image/png;base64,")
                    base64_data = data_value
                    if ',' in base64_data:
                        base64_data = base64_data.split(',')[1]
                    
                    file_content = base64.b64decode(base64_data)
                except Exception as e:
                    return create_error_response(
                        error_message='Invalid base64 data. If providing a file path, it should contain "/" or "\\". If providing base64 data, ensure it is valid base64 encoded.',
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'image.data': ['Invalid base64 data or file path not found. Provide either base64 encoded data or a valid file path relative to media directory (e.g., "categories/boldAkm.jpg").']}
                    )
            
            # Generate file path
            if extension and not extension.startswith('.'):
                extension = '.' + extension
            
            # Create filename with timestamp to avoid conflicts
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S_%f')
            safe_filename = f"{timestamp}_{file_name}{extension}"
            
            # Save file to media/uploads directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, safe_filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Generate file URL
            file_url = f"/media/uploads/{safe_filename}"
            
            # Return response matching old Swagger format
            # data: null, messages: [""] (empty string)
            return Response({
                'data': None,
                'messages': [''],
                'succeeded': True
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

    @extend_schema(
        tags=['FileManager'],
        operation_id='filemanager_delete',
        summary='Delete a file by ID',
        description='Delete a file by its ID matching old Swagger format.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='File ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='File deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': 1,
                            'messages': [],
                            'succeeded': True
                        }
                    )
                ]
            ),
            404: {'description': 'File not found'}
        }
    )
    def destroy(self, request, pk=None):
        """Delete a file by ID matching old Swagger format. Returns file ID."""
        try:
            if not pk:
                return create_error_response(
                    error_message='File ID is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'id': ['File ID is required.']}
                )
            
            try:
                file_id_int = int(pk)
            except (ValueError, TypeError):
                return create_error_response(
                    error_message='Invalid file ID.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'id': ['Invalid file ID.']}
                )

            # TODO: When File model is created, implement:
            # from zistino_apps.files.models import File
            # try:
            #     file_instance = File.objects.get(pk=file_id_int)
            #     # Check permissions (user owns file or is admin)
            #     if file_instance.user != request.user and not request.user.is_staff:
            #         return create_error_response(
            #             error_message='Permission denied.',
            #             status_code=status.HTTP_403_FORBIDDEN,
            #             errors={'permission': ['Permission denied.']}
            #         )
            #     file_instance.delete()
            #     return create_success_response(data=file_id_int)
            # except File.DoesNotExist:
            #     return create_error_response(
            #         error_message=f'File with ID "{file_id_int}" not found.',
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         errors={'id': [f'File with ID "{file_id_int}" not found.']}
            #     )

            # For now, try to find and delete file in media/uploads directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            
            if not os.path.exists(upload_dir):
                return create_error_response(
                    error_message=f'File with ID "{file_id_int}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'File with ID "{file_id_int}" not found.']}
                )
            
            # List all files in uploads directory
            files = []
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    files.append((filename, file_path))
            
            # Sort by modification time (newest first) and try to get file by index
            files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
            
            if file_id_int <= 0 or file_id_int > len(files):
                return create_error_response(
                    error_message=f'File with ID "{file_id_int}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'File with ID "{file_id_int}" not found.']}
                )
            
            # Get file by index (ID 1 = first file, ID 2 = second file, etc.)
            filename, file_path = files[file_id_int - 1]
            
            try:
                # Delete the file
                os.remove(file_path)
                return create_success_response(data=file_id_int)
            except (IOError, OSError) as e:
                return create_error_response(
                    error_message=f'Error deleting file: {str(e)}',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    errors={'file': [f'Error deleting file: {str(e)}']}
                )
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )


@extend_schema(
    tags=['FileManager'],
    operation_id='filemanager_download_by_id',
    summary='Download file by ID',
    description='Download a file by its ID matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=True,
            description='File ID'
        )
    ],
    responses={
        200: {
            'description': 'File content',
            'content': {'application/octet-stream': {}}
        },
        400: {'description': 'File ID is required'},
        404: {'description': 'File not found'}
    }
)
class FileManagerDownloadByIdView(APIView):
    """GET /api/v1/filemanager/download-by-id?id=1 - Download file by ID"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Download a file by ID (ID should be in query parameter) matching old Swagger format."""
        from django.http import FileResponse, Http404
        from django.core.files.storage import default_storage
        
        file_id = request.query_params.get('id')
        if not file_id:
            return create_error_response(
                error_message='File ID is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'id': ['File ID is required.']}
            )

        try:
            file_id_int = int(file_id)
        except (ValueError, TypeError):
            return create_error_response(
                error_message='Invalid file ID.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'id': ['Invalid file ID.']}
            )

        # TODO: When File model is created, implement:
        # from zistino_apps.files.models import File
        # try:
        #     file_instance = File.objects.get(pk=file_id_int)
        #     # Check permissions (user owns file or is admin)
        #     if file_instance.user != request.user and not request.user.is_staff:
        #         return create_error_response(
        #             error_message='Permission denied.',
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             errors={'permission': ['Permission denied.']}
        #         )
        #     file_path = file_instance.file.path
        #     filename = file_instance.fileName or file_instance.file.name
        #     mime_type = file_instance.mimeType or 'application/octet-stream'
        # except File.DoesNotExist:
        #     return create_error_response(
        #         error_message=f'File with ID "{file_id_int}" not found.',
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         errors={'id': [f'File with ID "{file_id_int}" not found.']}
        #     )

        # For now, try to find file in media/uploads directory by matching ID in filename
        # Files are saved with format: {timestamp}_{name}.{extension}
        # We'll search for files and try to match by ID (this is a workaround until File model exists)
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        
        if not os.path.exists(upload_dir):
            return create_error_response(
                error_message=f'File with ID "{file_id_int}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'File with ID "{file_id_int}" not found.']}
            )
        
        # List all files in uploads directory
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                files.append((filename, file_path))
        
        # Sort by modification time (newest first) and try to get file by index
        files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
        
        if file_id_int <= 0 or file_id_int > len(files):
            return create_error_response(
                error_message=f'File with ID "{file_id_int}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'File with ID "{file_id_int}" not found.']}
            )
        
        # Get file by index (ID 1 = first file, ID 2 = second file, etc.)
        filename, file_path = files[file_id_int - 1]
        
        try:
            # Determine MIME type from extension
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Open file and return as download
            file_obj = open(file_path, 'rb')
            response = FileResponse(
                file_obj,
                content_type=mime_type,
                as_attachment=True,
                filename=filename
            )
            
            # Set content-disposition header matching old Swagger format
            # Format: attachment; filename="filename"; filename*=UTF-8''encoded_filename
            from urllib.parse import quote
            encoded_filename = quote(filename.encode('utf-8'))
            response['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
            response['Content-Length'] = os.path.getsize(file_path)
            response['api-supported-versions'] = '1.0'
            
            return response
        
        except (IOError, OSError) as e:
            return create_error_response(
                error_message=f'Error reading file: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'file': [f'Error reading file: {str(e)}']}
            )


@extend_schema(
    tags=['FileManager'],
    operation_id='filemanager_get_user_file_list',
    summary='Get user file list',
    description='Get list of files for a specific user matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='userId',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='User ID (UUID)'
        ),
        OpenApiParameter(
            name='groupName',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Group name'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of files',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': [{
                            'domainEvents': [{
                                'triggeredOn': '2025-11-11T13:02:06.183Z'
                            }],
                            'id': 0,
                            'createdBy': 'string',
                            'userId': 'string',
                            'createDate': '2025-11-11T13:02:06.183Z',
                            'fileName': 'string',
                            'fileExtention': 'string',
                            'fileInternalName': 'string',
                            'originalPath': 'string',
                            'originalSize': 0,
                            'webPPath': 'string',
                            'thumbnailPath': 'string',
                            'groupName': 'string'
                        }]
                    }
                )
            ]
        ),
        400: {'description': 'User ID and groupName are required'}
    }
)
class FileManagerGetUserFileListView(APIView):
    """GET /api/v1/filemanager/getuserfilelist - Get user file list matching old Swagger format"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get list of files for a specific user matching old Swagger format."""
        user_id = request.query_params.get('userId') or request.query_params.get('user_id')
        group_name = request.query_params.get('groupName') or request.query_params.get('group_name')
        
        if not user_id:
            return create_error_response(
                error_message='User ID is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'userId': ['User ID is required.']}
            )
        
        if not group_name:
            return create_error_response(
                error_message='Group name is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'groupName': ['Group name is required.']}
            )

        # TODO: When File model is created, implement:
        # from zistino_apps.files.models import File
        # files = File.objects.filter(user_id=user_id, group_name=group_name).order_by('-created_at')
        
        # For now, search for files in media directory that match the groupName pattern
        files_data = []
        
        try:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            media_root = settings.MEDIA_ROOT
            
            # Search for files that might match the groupName
            potential_folders = []
            
            # Check in uploads directory
            if os.path.exists(upload_dir):
                # Check if there's a folder matching groupName
                group_folder = os.path.join(upload_dir, group_name)
                if os.path.exists(group_folder) and os.path.isdir(group_folder):
                    potential_folders.append(group_folder)
                else:
                    # Search all files in uploads
                    potential_folders.append(upload_dir)
            
            # Also check in media root for folders matching groupName
            if os.path.exists(media_root):
                group_folder_root = os.path.join(media_root, group_name)
                if os.path.exists(group_folder_root) and os.path.isdir(group_folder_root):
                    potential_folders.append(group_folder_root)
            
            # Collect files from potential folders
            all_files = []
            for folder in potential_folders:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            # Get file stats
                            file_size = os.path.getsize(file_path)
                            mod_time = os.path.getmtime(file_path)
                            created_at = timezone.datetime.fromtimestamp(mod_time, tz=timezone.get_current_timezone())
                            
                            # Get relative path for fileUrl
                            if folder == upload_dir:
                                file_url = f"/media/uploads/{filename}"
                            elif folder.startswith(media_root):
                                rel_path = os.path.relpath(file_path, media_root)
                                file_url = f"/media/{rel_path.replace(os.sep, '/')}"
                            else:
                                file_url = f"/media/{filename}"
                            
                            # Get file extension
                            file_ext = os.path.splitext(filename)[1] or ''
                            
                            # Build file detail matching old Swagger format
                            file_data = {
                                'domainEvents': [{
                                    'triggeredOn': created_at.isoformat()
                                }],
                                'id': len(all_files) + 1,  # Sequential ID
                                'createdBy': user_id,
                                'userId': user_id,
                                'createDate': created_at.isoformat(),
                                'fileName': filename,
                                'fileExtention': file_ext,
                                'fileInternalName': filename,
                                'originalPath': file_url,
                                'originalSize': file_size,
                                'webPPath': None,
                                'thumbnailPath': None,
                                'groupName': group_name
                            }
                            all_files.append(file_data)
            
            # Sort by creation date (newest first)
            all_files.sort(key=lambda x: x['createDate'], reverse=True)
            files_data = all_files
            
        except Exception as e:
            # If there's an error, just return empty list
            files_data = []
        
        # Return response matching old Swagger format
        return Response({
            'messages': [''],
            'succeeded': True,
            'data': files_data
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['FileManager'],
    operation_id='filemanager_get_my_file_lists',
    summary='Get my file lists',
    description='Get list of files for the currently authenticated user matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='groupName',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Group name'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='List of files',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'messages': ['string'],
                        'succeeded': True,
                        'data': [{
                            'domainEvents': [{
                                'triggeredOn': '2025-11-11T13:03:26.875Z'
                            }],
                            'id': 0,
                            'createdBy': 'string',
                            'userId': 'string',
                            'createDate': '2025-11-11T13:03:26.875Z',
                            'fileName': 'string',
                            'fileExtention': 'string',
                            'fileInternalName': 'string',
                            'originalPath': 'string',
                            'originalSize': 0,
                            'webPPath': 'string',
                            'thumbnailPath': 'string',
                            'groupName': 'string'
                        }]
                    }
                )
            ]
        ),
        400: {'description': 'Group name is required'}
    }
)
class FileManagerGetMyFileListsView(APIView):
    """GET /api/v1/filemanager/getmyfilelists - Get my file lists matching old Swagger format"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of files for the currently authenticated user matching old Swagger format."""
        group_name = request.query_params.get('groupName') or request.query_params.get('group_name')
        
        if not group_name:
            return create_error_response(
                error_message='Group name is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={'groupName': ['Group name is required.']}
            )
        
        # TODO: When File model is created, implement:
        # from zistino_apps.files.models import File
        # files = File.objects.filter(user=request.user, group_name=group_name).order_by('-created_at')
        
        # For now, search for files in media directory that match the groupName pattern
        # groupName might correspond to a folder name or be used as a filter
        files_data = []
        
        try:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            media_root = settings.MEDIA_ROOT
            
            # Search for files that might match the groupName
            # Check if groupName corresponds to a folder name
            potential_folders = []
            
            # Check in uploads directory
            if os.path.exists(upload_dir):
                # Check if there's a folder matching groupName
                group_folder = os.path.join(upload_dir, group_name)
                if os.path.exists(group_folder) and os.path.isdir(group_folder):
                    potential_folders.append(group_folder)
                else:
                    # Search all files in uploads
                    potential_folders.append(upload_dir)
            
            # Also check in media root for folders matching groupName
            if os.path.exists(media_root):
                group_folder_root = os.path.join(media_root, group_name)
                if os.path.exists(group_folder_root) and os.path.isdir(group_folder_root):
                    potential_folders.append(group_folder_root)
            
            # Collect files from potential folders
            all_files = []
            for folder in potential_folders:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            # Get file stats
                            file_size = os.path.getsize(file_path)
                            mod_time = os.path.getmtime(file_path)
                            created_at = timezone.datetime.fromtimestamp(mod_time, tz=timezone.get_current_timezone())
                            
                            # Get relative path for fileUrl
                            if folder == upload_dir:
                                file_url = f"/media/uploads/{filename}"
                            elif folder.startswith(media_root):
                                rel_path = os.path.relpath(file_path, media_root)
                                file_url = f"/media/{rel_path.replace(os.sep, '/')}"
                            else:
                                file_url = f"/media/{filename}"
                            
                            # Get file extension
                            file_ext = os.path.splitext(filename)[1] or ''
                            
                            # Build file detail matching old Swagger format
                            file_data = {
                                'domainEvents': [{
                                    'triggeredOn': created_at.isoformat()
                                }],
                                'id': len(all_files) + 1,  # Sequential ID
                                'createdBy': str(request.user.id) if request.user.is_authenticated else None,
                                'userId': str(request.user.id) if request.user.is_authenticated else None,
                                'createDate': created_at.isoformat(),
                                'fileName': filename,
                                'fileExtention': file_ext,
                                'fileInternalName': filename,
                                'originalPath': file_url,
                                'originalSize': file_size,
                                'webPPath': None,
                                'thumbnailPath': None,
                                'groupName': group_name
                            }
                            all_files.append(file_data)
            
            # Sort by creation date (newest first)
            all_files.sort(key=lambda x: x['createDate'], reverse=True)
            files_data = all_files
            
        except Exception as e:
            # If there's an error, just return empty list
            files_data = []
        
        # Return response matching old Swagger format
        return Response({
            'messages': [''],
            'succeeded': True,
            'data': files_data
        }, status=status.HTTP_200_OK)

