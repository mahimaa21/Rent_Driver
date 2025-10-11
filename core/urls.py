from django.urls import path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # ---------- AUTH ----------
    path("api/register/", views.register, name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/me/", views.me, name="me"),

    # ---------- DRIVER PROFILE ----------
    path("api/driver/profile/create/", views.create_driver_profile, name="create_driver_profile"),

    # ---------- RIDE REQUEST ----------
    path("api/rides/create/", views.create_ride_request, name="create_ride_request"),
    path("api/rides/my/", views.list_my_ride_requests, name="list_my_rides"),
    path("api/rides/<int:ride_request_id>/cancel/", views.cancel_ride_request, name="cancel_ride_request"),
    path("api/rides/suggest/<int:ride_request_id>/", views.suggest_drivers, name="suggest_drivers"),

    # ---------- BOOKING ----------
    path("api/booking/create/<int:ride_request_id>/", views.create_booking, name="create_booking"),
    path("api/bookings/my/", views.list_my_bookings, name="list_my_bookings"),
    path("api/booking/<int:booking_id>/status/", views.update_booking_status, name="update_booking_status"),



# ---------- DRIVER: AVAILABLE RIDES ----------
    path("api/rides/available/", views.list_available_rides, name="list_available_rides"),

    # ---------- REVIEWS ----------
    path("api/reviews/create/<int:booking_id>/", views.create_review, name="create_review"),
    path("api/reviews/driver/<int:driver_id>/", views.list_driver_reviews, name="list_driver_reviews"),

    # ---------- LEADERBOARD ----------
    path("api/leaderboard/drivers/", views.driver_leaderboard, name="driver_leaderboard"),
