from django.db import models

from core.models import AliveManager, TimeStamped


class JobPost(TimeStamped):
    title = models.CharField(max_length=80)
    org = models.CharField(max_length=80)
    url = models.URLField()
    expires_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="published")
    objects = AliveManager()
    all_objects = models.Manager()


class Launch(TimeStamped):
    title = models.CharField(max_length=80)
    body = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default="published")
    objects = AliveManager()
    all_objects = models.Manager()


class EventItem(TimeStamped):
    title = models.CharField(max_length=80)
    when = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default="published")
    objects = AliveManager()
    all_objects = models.Manager()


class Deal(TimeStamped):
    title = models.CharField(max_length=80)
    body = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default="published")
    objects = AliveManager()
    all_objects = models.Manager()


class SponsoredPost(TimeStamped):
    title = models.CharField(max_length=80)
    body_md = models.TextField()
    status = models.CharField(max_length=20, default="draft")
    objects = AliveManager()
    all_objects = models.Manager()
