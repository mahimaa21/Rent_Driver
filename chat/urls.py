from django.urls import path
from . import views

urlpatterns = [
    path('room/<int:booking_id>/', views.ChatRoomView.as_view(), name='chat_room'),
    path('api/messages/<int:booking_id>/', views.chat_messages, name='chat_messages'),
]
