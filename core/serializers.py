from rest_framework import serializers
from .models import Account, DriverProfile,RideRequest, Booking
from emergency.models import EmergencyContact
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Account
        fields = ['username', 'password', 'role']

    def create(self, validated_data):
        # Create user with proper role handling
        user = Account(
            username=validated_data['username'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user
#driver profile serializer
class DriverProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = DriverProfile
        fields = [
            'id',
            'user',
            'license_number',
            'vehicle_details',
            'location_name',
            'current_lat',
            'current_lng',
            'profile_image',
        ]

#ride request serializer
#class RideRequestSerializer(serializers.ModelSerializer):
 #   customer = serializers.StringRelatedField(read_only=True)
  #  class Meta:
   #     model = RideRequest
    #    fields = ['id', 'customer', 'pickup_location', 'dropoff_location', 'created_at', 'status']
class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = "__all__"
        read_only_fields = ["customer", "status", "created_at"]

#booking serializer
class BookingSerializer(serializers.ModelSerializer):
    ride_request = RideRequestSerializer(read_only=True)
    driver = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'ride_request', 'driver', 'confirmed_at', 'status']




class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "phone_number", "created_at"]



# core/serializers.py
from .models import DriverReview

class DriverReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    driver = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DriverReview
        fields = ['id', 'booking', 'driver', 'customer', 'rating', 'feedback', 'created_at']