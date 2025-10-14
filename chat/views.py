from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden
from .models import ChatMessage
from core.models import Booking
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

User = get_user_model()

class ChatRoomView(View):
    def get(self, request, booking_id):
        # Only allow access if user is authenticated (JWT or session)
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden('You must be logged in to view this chat room.')
        return render(request, 'chat/chat_room.html', {'booking_id': booking_id})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_messages(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
    user = request.user
    # Only allow customer or driver of the booking
    if not (user == booking.ride_request.customer or user == booking.driver):
        return JsonResponse({'error': 'You are not allowed to access this chat.'}, status=403)
    if request.method == 'GET':
        messages = ChatMessage.objects.filter(booking_id=booking_id).order_by('timestamp')
        data = [
            {
                'sender': m.sender.username,
                'message': m.message,
                'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            } for m in messages
        ]
        return JsonResponse({'messages': data})
    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        msg = ChatMessage.objects.create(
            booking_id=booking_id,
            sender=request.user,
            message=body.get('message', '')
        )
        return JsonResponse({'status': 'ok', 'id': msg.id})
    return JsonResponse({'error': 'Invalid method'}, status=405)