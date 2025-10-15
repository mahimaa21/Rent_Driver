from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("api/health/", views.health_check, name="health_check"),
    path("api/info/", views.server_info, name="server_info"),
path("", TemplateView.as_view(template_name="health.html"), name="health_dashboard"),
]