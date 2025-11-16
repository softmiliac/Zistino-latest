"""
URL patterns for DriverDelivery compatibility layer.
Provides all 5 endpoints matching Flutter app expectations.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Custom endpoints (must come before detail routes to avoid conflicts)
    path('search', views.DriverDeliveryViewSet.as_view({'post': 'search'}), name='driverdelivery-search'),
    path('myrequests', views.DriverDeliveryMyRequestsView.as_view(), name='driverdelivery-myrequests'),
    
    # Custom routes for CRUD operations that accept both UUID and integer IDs (using <str:id> instead of <uuid:id>)
    path('<str:id>', views.DriverDeliveryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='driverdelivery-detail'),
    path('', views.DriverDeliveryViewSet.as_view({'get': 'list', 'post': 'create'}), name='driverdelivery-list'),
]

