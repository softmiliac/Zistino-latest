from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db.models import Q
from zistino_apps.users.permissions import IsManager

from .models import Notification, Comment
from .serializers import NotificationSerializer, CommentSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    tags=['Admin'],
    operation_id='comments_client_search',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pageNumber': {'type': 'integer', 'default': 1},
                'pageSize': {'type': 'integer', 'default': 5},
                'keyword': {'type': 'string', 'default': ''},
            }
        }
    },
    examples=[
        OpenApiExample(
            'Search all comments',
            value={
                'pageNumber': 1,
                'pageSize': 5,
                'keyword': ''
            }
        ),
        OpenApiExample(
            'Search by keyword',
            value={
                'pageNumber': 1,
                'pageSize': 5,
                'keyword': 'excellent'
            }
        )
    ]
)
class AdminCommentSearchView(APIView):
    """Admin search endpoint for comments."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search comments with pagination."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 5)
        keyword = (request.data.get('keyword') or '').strip()

        qs = Comment.objects.all().select_related('user', 'product', 'parent').order_by('-created_on')

        if keyword:
            qs = qs.filter(
                Q(text__icontains=keyword) |
                Q(user_full_name__icontains=keyword) |
                Q(user__phone_number__icontains=keyword) |
                Q(user__username__icontains=keyword)
            )

        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        total = qs.count()
        total_pages = (total + page_size - 1) // page_size

        return Response({
            'data': CommentSerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': total,
            'totalPages': total_pages,
            'hasNextPage': page_number < total_pages,
            'hasPreviousPage': page_number > 1,
        })
