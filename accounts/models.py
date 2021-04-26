"""
Accounts Models
"""
###
# Libraries
###
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext as _

from helpers.s3 import UploadFileTo


###
# Choices
###


###
# Querysets
###


###
# Models
###
class User(AbstractUser):
    # Helpers
    UPLOAD_TO = 'accounts'
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )

    is_restaurant = models.BooleanField(
        verbose_name=_('Is Restaurant owner'),
        default=False,
    )
    image = models.FileField(
        upload_to=UploadFileTo(UPLOAD_TO, 'image'),
        null=True,
        blank=True,
        verbose_name=_('Image'),
    )

    @property
    def full_name(self):
        if self.first_name:
            return f'{self.first_name} {self.last_name}'
        return 'Unnamed'


class ChangeEmailRequest(models.Model):
    # Helpers
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('uuid'),
    )

    # User model
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='change_email_request',
        verbose_name=_('user'),
    )

    # Email
    email = models.EmailField(verbose_name=_('email'))
