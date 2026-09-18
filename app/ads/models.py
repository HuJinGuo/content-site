from django.conf import settings
from django.db import models

from core.models import AliveManager, TimeStamped


class AdSlot(TimeStamped):
    key = models.CharField(max_length=10, unique=True)  # R1 S3
    name = models.CharField(max_length=40)
    objects = AliveManager()
    all_objects = models.Manager()


class AdCampaign(TimeStamped):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    status = models.CharField(max_length=20, default="draft")
    objects = AliveManager()
    all_objects = models.Manager()


class AdCreative(TimeStamped):
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name="creatives")
    public_id = models.CharField(max_length=16, unique=True, blank=True)
    title = models.CharField(max_length=80)
    body = models.CharField(max_length=200)
    url = models.URLField()
    status = models.CharField(max_length=20, default="review")
    objects = AliveManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.public_id:
            from content.models import new_public_id

            self.public_id = new_public_id()
        super().save(*args, **kwargs)


class HouseAd(TimeStamped):
    slot = models.CharField(max_length=10)
    title = models.CharField(max_length=80)
    body = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    objects = AliveManager()
    all_objects = models.Manager()


class GoClick(models.Model):
    public_id = models.CharField(max_length=16)
    at = models.DateTimeField(auto_now_add=True)
    slot = models.CharField(max_length=10, blank=True)
