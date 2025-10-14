from django.contrib import admin
from .models import EmergencyContact, EmergencyAlert

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
	list_display = ("user", "phone_number", "created_at")
	search_fields = ("user__username", "phone_number")

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
	list_display = ("user", "contact", "status", "triggered_at")
	search_fields = ("user__username", "contact__phone_number", "status")
