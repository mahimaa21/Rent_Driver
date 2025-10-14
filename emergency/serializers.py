# emergency/serializers.py
from rest_framework import serializers
from .models import EmergencyContact, EmergencyAlert

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "phone_number", "created_at"]


class EmergencyAlertSerializer(serializers.ModelSerializer):
    contact = EmergencyContactSerializer(read_only=True)

    class Meta:
        model = EmergencyAlert
        fields = ["id", "contact", "status", "triggered_at"]