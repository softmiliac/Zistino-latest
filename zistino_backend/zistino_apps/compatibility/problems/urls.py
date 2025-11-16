"""
URL patterns for Problems compatibility layer.
Provides all 10 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ProblemsViewSet, basename='problems')

urlpatterns = [
    # Router URLs (handles: GET/POST /api/v1/problems, GET/PUT/DELETE /api/v1/problems/{id})
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dapper', views.ProblemsDapperView.as_view(), name='problems-dapper'),
    path('byparentid/<int:id>', views.ProblemsByParentIdView.as_view(), name='problems-byparentid'),
    path('children', views.ProblemsChildrenView.as_view(), name='problems-children'),
    path('byproductid/<str:id>', views.ProblemsByProductIdView.as_view(), name='problems-byproductid'),
    path('anonymous-byproductid/<str:id>', views.ProblemsAnonymousByProductIdView.as_view(), name='problems-anonymous-byproductid'),
]

