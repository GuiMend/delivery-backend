"""
Restaurants URL Configuration
"""
###
# Libraries
###
from django.urls import re_path, include


###
# URL Patterns
###
urlpatterns = [
    re_path(r'^api/v1/', include('restaurants.api.v1.urls'))
]
