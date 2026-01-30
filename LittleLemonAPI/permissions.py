from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow managers to have access.
    """

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists():
            return True
        return False
    
class IsDeliveryCrew(permissions.BasePermission):
    """
    Custom permission to only allow delivery crew to have access.
    """

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Delivery Crew').exists():
            return True
        return False