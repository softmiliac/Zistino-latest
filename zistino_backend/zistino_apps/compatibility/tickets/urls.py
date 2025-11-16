"""
URL patterns for Tickets compatibility layer.
Provides all endpoints matching old Swagger format.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.TicketsViewSet, basename='tickets')

urlpatterns = [
    # Custom endpoints (must come before router to avoid conflicts)
    path('dapper', views.TicketsDapperView.as_view(), name='tickets-dapper'),
    path('client/<int:id>', views.TicketsClientRetrieveView.as_view(), name='tickets-client-retrieve'),
    
    # Router URLs (handles: GET/POST /api/v1/tickets, GET/PUT/DELETE /api/v1/tickets/{id}, POST /api/v1/tickets/search, POST /api/v1/tickets/message, GET /api/v1/tickets/client, POST /api/v1/tickets/client/search, POST /api/v1/tickets/client/message)
    path('', include(router.urls)),
]

