from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Avg, Q
import math

from .models import (
    Account,
    DriverProfile,
    RideRequest,
    Booking,
    DriverReview,
)
from emergency.models import EmergencyContact, EmergencyAlert
from .serializers import (
    RegisterSerializer,
    DriverProfileSerializer,
    RideRequestSerializer,
    BookingSerializer,
    EmergencyContactSerializer,
    DriverReviewSerializer,
)


# ================ UTILS ========================================
def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates (Haversine formula)."""
    lat1, lng1, lat2, lng2 = map(float, [lat1, lng1, lat2, lng2])
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))  


# ================ AUTH =========================================
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({"message": "Login successful"}, status=200)
    return Response({"error": "Invalid credentials"}, status=401)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"message": "Logout successful"}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return current user's info (role, username)."""
    return Response({"username": request.user.username, "role": request.user.role})


# ================ DRIVER PROFILE ===============================
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

class DriverProfileCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "driver":
            return Response({"error": "Only drivers can create a profile"}, status=403)
        serializer = DriverProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DriverProfileDetailView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = DriverProfile.objects.get(user=request.user)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)
        serializer = DriverProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        try:
            profile = DriverProfile.objects.get(user=request.user)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)
        serializer = DriverProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        try:
            profile = DriverProfile.objects.get(user=request.user)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)
        profile.delete()
        return Response({"message": "Profile deleted"}, status=204)


# ================ RIDE REQUEST ================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_ride_request(request):
    if request.user.role != "customer":
        return Response({"error": "Only customers can create ride requests"}, status=403)

    serializer = RideRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(customer=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_my_ride_requests(request):
    rides = RideRequest.objects.filter(customer=request.user)
    serializer = RideRequestSerializer(rides, many=True)
    return Response(serializer.data)


# ================ BOOKING ======================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_booking(request, ride_request_id):
    if request.user.role != "driver":
        return Response({"error": "Only drivers can accept bookings"}, status=403)

    try:
        ride = RideRequest.objects.get(id=ride_request_id, status="pending")
    except RideRequest.DoesNotExist:
        return Response({"error": "Ride not found or already matched"}, status=404)

    ride.status = "accepted"
    ride.save()

    booking = Booking.objects.create(ride_request=ride, driver=request.user)
    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_my_bookings(request):
    if request.user.role == "driver":
        bookings = Booking.objects.filter(driver=request.user)
    else:
        bookings = Booking.objects.filter(ride_request__customer=request.user)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, driver=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found or unauthorized"}, status=404)

    new_status = request.data.get("status")
    if new_status not in ["completed", "cancelled"]:
        return Response({"error": "Invalid status"}, status=400)

    booking.status = new_status
    booking.save()
    booking.ride_request.status = "completed" if new_status == "completed" else "cancelled"
    booking.ride_request.save()

    return Response({"message": f"Booking marked as {new_status}"}, status=200)


# ================ CANCEL BOOKING (CUSTOMER SIDE) ===============
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """Allow customers to cancel a ride they booked"""
    user = request.user
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    # customer cancel korbe
    if booking.ride_request.customer != user:
        return Response({"error": "Not authorized to cancel this ride"}, status=403)

    
    if booking.status in ["completed", "cancelled"]:
        return Response({"error": f"Cannot cancel a {booking.status} ride"}, status=400)

    booking.status = "cancelled"
    booking.save()
    ride = booking.ride_request
    ride.status = "cancelled"
    ride.save()

    return Response({"message": "Ride cancelled successfully"}, status=200)


# ================ CANCEL RIDE =================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_ride_request(request, ride_request_id):
    try:
        ride = RideRequest.objects.get(id=ride_request_id, customer=request.user, status="pending")
    except RideRequest.DoesNotExist:
        return Response({"error": "Ride not found or cannot be cancelled"}, status=404)

    ride.status = "cancelled"
    ride.save()
    return Response({"message": "Ride cancelled successfully"}, status=200)

