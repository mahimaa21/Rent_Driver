from django.shortcuts import render

# Create your views here.
# emergency/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import EmergencyContact, EmergencyAlert
from .serializers import EmergencyContactSerializer


# ===============================================================
# ================ AUTHENTICATED EMERGENCY VIEWS =================
# ===============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_contact(request):
    """Authenticated users create/update their emergency contact."""
    phone = request.data.get("phone_number")

    if not phone:
        return Response({"error": "Phone number required"}, status=400)

    # If contact exists, update instead of duplicate
    contact, created = EmergencyContact.objects.update_or_create(
        user=request.user,
        defaults={"phone_number": phone}
    )

    serializer = EmergencyContactSerializer(contact)
    return Response({
        "message": "✅ Contact saved successfully",
        "contact": serializer.data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_contact(request):
    """Fetch the authenticated user's emergency contact."""
    try:
        contact = EmergencyContact.objects.get(user=request.user)
        serializer = EmergencyContactSerializer(contact)
        return Response(serializer.data)
    except EmergencyContact.DoesNotExist:
        return Response({"error": "No contact found for this user"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_alert(request):
    """Trigger an emergency alert for the authenticated user."""
    try:
        contact = EmergencyContact.objects.get(user=request.user)
    except EmergencyContact.DoesNotExist:
        return Response({"error": "Set an emergency contact first"}, status=404)

    alert = EmergencyAlert.objects.create(
        user=request.user,
        contact=contact,
        status="sent"
    )

    return Response({
        "message": f"🚨 Alert triggered to {contact.phone_number}",
        "alert_id": alert.id,
        "time": alert.triggered_at
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def alert_history(request):
    """Return recent alerts for this user only."""
    alerts = EmergencyAlert.objects.filter(user=request.user).order_by("-triggered_at")[:10]
    data = [
        {"contact": a.contact.phone_number, "status": a.status, "time": a.triggered_at}
        for a in alerts
    ]
    return Response(data)