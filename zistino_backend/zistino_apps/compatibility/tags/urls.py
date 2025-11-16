"""
URL patterns for Tags compatibility layer.
Provides all 8 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.TagsViewSet, basename='tags')

urlpatterns = [
    # Router URLs (handles: GET/POST /api/v1/tags, GET/PUT/DELETE /api/v1/tags/{id})
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dapper', views.TagsDapperView.as_view(), name='tags-dapper'),
    path('all', views.TagsAllView.as_view(), name='tags-all'),
    path('client/all', views.TagsClientAllView.as_view(), name='tags-client-all'),
]

