"""
API V1: Accounts Serializers
"""
###
# Libraries
###
from django.contrib.auth.models import User
from rest_auth.models import TokenModel
from rest_auth.serializers import (
    UserDetailsSerializer as BaseUserDetailsSerializer,
    PasswordResetSerializer as BasePasswordResetSerializer,
)
from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.utils.translation import ugettext as _

from restaurants.models import Restaurant, Meal, Order, MealRelations, StatusHistory


###
# Serializers
###
class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('id', 'image', 'name', 'description', 'price', 'restaurant')


class MealRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRelations
        fields = ('id', 'meal', 'quantity')


class MealRelationDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='meal.id')
    name = serializers.CharField(source='meal.name')
    image = serializers.FileField(source='meal.image')
    description = serializers.CharField(source='meal.description')
    price = serializers.FloatField(source='meal.price')

    class Meta:
        model = MealRelations
        fields = ('quantity', 'id', 'name', 'image', 'description', 'price')


class StatusHistorySerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    datetime = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = StatusHistory
        fields = ('id', 'datetime', 'status', 'order')

    def validate(self, attrs):
        user = self.context.get('request').user
        order = attrs.get('order')
        restaurant_owner = order.restaurant.user
        client = order.user
        status = attrs.get('status')

        errors = {}

        if order.status == Order.Status.CANCELED:
            errors.update({'status': _(f'The order is already finalized. No changes allowed')})

        if order.status == Order.Status.PLACED:
            if status != Order.Status.PROCESSING and status != Order.Status.CANCELED:
                if user == restaurant_owner:
                    errors.update({'status': _(f'Status must be {Order.Status.PROCESSING}')})
                else:
                    errors.update({'user': _("You don't have permission to perform this action")})
            elif status != Order.Status.CANCELED and status != Order.Status.PROCESSING:
                if user == client:
                    errors.update({'status': _(f'Status must be {Order.Status.CANCELED}')})
                else:
                    errors.update({'user': _("You don't have permission to perform this action")})
        elif order.status == Order.Status.DELIVERED:
            if user != client:
                errors.update({'user': _("You don't have permission to perform this action")})
            elif status != Order.Status.RECEIVED:
                errors.update({'status': _(f'Status must be {Order.Status.RECEIVED}')})
        else:
            if user != restaurant_owner:
                errors.update({'user': _("You don't have permission to perform this action")})

        if order.status == Order.Status.PROCESSING and status != Order.Status.IN_ROUTE:
            errors.update({'status': _(f'Status must be {Order.Status.IN_ROUTE}')})

        if order.status == Order.Status.IN_ROUTE and status != Order.Status.DELIVERED:
            errors.update({'status': _(f'Status must be {Order.Status.DELIVERED}')})

        if errors:
            raise ValidationError(errors)
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    meals = MealRelationSerializer(many=True, write_only=True)
    status = serializers.CharField(read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    datetime = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'restaurant', 'meals', 'total', 'status', 'status_history', 'datetime')

    def create(self, validated_data):
        instance = Order.objects.create(
            user=validated_data.get('user'),
            restaurant=validated_data.get('restaurant'),
            total=validated_data.get('total'),
        )
        StatusHistory.objects.create(order=instance, status=Order.Status.PLACED)

        for meal in validated_data.get('meals'):
            MealRelations.objects.create(**meal, order=instance)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['meals'] = MealRelationDetailSerializer(instance.meal_relations.all(), many=True).data
        data['restaurant'] = RestaurantSerializer(instance.restaurant).data
        return data


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'description', 'type', 'image', 'user')


class RestaurantDetailSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'description', 'type', 'image', 'user', 'meals')
