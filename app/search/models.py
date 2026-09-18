from django.db import models

from core.models import AliveManager, TimeStamped


class SearchLog(TimeStamped):
    q = models.CharField(max_length=100)
    zero = models.BooleanField(default=False)
    hits = models.PositiveIntegerField(default=0)
    ip_hash = models.CharField(max_length=64, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class TopicGap(TimeStamped):
    signal = models.CharField(max_length=40)
    title = models.CharField(max_length=80)
    suggested_kind = models.CharField(max_length=20, default="concept")
    suggested_level = models.CharField(max_length=4, default="L1")
    score = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, default="open")  # open adopted ignored
    note = models.CharField(max_length=200, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()
