from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'colors', views.ColorViewSet)
router.register(r'prices', views.PriceViewSet)
router.register(r'specifications', views.SpecificationViewSet)
router.register(r'warranties', views.WarrantyViewSet)
router.register(r'faqs', views.FAQViewSet, basename='faqs')
router.register(r'comments', views.ProductCommentViewSet, basename='comments')
router.register(r'productsections', views.ProductSectionViewSet, basename='productsections')
router.register(r'problems', views.ProblemViewSet, basename='problems')

urlpatterns = [
    path('', include(router.urls)),
]
