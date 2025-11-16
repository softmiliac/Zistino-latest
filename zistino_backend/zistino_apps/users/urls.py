from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomerAddressViewSet, AdminUserSearchView

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'customer/addresses', CustomerAddressViewSet, basename='customer-addresses')
router.register(r'vehicles', views.VehicleViewSet, basename='vehicle')

urlpatterns = [
    path('', include(router.urls)),
    path('profile', views.UserProfileView.as_view(), name='user-profile'),
    path('upload-image', views.UploadProfileImageView.as_view(), name='upload-profile-image'),
    path('search', AdminUserSearchView.as_view(), name='admin-users-search'),
]
