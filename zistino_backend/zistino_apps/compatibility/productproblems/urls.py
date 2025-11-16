"""
URL patterns for ProductProblems compatibility layer.
Provides all 11 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ProductProblemsViewSet, basename='productproblems')

urlpatterns = [
    # Router URLs (handles: GET/POST /api/v1/productproblems, GET/PUT/DELETE /api/v1/productproblems/{id})
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dapper', views.ProductProblemsDapperView.as_view(), name='productproblems-dapper'),
    path('all', views.ProductProblemsAllView.as_view(), name='productproblems-all'),
    path('productproblemgroup', views.ProductProblemGroupDeleteView.as_view(), name='productproblems-group-delete'),
]

