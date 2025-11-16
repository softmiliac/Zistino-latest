"""
URL patterns for ContactUsMessages compatibility layer.
Provides all endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ContactUsMessagesViewSet, basename='contactusmessages')

urlpatterns = [
    # Custom endpoints (must come before router to avoid conflicts)
    path('search', views.ContactUsMessagesViewSet.as_view({'post': 'search'}), name='contactusmessages-search'),
    path('client', views.ContactUsMessagesClientCreateView.as_view(), name='contactusmessages-client-create'),
    path('anonymous-client', views.ContactUsMessagesAnonymousClientCreateView.as_view(), name='contactusmessages-anonymous-client-create'),
    
    # Router URLs (handles: GET/POST /api/v1/contactusmessages, GET/PUT/DELETE /api/v1/contactusmessages/{id})
    path('', include(router.urls)),
]

