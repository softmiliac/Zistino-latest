from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'deliveries', views.DeliveryViewSet, basename='delivery')
router.register(r'trips', views.TripViewSet, basename='trip')
router.register(r'locations', views.LocationUpdateViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
    # Delivery reminder endpoints
    path('reminder-check', views.DeliveryReminderCheckView.as_view(), name='delivery-reminder-check'),
]
