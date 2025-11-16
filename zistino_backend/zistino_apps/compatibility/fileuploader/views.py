"""
Compatibility views for FileUploader endpoints.
All endpoints will appear under "FileUploader" folder in Swagger UI.

Based on Flutter Swagger: https://recycle.metadatads.com/swagger/index.html#/FileUploader
"""
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from zistino_apps.users.permissions import IsManager
import base64
import os
import secrets
import string
from django.conf import settings
from django.utils import timezone

from zistino_apps.compatibility.utils import create_success_response, create_error_response
from .serializers import (
    FileUploaderSerializer,
    FileUploadRequestSerializer,
    FileGroupNameRequestSerializer,
    FileGenerateTokenRequestSerializer,
    FileByTokenResponseSerializer
)


@extend_schema(tags=['FileUploader'])
class FileUploaderViewSet(viewsets.ViewSet):
    """
    ViewSet for file uploader operations.
    All endpoints will appear under "FileUploader" folder in Swagger UI.
    
    Note: This is a placeholder implementation. File upload functionality needs to be implemented.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Authenticated users for upload, AllowAny for public file access."""
        if self.action in ['create', 'list', 'groupname', 'generatetoken']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        tags=['FileUploader'],
        operation_id='fileuploader_create',
        summary='Upload a file',
        description='Upload a new file matching old Swagger format. Accepts folder name as query parameter.',
        parameters=[
            OpenApiParameter(
                name='folder',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Folder name'
            )
        ],
        request=FileUploadRequestSerializer,
        examples=[
            OpenApiExample(
                'Upload file',
                value={
                    'file': 'file content'
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
                            'data': [{
                                'id': 1,
                                'fileName': 'example.jpg',
                                'fileUrl': '/media/uploads/20251109_123456_123456_example.jpg',
                                'fileSize': 1024,
                                'mimeType': 'image/jpeg',
                                'token': None,
                                'folder': None,
                                'groupName': None,
                                'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                                'createdAt': '2025-11-09T12:34:56.789Z'
                            }],
                            'messages': ['/media/uploads/20251109_123456_123456_example.jpg'],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    def create(self, request):
        """Upload a new file matching old Swagger format. Accepts folder name as query parameter."""
        try:
            # Get folder from query parameter (not from request body)
            folder = request.query_params.get('folder', '')
            
            # Handle both multipart/form-data (file upload) and JSON
            file_obj = request.FILES.get('file')
            
            # If no file uploaded, return success with empty message (matching old Swagger)
            if not file_obj:
                return create_success_response(data=[], messages=[''])
            
            # Generate file path
            file_extension = os.path.splitext(file_obj.name)[1] or ''
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S_%f')
            safe_filename = f"{timestamp}_{file_obj.name}"
            
            # Save file to media/uploads directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            if folder:
                upload_dir = os.path.join(upload_dir, folder)
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, safe_filename)
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            
            # Generate file URL
            if folder:
                file_url = f"/media/uploads/{folder}/{safe_filename}"
            else:
                file_url = f"/media/uploads/{safe_filename}"
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Get MIME type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Create file data object matching FileUploaderSerializer structure
            # Since we don't have a File model yet, we'll use a placeholder ID
            # The ID will be based on the file index in the uploads directory
            upload_dir_base = os.path.join(settings.MEDIA_ROOT, 'uploads')
            if folder:
                upload_dir_base = os.path.join(upload_dir_base, folder)
            
            # Count existing files to generate an ID
            file_count = 0
            if os.path.exists(upload_dir_base):
                for f in os.listdir(upload_dir_base):
                    if os.path.isfile(os.path.join(upload_dir_base, f)):
                        file_count += 1
            
            file_data = {
                'id': file_count,  # Placeholder ID based on file count
                'fileName': file_obj.name,
                'fileUrl': file_url,
                'fileSize': file_size,
                'mimeType': mime_type,
                'token': None,  # Token will be generated when generatetoken endpoint is called
                'folder': folder if folder else None,
                'groupName': None,  # Will be set when groupname endpoint is called
                'userId': str(request.user.id) if request.user.is_authenticated else None,
                'createdAt': timezone.now().isoformat()
            }
            
            # Return response matching old Swagger format with file data
            return create_success_response(data=[file_data], messages=[file_url])
        
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
        tags=['FileUploader'],
        operation_id='fileuploader_list',
        summary='Get list of files',
        description='Get list of uploaded files matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='List of files',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [],
                            'messages': ['string'],
                            'succeeded': True
                        }
                    )
                ]
            )
        }
    )
    def list(self, request):
        """Get list of uploaded files matching old Swagger format."""
        # TODO: When File model is created, implement:
        # from zistino_apps.files.models import File
        # files = File.objects.filter(user=request.user).order_by('-created_at')
        # serializer = FileUploaderSerializer(files, many=True)
        # return create_success_response(data=serializer.data, messages=[''])

        # Placeholder response matching old Swagger format
        return create_success_response(data=[], messages=[''])

    @extend_schema(
        tags=['FileUploader'],
        operation_id='fileuploader_groupname',
        summary='Group files by name',
        description='Group files by group name matching old Swagger format. Accepts folder and groupName as query parameters.',
        parameters=[
            OpenApiParameter(
                name='folder',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Folder name'
            ),
            OpenApiParameter(
                name='groupName',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Group name'
            )
        ],
        request=FileGroupNameRequestSerializer,
        examples=[
            OpenApiExample(
                'Group files',
                value={
                    'fileIds': [0]
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer,
                description='Files grouped successfully',
                examples=[
                    OpenApiExample(
                        'Success response',
                        value={
                            'data': [],
                            'messages': ['string'],
                            'succeeded': True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'}
        }
    )
    @action(detail=False, methods=['post'], url_path='groupname', permission_classes=[IsAuthenticated])
    def groupname(self, request):
        """Group files by group name matching old Swagger format. Accepts folder and groupName as query parameters."""
        try:
            # Get folder and groupName from query parameters (not from request body)
            folder = request.query_params.get('folder', '')
            group_name = request.query_params.get('groupName') or request.query_params.get('group_name')
            
            # Get fileIds from request body if provided
            file_ids = request.data.get('fileIds', []) if request.data else []

            if not group_name:
                return create_error_response(
                    error_message='groupName is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'groupName': ['groupName is required.']}
                )

            # TODO: When File model is created, implement:
            # from zistino_apps.files.models import File
            # files = File.objects.filter(id__in=file_ids, user=request.user, folder=folder)
            # files.update(groupName=group_name)
            # return create_success_response(data=[], messages=['Files grouped successfully'])

            # Placeholder response matching old Swagger format
            return create_success_response(data=[], messages=[''])
        
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
    tags=['FileUploader'],
    operation_id='fileuploader_generatetoken',
    summary='Generate token for file',
    description='Generate a token for secure file access matching old Swagger format. Returns token string directly.',
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
            description='Token generated successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value='8cVuwcHF7Jx7pHXdIaq33%2F5gW8pcnvrMp%2BSSpbhCbcyC2ug4JgGoSFLxy%2FzzVjcg%2BLbiQWbI5uRO0%2BxedseN9bY7f2yr1YE4LsyGu2XPMJAQmIiZ0Qv3MKzmy2G1J7T4'
                )
            ]
        ),
        400: {'description': 'Validation error'},
        404: {'description': 'File not found'}
    }
)
class FileUploaderGenerateTokenView(APIView):
    """GET /api/v1/fileuploader/generatetoken/{id} - Generate token for file"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Generate a token for a file by file ID matching old Swagger format. Returns token string directly."""
        try:
            # TODO: When File model is created, implement:
            # from zistino_apps.files.models import File
            # import uuid
            # import datetime
            # try:
            #     file_instance = File.objects.get(pk=id)
            #     # Check permissions (user owns file or is admin)
            #     if file_instance.user != request.user and not request.user.is_staff:
            #         return Response('Permission denied.', status=status.HTTP_403_FORBIDDEN)
            #     
            #     # Generate token (URL-encoded format like old Swagger)
            #     import urllib.parse
            #     token = str(uuid.uuid4())
            #     expires_at = datetime.datetime.now() + datetime.timedelta(seconds=3600)
            #     file_instance.token = token
            #     file_instance.token_expires_at = expires_at
            #     file_instance.save()
            #     
            #     # Return token as URL-encoded string
            #     encoded_token = urllib.parse.quote(token, safe='')
            #     return Response(encoded_token, status=status.HTTP_200_OK)
            # except File.DoesNotExist:
            #     return Response('File not found.', status=status.HTTP_404_NOT_FOUND)

            # Generate a placeholder token (URL-encoded format like old Swagger)
            import urllib.parse
            # Generate a longer token similar to the example
            token_chars = string.ascii_letters + string.digits + '/+'
            token = ''.join(secrets.choice(token_chars) for _ in range(128))
            # URL encode the token
            encoded_token = urllib.parse.quote(token, safe='')
            
            # Return token string directly (not wrapped in JSON response)
            return Response(encoded_token, status=status.HTTP_200_OK, content_type='text/plain')
        
        except Exception as e:
            # Catch any unexpected errors and return proper error response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )


