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
    EmergencyContact,
    EmergencyAlert,
    DriverReview,
)
from .serializers import (
    RegisterSerializer,
    DriverProfileSerializer,
    RideRequestSerializer,
    BookingSerializer,
    EmergencyContactSerializer,
    DriverReviewSerializer,
)

# ===============================================================
# ================ UTILS ========================================
# ===============================================================

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates (Haversine formula)."""
    lat1, lng1, lat2, lng2 = map(float, [lat1, lng1, lat2, lng2])
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))  # km


# ===============================================================
# ================ AUTH =========================================
# ===============================================================

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