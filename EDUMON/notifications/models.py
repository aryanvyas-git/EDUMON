from django.conf import settings
from django.db import models


class Notification(models.Model):
    """An in-app notification delivered to a user, fired by signals (R1k, R1l)."""

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    verb = models.CharField(max_length=255)
    target = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient}: {self.verb}'
