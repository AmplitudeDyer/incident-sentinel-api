from __future__ import annotations

from django.db import models


class Brief(models.Model):
    """Persisted mission-brief payloads and generated plans."""

    mission_title = models.CharField(max_length=255)
    request_payload = models.JSONField()
    response_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Brief #{self.pk}: {self.mission_title}"
