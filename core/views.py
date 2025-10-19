from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Avg, Q
from math import radians, sin, cos, sqrt, atan2
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json

from .models import (
    Account,
    DriverProfile,
    RideRequest,
    Booking,
    EmergencyContact,
    EmergencyAlert,
    DriverReview,
    ChatMessage,
)
from .models import Account


def calculate_distance(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lng points."""
    if None in [lat1, lon1, lat2, lon2]:
        return None
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def geocode_address(address: str):
    try:
        if not address:
            return None, None
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
        }
        url = "https://nominatim.openstreetmap.org/search?" + urlencode(params)
        req = Request(url, headers={
            "User-Agent": "RentADriver/1.0 (education; contact: example@example.com)",
        })
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and data:
                lat = float(data[0].get("lat"))
                lon = float(data[0].get("lon"))
                return lat, lon
    except Exception:
        pass
    return None, None


def home_view(request):
    return render(request, "index.html")


def register_view(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "").strip()
        role = request.POST.get("role")
        if not username or not password or role not in ["customer", "driver"]:
            messages.error(request, "Please fill all fields correctly.")
            return redirect("register")
        if Account.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")
        user = Account.objects.create_user(username=username, password=password, role=role)
        login(request, user)
        messages.success(request, "Registration successful!")
        # If driver, require profile completion first
        if role == "driver":
            return redirect("driver_profile")
        return redirect("customer_dashboard")
    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("driver_dashboard" if user.role == "driver" else "customer_dashboard")
        messages.error(request, "Invalid credentials.")
        return redirect("login")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("home")

# DRIVER PROFILE 
@login_required
def driver_profile_view(request):
    if request.user.role != "driver":
        return HttpResponseForbidden("Only drivers can create a profile")
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        license_number = request.POST.get("license")
        vehicle_details = request.POST.get("vehicle")
        nid_number = request.POST.get("nid_number")
        address = request.POST.get("address")
        profile_picture = request.FILES.get("profile_picture")
        lat = request.POST.get("lat")
        lng = request.POST.get("lng")
        profile, _ = DriverProfile.objects.get_or_create(user=request.user)
        if full_name:
            profile.full_name = full_name
        profile.license_number = license_number
        profile.vehicle_details = vehicle_details
        if nid_number:
            profile.nid_number = nid_number
        if address is not None:
            profile.address = address
        if profile_picture:
            profile.profile_picture = profile_picture
       # Jodi latitude ar longitude deya thake tahole oigulo use hobe.Ar jodi na thake, tahole deya address theke location ber kora hobe.
        lat_val = float(lat) if lat else None
        lng_val = float(lng) if lng else None

        if lat_val is None or lng_val is None:
            # Jodi address deya thake tahole sei address diye coordinates ber korar try kore"
            if address:
                g_lat, g_lng = geocode_address(address)
                if lat_val is None:
                    lat_val = g_lat
                if lng_val is None:
                    lng_val = g_lng
                if g_lat is None or g_lng is None:
                    messages.info(request, "Could not determine coordinates from address; you can use 'Use my location' or enter coordinates manually.")

        profile.current_lat = lat_val
        profile.current_lng = lng_val
        profile.save()
        messages.success(request, "Profile saved.")
        return redirect("driver_dashboard")
    try:
        profile = DriverProfile.objects.get(user=request.user)
    except DriverProfile.DoesNotExist:
        profile = None
    return render(request, "driver_profile.html", {"profile": profile})


@login_required
def delete_profile_picture(request):
    if request.user.role != "driver":
        return HttpResponseForbidden("Only drivers can modify a driver profile")
    if request.method != "POST":
        return redirect("driver_profile")
    try:
        profile = DriverProfile.objects.get(user=request.user)
        if profile.profile_picture:
            profile.profile_picture.delete(save=False)
            profile.profile_picture = None
            profile.save(update_fields=["profile_picture"])
            messages.info(request, "Profile picture removed.")
        else:
            messages.info(request, "No profile picture to remove.")
    except DriverProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
    return redirect("driver_profile")


# RIDE REQUEST

@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        return redirect("driver_dashboard")
    if request.method == "POST":
        pickup = request.POST.get("pickup")
        dropoff = request.POST.get("dropoff")
        car = request.POST.get("carName")
        RideRequest.objects.create(
            customer=request.user,
            pickup_location=pickup,
            dropoff_location=dropoff,
        )
        messages.success(request, "Ride request created.")
        return redirect("customer_dashboard")
    rides = RideRequest.objects.filter(customer=request.user).order_by("-created_at")
    customer_bookings = Booking.objects.filter(ride_request__customer=request.user).order_by("-confirmed_at")

    # Build nearby drivers list based on customer's last known location
    nearby_list = []
    lat0 = request.user.last_lat
    lng0 = request.user.last_lng
    drivers = DriverProfile.objects.select_related("user").all()
    for d in drivers:
        if d.current_lat is None or d.current_lng is None:
            continue
        dist = None
        if lat0 is not None and lng0 is not None:
            dist = calculate_distance(lat0, lng0, d.current_lat, d.current_lng)
        nearby_list.append({
            "user": d.user,
            "vehicle_details": d.vehicle_details,
            "distance_km": round(dist, 2) if dist is not None else None,
        })

    # Jodi distance thake tahole distance er upor vitti kore sort kore ar  10 km er vitore ja ase oigula filter kore"
    if any(item["distance_km"] is not None for item in nearby_list):
        filtered = [item for item in nearby_list if item["distance_km"] is not None and item["distance_km"] <= 10]
        if not filtered:
            filtered = [item for item in nearby_list if item["distance_km"] is not None]
        filtered.sort(key=lambda x: x["distance_km"])
        nearby_list = filtered[:10]
    else:
        # kono location nai
        nearby_list = nearby_list[:10]

    return render(request, "customer_dashboard.html", {
        "rides": rides,
        "nearby_drivers": nearby_list,
        "customer_bookings": customer_bookings,
    })


# BOOKING 

@login_required
def create_booking(request, ride_request_id):
    if request.user.role != "driver":
        return HttpResponseForbidden("Only drivers can accept bookings")
    ride = get_object_or_404(RideRequest, id=ride_request_id, status="pending")
    ride.status = "accepted"
    ride.save()
    Booking.objects.create(ride_request=ride, driver=request.user)
    messages.success(request, "Booking created.")
    return redirect("driver_dashboard")


@login_required
def list_my_bookings(request):
    if request.user.role == "driver":
        bookings = Booking.objects.filter(driver=request.user)
    else:
        bookings = Booking.objects.filter(ride_request__customer=request.user)
    return render(request, "driver_dashboard.html", {"bookings": bookings})


@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, driver=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["completed", "cancelled"]:
            booking.status = new_status
            booking.save()
            booking.ride_request.status = ("completed" if new_status == "completed" else "cancelled")
            booking.ride_request.save()
            messages.success(request, f"Booking marked as {new_status}.")
    return redirect("driver_dashboard")

# CANCEL RIDE 

@login_required
def cancel_ride_request(request, ride_request_id):
    ride = get_object_or_404(RideRequest, id=ride_request_id)

    #ride je create koreche(customer) ba je driver ke assign kora hoyeche shei driver cancel korte parbe."
    is_customer = request.user == ride.customer
    is_assigned_driver = False
    try:
        booking = ride.booking
        is_assigned_driver = request.user.role == "driver" and booking.driver_id == request.user.id
    except Booking.DoesNotExist:
        booking = None

    if not (is_customer or is_assigned_driver):
        return HttpResponseForbidden("You are not allowed to cancel this ride")

    # Do not alter finalized rides
    if ride.status in ["completed", "cancelled"]:
        messages.info(request, "This ride is already finalized.")
        return redirect("driver_dashboard" if request.user.role == "driver" else "customer_dashboard")

    # Cancel linked booking if present and not finalized
    if booking and booking.status not in ["completed", "cancelled"]:
        booking.status = "cancelled"
        booking.save(update_fields=["status"])

    # Mark ride cancelled
    ride.status = "cancelled"
    ride.save(update_fields=["status"])

    messages.success(request, "Ride cancelled.")
    return redirect("driver_dashboard" if request.user.role == "driver" else "customer_dashboard")


@login_required
def edit_ride_request(request, ride_request_id):
    """Allow a customer to edit their own pending ride's pickup/dropoff."""
    ride = get_object_or_404(RideRequest, id=ride_request_id, customer=request.user)
    if ride.status != "pending":
        messages.info(request, "Only pending rides can be edited.")
        return redirect("customer_dashboard")
    if request.method == "POST":
        pickup = (request.POST.get("pickup") or "").strip()
        dropoff = (request.POST.get("dropoff") or "").strip()
        if not pickup or not dropoff:
            messages.error(request, "Both pickup and dropoff are required.")
            return redirect("edit_ride_request", ride_request_id=ride.id)
        ride.pickup_location = pickup
        ride.dropoff_location = dropoff
        ride.save(update_fields=["pickup_location", "dropoff_location"])
        messages.success(request, "Ride updated.")
        return redirect("customer_dashboard")
    return render(request, "ride_edit.html", {"ride": ride})
