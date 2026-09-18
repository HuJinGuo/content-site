from django.db import models

from core.models import TimeStamped


class ServerEvent(models.Model):
    name = models.CharField(max_length=40)
    props = models.JSONField(default=dict, blank=True)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-at"]


class MetricsDaily(TimeStamped):
    day = models.DateField(unique=True)
    numbers = models.JSONField(default=dict, blank=True)
