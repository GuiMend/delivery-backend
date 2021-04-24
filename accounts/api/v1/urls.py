"""
API V1: Accounts Urls
"""
###
# Libraries
###
from django.urls import re_path, include
from rest_auth.views import (
    LoginView,
    LogoutView,
    UserDetailsView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from rest_auth.registration.views import (
    RegisterView,
)
from rest_framework_nested import routers

from .views import (
    ChangeEmailViewSet,
    ChangeEmailConfirmationViewSet,
)

###
# Routers
###
""" Main router """
router = routers.SimpleRouter()

###
# URLs
###
urlpatterns = [
    re_path(
        r'^login/$',
        LoginView.as_view(),
        name='rest_login',
    ),
    re_path(
        r'^logout/$',
        LogoutView.as_view(),
        name='rest_logout',
    ),
    re_path(
        r'^user/$',
        UserDetailsView.as_view(),
        name='rest_user_details',
    ),
    re_path(
        r'^change-password/$',
        PasswordChangeView.as_view(),
        name='rest_password_change',
    ),
    re_path(
        r'^change-email/(?P<uuid>[^/]+)/$',
        ChangeEmailConfirmationViewSet.as_view(),
        name='change-email-confirmation',
    ),
    re_path(
        r'^change-email/$',
        ChangeEmailViewSet.as_view(),
        name='change-email',
    ),
    re_path(
        r'^password/reset/$',
        PasswordResetView.as_view(),
        name='rest_password_reset',
    ),
    re_path(
        r'^password/reset/confirm/$',
        PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm',
    ),
    re_path(
        r'^register/$',
        RegisterView.as_view(),
        name='rest_register',
    ),
    re_path(r'^', include(router.urls)),
]
