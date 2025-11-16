from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """
    Permission class to check if user is a manager.
    Managers are identified by is_staff=True flag.
    """
    message = 'You must be a manager to access this endpoint.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

