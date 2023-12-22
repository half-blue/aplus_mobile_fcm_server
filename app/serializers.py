from rest_framework import serializers
from .models import *
from fcm_django.models import FCMDevice

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["threads"]

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ["registration_id", "type", "active"]