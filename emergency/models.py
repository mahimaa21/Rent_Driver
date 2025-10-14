# emergency/models.py
from django.db import models
from django.conf import settings

# 🔹 Emergency Contact (per-user)
class EmergencyContact(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_contact"
    )
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"


# 🔹 Emergency Alert (triggered history)
class EmergencyAlert(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_alerts"
    )
    contact = models.ForeignKey(
        EmergencyContact,
        on_delete=models.CASCADE,
        related_name="alerts"
    )
    triggered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("sent", "Sent"), ("failed", "Failed")],
        default="sent"
    )

    def __str__(self):
        return f"Alert by {self.user.username} → {self.contact.phone_number}"