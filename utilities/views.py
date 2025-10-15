from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic backend health check.
    """
    return Response({
        "status": "ok",
        "database": "connected",  # can expand later
        "time": timezone.now(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def server_info(request):
    """
    Returns general backend info (for debugging).
    """
    return Response({
        "app_name": "Rent a Driver",
        "version": "1.0.0",
        "debug": settings.DEBUG,
        "timezone": settings.TIME_ZONE,
        "installed_apps": [app for app in settings.INSTALLED_APPS if app.startswith("core") or app in ["emergency", "utilities"]],
        "server_time": timezone.now(),
    })