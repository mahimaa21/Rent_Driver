from django.contrib import admin
from .models import SystemLog

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("action", "level", "user", "timestamp")
    list_filter = ("level", "timestamp")
    search_fields = ("action", "user__username")