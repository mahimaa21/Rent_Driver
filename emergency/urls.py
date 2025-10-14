# emergency/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/set/", views.set_contact, name="set_emergency_contact"),
    path("api/get/", views.get_contact, name="get_emergency_contact"),
    path("api/alert/", views.trigger_alert, name="trigger_alert"),
    path("api/history/", views.alert_history, name="alert_history"),
]