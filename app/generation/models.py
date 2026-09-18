from django.db import models

from core.models import AliveManager, TimeStamped


class Brief(TimeStamped):
    title = models.CharField(max_length=80)
    kind = models.CharField(max_length=20, default="concept")
    level = models.CharField(max_length=4, default="L1")
    domain = models.CharField(max_length=20, default="general")
    angle = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="open")
    node = models.ForeignKey("content.ContentNode", null=True, blank=True, on_delete=models.SET_NULL)
    objects = AliveManager()
    all_objects = models.Manager()


class PromptVersion(TimeStamped):
    name = models.CharField(max_length=40)
    version = models.CharField(max_length=20)
    body = models.TextField()
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "version"], name="uniq_prompt_ver")]


class GenerationJob(TimeStamped):
    brief = models.ForeignKey(Brief, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=20, default="writer")
    status = models.CharField(max_length=20, default="queued")
    model = models.CharField(max_length=40, blank=True)
    prompt_version = models.CharField(max_length=40, blank=True)
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    cost_cents = models.PositiveIntegerField(default=0)
    log = models.JSONField(default=dict, blank=True)
    actor_id = models.BigIntegerField(null=True, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class FactClaim(TimeStamped):
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE, related_name="claims")
    claim = models.CharField(max_length=240)
    source_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default="open")  # open verified disputed
    objects = AliveManager()
    all_objects = models.Manager()


class QaReport(TimeStamped):
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE, related_name="qa_reports")
    gates = models.JSONField(default=dict)
    passed = models.BooleanField(default=False)
    objects = AliveManager()
    all_objects = models.Manager()
