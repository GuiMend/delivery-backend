"""
API V1: Accounts Views
"""
###
# Libraries
###
from functools import reduce
from operator import and_

import django_filters
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.validators import ValidationError
from django_filters import rest_framework as filters
from django.utils.translation import ugettext as _
from rest_framework import (
    permissions,
    status,
    generics,
    parsers,
    viewsets)
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from accounts.api.v1.permissions import IsRestaurantOwner
from accounts.api.v1.serializers import BlockUserSerializer
from accounts.models import User
from helpers.parser import MultipartJsonParser, multipart_json_custom_create, multipart_json_custom_update
from restaurants.models import Restaurant, Meal, Order, StatusHistory
from .serializers import RestaurantSerializer, RestaurantDetailSerializer, MealSerializer, OrderSerializer, \
    StatusHistorySerializer


###
# Filters
###
class RestaurantsFilter(django_filters.FilterSet):
    my_restaurant = django_filters.BooleanFilter(method="filter_my_restaurant")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.request.user.is_restaurant:
            return queryset
        return queryset.filter(~Q(blocked_users__in=[self.request.user]))

    def filter_my_restaurant(self, queryset, name, value):
        return queryset.filter(user=self.request.user)


###
# Viewsets
###
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RestaurantsFilter
    pagination_class = None
    parser_classes = (MultipartJsonParser, parsers.JSONParser)

    def get_permissions(self):
        permissions_classes = [
            permissions.IsAuthenticated
        ]
        if self.request.method not in SAFE_METHODS:
            permissions_classes.append(IsRestaurantOwner)
        return [permission() for permission in permissions_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantSerializer

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return multipart_json_custom_update(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return multipart_json_custom_create(self, request, *args, **kwargs)


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    pagination_class = None
    parser_classes = (MultipartJsonParser, parsers.JSONParser)

    def get_permissions(self):
        permissions_classes = [
            permissions.IsAuthenticated
        ]
        if self.request.method not in SAFE_METHODS:
            permissions_classes.append(IsRestaurantOwner)
        return [permission() for permission in permissions_classes]

    def update(self, request, *args, **kwargs):
        return multipart_json_custom_update(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return multipart_json_custom_create(self, request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticated,)

    def filter_queryset(self, queryset):
        if self.request.user.is_restaurant:
            return queryset.filter(restaurant__user=self.request.user).order_by('created_at')
        return queryset.filter(user=self.request.user).order_by('created_at')

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return multipart_json_custom_update(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return multipart_json_custom_create(self, request, *args, **kwargs)


class StatusHistoryViewSet(viewsets.ModelViewSet):
    queryset = StatusHistory.objects.all()
    serializer_class = StatusHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)


class BlockUserView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, IsRestaurantOwner)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.data.get('user'))
        restaurants = request.user.restaurants.all()

        for restaurant in restaurants:
            if restaurant.user == user:
                raise ValidationError({'user': _("You can't block your own restaurant")})
            restaurant.blocked_users.add(user)

        serializer = BlockUserSerializer(user, data={})
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
