"""
API V1: Accounts Permissions
"""
###
# Libraries
###
from rest_framework.permissions import BasePermission


###
# Permissions
###


class IsRestaurantOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_restaurant
