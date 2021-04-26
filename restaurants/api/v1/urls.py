"""
API V1: Restaurants Urls
"""
###
# Libraries
###
from django.urls import re_path, include
from rest_framework_nested import routers

from restaurants.api.v1.views import RestaurantViewSet, MealViewSet, OrderViewSet, StatusHistoryViewSet, BlockUserView

###
# Routers
###
""" Main router """
router = routers.SimpleRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurants')
router.register(r'meals', MealViewSet, basename='meals')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'status-history', StatusHistoryViewSet, basename='status-history')

###
# URLs
###
urlpatterns = [
    re_path(r'^block-user', BlockUserView.as_view(), name="block-user"),
    re_path(r'^', include(router.urls)),
]
