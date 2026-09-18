from django.db import models

from core.models import AliveManager, TimeStamped


class Entity(TimeStamped):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=20, default="tool")  # tool company paper model
    official_url = models.URLField()
    summary = models.CharField(max_length=200, blank=True)
    claimed = models.BooleanField(default=False)
    facts = models.JSONField(default=dict, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class Claim(TimeStamped):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="claims")
    email = models.EmailField()
    contact = models.CharField(max_length=80, blank=True)
    fields = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default="pending")
    objects = AliveManager()
    all_objects = models.Manager()
