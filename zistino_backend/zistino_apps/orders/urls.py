from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomerOrdersViewSet, WeightRangesView, TimeSlotsView

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
# remove legacy basket routes from orders to avoid duplicates
# router.register(r'baskets', views.BasketViewSet, basename='basket')
# router.register(r'basket-items', views.BasketItemViewSet, basename='basket-item')

urlpatterns = [
    path('', include(router.urls)),
    # Customer orders endpoints - separate path to avoid conflicts
    path('customer/orders', CustomerOrdersViewSet.as_view({'post': 'create', 'get': 'list'}), name='customer-orders-list'),
    path('customer/orders/<uuid:pk>', CustomerOrdersViewSet.as_view({'get': 'retrieve'}), name='customer-orders-detail'),
    path('customer/orders/client/search', CustomerOrdersViewSet.as_view({'post': 'client_search'}), name='customer-orders-search'),
    # Waste weight endpoints
    path('waste/weight-summary', views.WasteWeightSummaryView.as_view(), name='waste-weight-summary'),
    path('waste/weight-history', views.WasteWeightHistoryView.as_view(), name='waste-weight-history'),
    path('waste/orders/<uuid:order_id>/weights', views.OrderWeightDetailView.as_view(), name='order-weight-detail'),
    # Waste delivery request configuration endpoints
    path('waste/weight-ranges', WeightRangesView.as_view(), name='weight-ranges'),
    path('waste/time-slots', TimeSlotsView.as_view(), name='time-slots'),
]
