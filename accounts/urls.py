"""
Accounts URL Configuration
"""
###
# Libraries
###
from django.urls import re_path, include


###
# URL Patterns
###
urlpatterns = [
    re_path(r'^api/v1/', include('accounts.api.v1.urls'))
]
