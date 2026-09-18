from __future__ import annotations

from django.db import models
from django.utils import timezone


class TimeStamped(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])


class AliveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class FeatureFlag(TimeStamped):
    key = models.CharField(max_length=80, unique=True)
    value = models.JSONField()
    note = models.CharField(max_length=200, blank=True)

    objects = AliveManager()
    all_objects = models.Manager()

    def __str__(self) -> str:
        return self.key


class SiteSetting(TimeStamped):
    """单行。"""

    notice = models.CharField(max_length=80, blank=True)
    maintenance = models.BooleanField(default=False)
    maintenance_until = models.DateTimeField(null=True, blank=True)
    card_shop_url = models.URLField(blank=True)
    flags_version = models.PositiveIntegerField(default=1)
    supporter_price = models.CharField(max_length=40, blank=True, default="价格见发卡站")
    from_email = models.EmailField(blank=True)
    extra = models.JSONField(default=dict, blank=True)

    objects = AliveManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> SiteSetting:
        obj, _ = cls.all_objects.get_or_create(pk=1)
        return obj


class AuditLog(models.Model):
    actor_id = models.BigIntegerField(null=True, blank=True)
    action = models.CharField(max_length=80)
    obj_type = models.CharField(max_length=80)
    obj_id = models.CharField(max_length=80, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-at"]


class StateTransition(models.Model):
    obj_type = models.CharField(max_length=80)
    obj_id = models.CharField(max_length=80)
    from_state = models.CharField(max_length=40)
    to_state = models.CharField(max_length=40)
    actor_id = models.BigIntegerField(null=True, blank=True)
    reason = models.CharField(max_length=200)
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-at"]
