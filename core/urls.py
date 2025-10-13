from django.urls import path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from core.views import DriverProfileCreateView, DriverProfileDetailView

urlpatterns = [
    # ---------- AUTH ----------
    path("api/register/", views.register, name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/me/", views.me, name="me"),

    # ---------- DRIVER PROFILE ----------
    path("api/driver/profile/create/", DriverProfileCreateView.as_view(), name="create_driver_profile"),
    path("api/driver/profile/me/", DriverProfileDetailView.as_view(), name="driver_profile_detail"),

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

    # ---------- EMERGENCY ----------
    path("api/emergency/set/", views.set_emergency_contact, name="set_emergency_contact"),
    path("api/emergency/get/", views.get_emergency_contact, name="get_emergency_contact"),
    path("api/emergency/alert/", views.trigger_alert, name="trigger_alert"),
    path("api/emergency/alerts/", views.list_alerts, name="list_alerts"),
    path("api/nearby-drivers/", views.nearby_drivers, name="nearby_drivers"),
    path("api/nearby-rides/", views.nearby_rides, name="nearby_rides"),
    path("api/booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),

]

# ---------- FRONTEND ROUTES ----------
urlpatterns += [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login"),
    path("register/", TemplateView.as_view(template_name="register.html"), name="register_page"),
    path("driver/profile/", TemplateView.as_view(template_name="driver_profile.html"), name="driver_profile_page"),
    path("customer/dashboard/", TemplateView.as_view(template_name="customer_dashboard.html"), name="customer_dashboard"),
    path("driver/dashboard/", TemplateView.as_view(template_name="driver_dashboard.html"), name="driver_dashboard"),
    path("leaderboard/", TemplateView.as_view(template_name="leaderboard.html"), name="leaderboard"),
    path("emergency/", TemplateView.as_view(template_name="emergency.html"), name="emergency"),
]