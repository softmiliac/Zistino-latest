from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'testimonials', views.TestimonialViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'menulinks', views.MenuLinkViewSet)
# blogposts removed - handled by compatibility layer at /api/v1/blogposts/
# router.register(r'blogposts', views.BlogPostViewSet)
router.register(r'blogcategories', views.BlogCategoryViewSet)
# blogtags removed - handled by compatibility layer at /api/v1/blogtags/
# router.register(r'blogtags', views.BlogTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # ============================================================================
    # BLOGPOSTS CUSTOM ENDPOINTS REMOVED
    # All blogposts endpoints are now handled by compatibility layer at /api/v1/blogposts/
    # ============================================================================
    # These endpoints moved to compatibility layer:
    # - GET /api/v1/blogposts/by-parentid/{id}
    # - GET /api/v1/blogposts/client/recents/{count}
    # - GET /api/v1/blogposts/client/byslug/{slug}
]

