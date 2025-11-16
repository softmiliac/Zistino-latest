"""
URL patterns for Tokens compatibility layer.
Provides all 7 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.TokensViewSet, basename='tokens')

urlpatterns = [
    # Custom endpoints (must come before router to avoid conflicts)
    path('tokenbyemail', views.TokensByEmailView.as_view(), name='tokens-by-email'),
    path('externallogin', views.TokensExternalLoginView.as_view(), name='tokens-external-login'),
    path('token-with-permissions', views.TokensWithPermissionsView.as_view(), name='tokens-with-permissions'),
    path('token-by-code', views.TokensByCodeView.as_view(), name='tokens-by-code'),
    path('token-by-code-confirmation', views.TokensByCodeConfirmationView.as_view(), name='tokens-by-code-confirmation'),
    path('refresh', views.TokensRefreshView.as_view(), name='tokens-refresh'),
    
    # Router URLs (handles: POST /api/v1/tokens)
    path('', include(router.urls)),
]

