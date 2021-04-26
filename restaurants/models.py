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
from django.core.validators import MinValueValidator

from helpers.models import TimestampModel
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
class Restaurant(TimestampModel):
    UPLOAD_TO = 'restaurant'
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        to='accounts.User',
        verbose_name=_('User'),
        related_name='restaurants',
        on_delete=models.CASCADE,
        blank=False,
    )

    blocked_users = models.ManyToManyField(
        'accounts.User',
        related_name='blocked_restaurants',
        verbose_name=_('Blocked Users'),
        blank=True,
    )

    image = models.FileField(
        upload_to=UploadFileTo(UPLOAD_TO, 'image'),
        null=True,
        blank=True,
        verbose_name=_('Image'),
    )

    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
        blank=False,
    )

    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )

    class Type(models.TextChoices):
        COFFEE = 'coffee', _('Coffee')
        BURGER = 'burger', _('Burger')
        DESERT = 'desert', _('Desert')
        PIZZA = 'pizza', _('Pizza')
        MEXICAN = 'mexican', _('Mexican')
        HEALTHY = 'healthy', _('Healthy')
        SUSHI = 'sushi', _('Sushi')

    type = models.CharField(
        max_length=16,
        choices=Type.choices,
        verbose_name=_('Type'),
    )

    def __str__(self):
        return self.name


class Meal(TimestampModel):
    UPLOAD_TO = 'meal'
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )
    restaurant = models.ForeignKey(
        to='restaurants.Restaurant',
        verbose_name=_('Restaurant'),
        related_name='meals',
        on_delete=models.CASCADE,
        blank=False,
    )

    image = models.FileField(
        upload_to=UploadFileTo(UPLOAD_TO, 'image'),
        null=True,
        blank=True,
        verbose_name=_('Image'),
    )

    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
        blank=False,
    )

    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )

    price = models.FloatField(
        verbose_name=_('Price'),
        validators=[MinValueValidator(0)],
        blank=False,
    )

    def __str__(self):
        return self.name


class MealRelations(TimestampModel):
    order = models.ForeignKey(
        to='restaurants.Order',
        verbose_name=_('Order'),
        related_name=_('meal_relations'),
        on_delete=models.CASCADE,
    )
    meal = models.ForeignKey(
        to='restaurants.Meal',
        verbose_name=_('Meal'),
        related_name=_('meal_relations'),
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Quantity'),
        blank=False,
        null=False,
    )

    def __str__(self):
        return f'{self.order.id}{self.order.status}: {self.meal.name} x {self.quantity}'


class Order(TimestampModel):
    user = models.ForeignKey(
        to='accounts.User',
        verbose_name=_('User'),
        related_name='orders',
        on_delete=models.CASCADE,
        blank=False,
    )
    restaurant = models.ForeignKey(
        to='restaurants.Restaurant',
        verbose_name=_('Restaurant'),
        related_name='orders_restaurant',
        on_delete=models.CASCADE,
        blank=False,
    )

    class Status(models.TextChoices):
        PLACED = 'placed', _('Placed')
        CANCELED = 'canceled', _('Canceled')
        PROCESSING = 'processing', _('Processing')
        IN_ROUTE = 'in_route', _('In route')
        DELIVERED = 'delivered', _('Delivered')
        RECEIVED = 'received', _('Received')

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        verbose_name=_('Status'),
        default=Status.PLACED,
    )

    meals = models.ManyToManyField(
        'restaurants.Meal',
        through='restaurants.MealRelations',
        related_name='orders',
        verbose_name=_('Meals'),
    )

    total = models.FloatField(
        verbose_name=_('Total'),
        validators=[MinValueValidator(0)],
        blank=False,
        null=False,
    )

    def __str__(self):
        return f'{self.restaurant.name}: {self.user.email} R${self.total} ({self.status})'


class StatusHistory(TimestampModel):
    order = models.ForeignKey(
        to='restaurants.Order',
        verbose_name=_('Order'),
        related_name='status_history',
        on_delete=models.CASCADE,
        blank=False,
    )
    status = models.CharField(
        max_length=16,
        choices=Order.Status.choices,
        blank=False,
    )

    def __str__(self):
        return f'{self.created_at} - {self.status}'
