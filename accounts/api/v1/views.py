"""
API V1: Accounts Views
"""
###
# Libraries
###
from smtplib import SMTPException

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest, Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import (
    permissions,
    viewsets,
    status,
    generics,
    mixins,
)
from rest_framework.response import Response
from rest_auth.views import UserDetailsView as BaseUserDetailsView
from accounts.models import (
    ChangeEmailRequest,
    User)
from . import serializers
from .permissions import IsRestaurantOwner


###
# Filters
###


###
# Viewsets
###
class UserView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserListSerializer
    permission_classes = (permissions.IsAuthenticated, IsRestaurantOwner)
    pagination_class = None


class UserDetailsView(BaseUserDetailsView):
    serializer_class = serializers.UserDetailsSerializer

    def get_serializer_class(self):
        return self.serializer_class


class ChangeEmailViewSet(generics.GenericAPIView):
    serializer_class = serializers.ChangeEmailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        email = serializer.data.get('email')

        change_request, _ = ChangeEmailRequest.objects.update_or_create(
            user=user, defaults={'email': email}
        )

        confirmation_link = HttpRequest.build_absolute_uri(
            request, location=str(change_request.uuid)
        )

        try:
            context = {
                'email': user.email,
                'confirmation_link': confirmation_link,
            }
            html_email = render_to_string('account/change_email.html', context)
            txt_email = render_to_string('account/change_email.txt', context)
            send_mail(
                subject='topfood-backend - Email Confirmation',
                message=txt_email,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_email
            )
        except SMTPException:
            return Response(
                'Failed to send email',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_payload = {
            'message': 'Confirmation email has been sent.'
        }
        return Response(response_payload, status=status.HTTP_200_OK)


class ChangeEmailConfirmationViewSet(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            change_request = ChangeEmailRequest.objects.get(uuid=self.kwargs.get('uuid'))
        except (ChangeEmailRequest.DoesNotExist, ValidationError):
            raise Http404('No requests match the given UUID')

        with transaction.atomic():
            user = change_request.user
            user.email = change_request.email
            allauth_email = user.emailaddress_set.first()
            allauth_email.email = change_request.email
            user.save(update_fields=['email'])
            allauth_email.save(update_fields=['email'])
            user.auth_token.delete()

            change_request.delete()
        return render('account/change_email_done.html', {'first_name': user.first_name})


