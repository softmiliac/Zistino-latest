"""
URL configuration for zistino_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from zistino_apps.products import views as products_views
from zistino_apps.users import views as users_views
from zistino_apps.deliveries import views as deliveries_views
from zistino_apps.payments import views as payments_views
from zistino_apps.notifications import views as notifications_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI schema and Swagger/Redoc docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/', include([
        path('auth/', include('zistino_apps.authentication.urls')),
        # Compatibility routes for Flutter apps (backward compatibility)
        # IMPORTANT: These must come BEFORE original routes to take precedence
        path('', include('zistino_apps.compatibility.urls')),
        # Original routes (kept for backward compatibility, but excluded from Swagger)
        path('users', include('zistino_apps.users.urls')),
        path('orders', include('zistino_apps.orders.urls')),
        path('products', include('zistino_apps.products.urls')),
        path('deliveries', include('zistino_apps.deliveries.urls')),
        path('payments', include('zistino_apps.payments.urls')),
        path('configurations', include('zistino_apps.configurations.urls')),
        # Original routes (kept for backward compatibility, but excluded from Swagger)
        path('', include('zistino_apps.baskets.urls')),
        path('', include('zistino_apps.content.urls')),
        path('', include('zistino_apps.points.urls')),
        # CMS endpoints for home page content
        path('cms/by-page', products_views.CMSByPageView.as_view(), name='cms-by-page'),
        path('cms/by-group-name', products_views.CMSByGroupNameView.as_view(), name='cms-by-group-name'),
        path('cms/page-view', products_views.CMSPageViewView.as_view(), name='cms-page-view'),
        # Zone endpoints
        path('mapzone/searchuserinzone', users_views.ZoneUserSearchView.as_view(), name='mapzone-searchuserinzone'),
        path('mapzone/search', users_views.ZoneSearchView.as_view(), name='mapzone-search'),
        path('mapzone/createuserinzone', users_views.CreateUserZoneView.as_view(), name='mapzone-createuserinzone'),
        path('mapzone/userinzone', users_views.UserInZoneView.as_view(), name='mapzone-userinzone'),
        path('mapzone', users_views.ZoneViewSet.as_view({'get': 'list', 'post': 'create'}), name='mapzone-list'),
        path('mapzone/<int:pk>', users_views.ZoneViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='mapzone-detail'),
        path('mapzone/userinzone/<int:pk>', users_views.UserZoneViewSet.as_view({'delete': 'destroy'}), name='mapzone-userinzone-delete'),
        # Driver delivery endpoints
        path('driverdelivery/followup', deliveries_views.DriverDeliveryFollowupView.as_view(), name='driverdelivery-followup'),
        path('driverdelivery/search', deliveries_views.AdminDeliverySearchView.as_view(), name='admin-driverdelivery-search'),
        path('drivers/byzone', users_views.DriversByZoneView.as_view(), name='admin-drivers-byzone'),
        path('transactionwallet/search', payments_views.AdminTransactionWalletSearchView.as_view(), name='admin-transactionwallet-search'),
        path('couponuses/search', payments_views.AdminCouponUsesSearchView.as_view(), name='admin-couponuses-search'),
        path('productspecifications/search', products_views.SpecificationViewSet.as_view({'post': 'search'}), name='admin-productspecifications-search'),
        path('comments/client/search', notifications_views.AdminCommentSearchView.as_view(), name='admin-comments-search'),
        # Manager endpoints (is_staff=True required)
        path('users/users/userbyrole', users_views.ManagerUserByRoleView.as_view(), name='manager-userbyrole'),
        path('manager', include([
            path('deliveries', deliveries_views.ManagerDeliveryViewSet.as_view({'get': 'list', 'post': 'create'}), name='manager-deliveries-list'),
            path('deliveries/<uuid:pk>', deliveries_views.ManagerDeliveryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='manager-deliveries-detail'),
            path('deliveries/<uuid:pk>/transfer', deliveries_views.ManagerDeliveryViewSet.as_view({'post': 'transfer'}), name='manager-deliveries-transfer'),
            path('deliveries/<uuid:pk>/price', deliveries_views.ManagerDeliveryViewSet.as_view({'get': 'price'}), name='manager-deliveries-price'),
            path('deliveries/<uuid:pk>/items/bulk-set', deliveries_views.ManagerDeliveryViewSet.as_view({'post': 'items_bulk_set'}), name='manager-deliveries-items-bulk-set'),
            path('disapprovals', deliveries_views.ManagerDisapprovalsView.as_view(), name='manager-disapprovals'),
            path('weight-range-minimums', deliveries_views.ManagerWeightRangeMinimumsView.as_view(), name='manager-weight-range-minimums'),
            path('weight-shortfalls', deliveries_views.ManagerWeightShortfallsView.as_view(), name='manager-weight-shortfalls'),
            path('drivers/<uuid:driver_id>/routes', deliveries_views.ManagerDriverRouteView.as_view(), name='manager-driver-routes'),
            path('drivers/<uuid:driver_id>/available-dates', deliveries_views.ManagerDriverAvailableDatesView.as_view(), name='manager-driver-available-dates'),
            path('drivers/satisfaction', deliveries_views.ManagerDriverSatisfactionView.as_view(), name='manager-driver-satisfaction'),
            path('telephone-requests', deliveries_views.ManagerTelephoneRequestView.as_view(), name='manager-telephone-requests'),
            path('survey-questions', deliveries_views.ManagerSurveyQuestionsListView.as_view(), name='manager-survey-questions-list'),
            path('survey-questions/create', deliveries_views.ManagerSurveyQuestionCreateView.as_view(), name='manager-survey-questions-create'),
            path('survey-questions/<uuid:question_id>/update', deliveries_views.ManagerSurveyQuestionUpdateView.as_view(), name='manager-survey-questions-update'),
            path('survey-questions/<uuid:question_id>/delete', deliveries_views.ManagerSurveyQuestionDeleteView.as_view(), name='manager-survey-questions-delete'),
            path('vehicles', users_views.ManagerVehicleViewSet.as_view({'get': 'list'}), name='manager-vehicles-list'),
            path('vehicles/<uuid:pk>', users_views.ManagerVehicleViewSet.as_view({'get': 'retrieve'}), name='manager-vehicles-detail'),
            path('trips', deliveries_views.ManagerTripViewSet.as_view({'get': 'list', 'post': 'create'}), name='manager-trips-list'),
            path('trips/<int:pk>', deliveries_views.ManagerTripViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='manager-trips-detail'),
            path('trips/<int:pk>/end', deliveries_views.ManagerTripViewSet.as_view({'put': 'end_trip', 'patch': 'end_trip'}), name='manager-trips-end'),
            path('locations', deliveries_views.ManagerLocationViewSet.as_view({'get': 'list'}), name='manager-locations-list'),
            path('locations/<int:pk>', deliveries_views.ManagerLocationViewSet.as_view({'get': 'retrieve'}), name='manager-locations-detail'),
        ])),
        # notifications temporarily hidden
        # path('notifications/', include('zistino_apps.notifications.urls')),
    ])),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
