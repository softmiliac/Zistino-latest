"""
Custom router for compatibility layer that doesn't add trailing slashes to URLs.
This matches the old Swagger format where endpoints don't have trailing slashes.
"""
from rest_framework.routers import DefaultRouter, Route, DynamicRoute


class NoTrailingSlashRouter(DefaultRouter):
    """
    Custom router that removes trailing slashes from all generated URLs.
    This ensures compatibility with the old Swagger format.
    """
    
    routes = [
        # List route - no trailing slash
        Route(
            url=r'^{prefix}$',
            mapping={'get': 'list', 'post': 'create'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Detail route - no trailing slash
        Route(
            url=r'^{prefix}/{lookup}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated routes (for @action decorators) - detail actions
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
        # Dynamically generated routes (for @action decorators) - list actions
        DynamicRoute(
            url=r'^{prefix}/{url_path}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
    ]

