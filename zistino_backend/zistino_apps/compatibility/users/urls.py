"""
URL patterns for Users compatibility layer.
Provides all 12 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.UsersViewSet, basename='users')

urlpatterns = [
    # Direct list endpoint (GET /api/v1/users) - must come before router to avoid API root view
    path('', views.UsersListView.as_view(), name='users-list'),
    # Retrieve endpoint (GET /api/v1/users/{id})
    path('<uuid:pk>', views.UsersRetrieveView.as_view(), name='users-retrieve'),
    
    # Custom endpoints (must come before router to avoid conflicts)
    path('usersearch', views.UsersUserSearchView.as_view(), name='users-usersearch'),
    path('client/searchsp', views.UsersClientSearchSPView.as_view(), name='users-client-searchsp'),
    path('client/permissions', views.UsersClientPermissionsView.as_view(), name='users-client-permissions'),
    
    # ViewSet actions (POST /api/v1/users/search, etc.)
    path('search', views.UsersViewSet.as_view({'post': 'search'}), name='users-search'),
    path('searchsp', views.UsersViewSet.as_view({'post': 'searchsp'}), name='users-searchsp'),
    path('userbyrole', views.UsersViewSet.as_view({'post': 'userbyrole'}), name='users-userbyrole'),
    path('userbyrolerequest', views.UsersViewSet.as_view({'post': 'userbyrolerequest'}), name='users-userbyrolerequest'),
    path('<uuid:pk>/roles', views.UsersViewSet.as_view({'get': 'roles', 'post': 'update_roles'}), name='users-roles'),
    path('<uuid:pk>/permissions', views.UsersViewSet.as_view({'get': 'permissions'}), name='users-permissions'),
]

