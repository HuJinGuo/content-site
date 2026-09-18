from django.db import models

from core.models import AliveManager, TimeStamped


class Source(TimeStamped):
    name = models.CharField(max_length=80)
    url = models.URLField()
    tier = models.CharField(max_length=20, default="official")
    objects = AliveManager()
    all_objects = models.Manager()


class Issue(TimeStamped):
    kind = models.CharField(max_length=20)  # daily weekly outdated deep
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    published_at = models.DateTimeField(null=True, blank=True)
    body_md = models.TextField(blank=True)
    html = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="published")
    items = models.JSONField(default=list)
    objects = AliveManager()
    all_objects = models.Manager()
