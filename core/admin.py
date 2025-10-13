from django.contrib import admin
from .models import Account, DriverProfile, RideRequest, Booking, DriverReview

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "role", "email", "is_active", "is_staff")
    search_fields = ("username", "email", "role")

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "license_number", "vehicle_details", "profile_image_tag")
    search_fields = ("user__username", "license_number", "vehicle_details")

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return f'<img src="{obj.profile_image.url}" style="height:40px;" />'
        return ""
    profile_image_tag.allow_tags = True
    profile_image_tag.short_description = "Profile Image"

@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ("customer", "pickup_location", "dropoff_location", "status", "created_at")
    search_fields = ("customer__username", "pickup_location", "dropoff_location")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "ride_request", "driver", "status", "confirmed_at")
    search_fields = ("ride_request__customer__username", "driver__username", "status")

@admin.register(DriverReview)
class DriverReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "driver", "customer", "rating", "created_at")
    search_fields = ("driver__username", "customer__username", "rating")
