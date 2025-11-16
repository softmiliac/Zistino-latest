from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BasketViewSet


router = DefaultRouter()
# Expose as /api/v1/baskets/
router.register(r"baskets", BasketViewSet, basename="basket")


urlpatterns = []
urlpatterns += router.urls


