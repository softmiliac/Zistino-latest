"""
URL patterns for Testimonials compatibility layer.
Provides all endpoints matching old Swagger format.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.TestimonialsViewSet, basename='testimonials')

urlpatterns = [
    # Custom endpoints (must come before router to avoid conflicts)
    path('dapper', views.TestimonialsDapperView.as_view(), name='testimonials-dapper'),
    
    # Router URLs (handles: POST /api/v1/testimonials, POST /api/v1/testimonials/search, POST /api/v1/testimonials/client, GET/PUT/DELETE /api/v1/testimonials/{id})
    path('', include(router.urls)),
]

