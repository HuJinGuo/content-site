from django.conf import settings
from django.db import models

from core.models import AliveManager, TimeStamped


class AskThread(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    answer = models.TextField(blank=True)
    citations = models.JSONField(default=list, blank=True)
    tokens = models.PositiveIntegerField(default=0)
    model = models.CharField(max_length=40, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()
