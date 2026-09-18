from django.db import models

from core.models import AliveManager, TimeStamped


class RedirectRule(TimeStamped):
    src = models.CharField(max_length=200, unique=True)
    dst = models.CharField(max_length=200)
    code = models.PositiveSmallIntegerField(default=301)
    objects = AliveManager()
    all_objects = models.Manager()