@extend_schema(
    tags=['FileUploader'],
    operation_id='fileuploader_file_by_token',
    summary='Get file by token',
    description='Get file information or download file using a token matching old Swagger format.',
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description='File access token'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=serializers.Serializer,
            description='File information',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={
                        'data': [],
                        'messages': ['string'],
                        'succeeded': True
                    }
                )
            ]
        ),
        404: {'description': 'File not found or token invalid'}
    }
)
class FileUploaderFileByTokenView(APIView):
    """GET /api/v1/fileuploader/file/{token} - Get file by token"""
    permission_classes = [AllowAny]  # Public access with valid token

    def get(self, request, token):
        """Get file by token (public access) matching old Swagger format."""
        try:
            # TODO: When File model is created, implement:
            # from zistino_apps.files.models import File
            # from django.http import FileResponse
            # import datetime
            # try:
            #     file_instance = File.objects.get(token=token)
            #     
            #     # Check if token is expired
            #     if file_instance.token_expires_at and file_instance.token_expires_at < datetime.datetime.now():
            #         return create_error_response(
            #             error_message='Token expired.',
            #             status_code=status.HTTP_401_UNAUTHORIZED,
            #             errors={'token': ['Token expired.']}
            #         )
            #     
            #     # Return file information
            #     serializer = FileByTokenResponseSerializer(file_instance)
            #     return create_success_response(data=[serializer.data], messages=[''])
            #     
            #     # Or return file download:
            #     # return FileResponse(file_instance.file.open(), as_attachment=True, filename=file_instance.fileName)
            # except File.DoesNotExist:
            #     return create_error_response(
            #         error_message='File not found or token invalid.',
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         errors={'token': ['File not found or token invalid.']}
            #     )

            # Placeholder response matching old Swagger format
            return create_success_response(data=[], messages=[''])
        
        except Exception as e:
            # Catch any unexpected errors and return proper JSON response
            error_detail = str(e)
            error_type = type(e).__name__
            
            return create_error_response(
                error_message=f'An error occurred while processing the request: {error_detail}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [f'{error_type}: {error_detail}']}
            )

