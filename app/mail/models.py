from django.db import models

from core.models import AliveManager, TimeStamped


class Subscriber(TimeStamped):
    email = models.EmailField()
    email_hash = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, default="pending")  # pending active unsubscribed
    prefs = models.JSONField(default=dict, blank=True)
    confirm_token = models.CharField(max_length=64, blank=True)
    manage_token = models.CharField(max_length=64, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class MailTemplate(TimeStamped):
    key = models.SlugField(unique=True)
    subject = models.CharField(max_length=80)
    body_md = models.TextField()
    objects = AliveManager()
    all_objects = models.Manager()


class Suppression(TimeStamped):
    email_hash = models.CharField(max_length=64, unique=True)
    reason = models.CharField(max_length=40, default="bounce")
    objects = AliveManager()
    all_objects = models.Manager()
