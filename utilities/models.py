from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SystemLog(models.Model):
    """
    Utility model to store system-level logs or events.
    Helps in tracking backend actions for debugging or audit purposes.
    """

    LEVEL_CHOICES = [
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="User who triggered the action (if applicable)."
    )
    action = models.CharField(max_length=255, help_text="What action happened.")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="INFO")
    timestamp = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(blank=True, null=True, help_text="Optional JSON details about the event.")

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"

    def __str__(self):
        return f"[{self.level}] {self.action} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"