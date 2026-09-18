from django.conf import settings
from django.db import models

from core.models import AliveManager, TimeStamped


class Assessment(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    answers = models.JSONField(default=dict)
    suggested_level = models.CharField(max_length=4, blank=True)
    suggested_path = models.SlugField(blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class Progress(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "node"], name="uniq_progress")]


class Bookmark(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE)
    objects = AliveManager()
    all_objects = models.Manager()


class Highlight(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE)
    quote = models.CharField(max_length=400)
    objects = AliveManager()
    all_objects = models.Manager()


class ErrorReport(TimeStamped):
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE, related_name="error_reports")
    body = models.CharField(max_length=500)
    email = models.EmailField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="open")
    objects = AliveManager()
    all_objects = models.Manager()


class DigestAction(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue_slug = models.SlugField()
    item_key = models.CharField(max_length=80)
    done = models.BooleanField(default=False)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "issue_slug", "item_key"], name="uniq_digest_action")]
