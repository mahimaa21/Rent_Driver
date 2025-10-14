from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("booking", "sender", "message", "timestamp")
    search_fields = ("sender__username", "message", "booking__id")
    list_filter = ("timestamp",)