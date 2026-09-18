from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from core.models import AliveManager, TimeStamped

ROLES = [
    ("", "读者"),
    ("advertiser", "广告主"),
    ("author", "作者 bot"),
    ("factchecker", "事实核查"),
    ("editor", "编辑"),
    ("publisher", "主编"),
    ("adops", "广告运营"),
    ("ops", "运营"),
    ("finance", "财务"),
    ("admin", "站长"),
]


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra):
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, email: str, password: str, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("staff_role", "admin")
        return self.create_user(email, password, **extra)

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=40, blank=True)
    staff_role = models.CharField(max_length=20, blank=True, choices=ROLES)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    delete_requested_at = models.DateTimeField(null=True, blank=True)
    git_token_hash = models.CharField(max_length=64, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()
    all_objects = models.Manager()

    def __str__(self) -> str:
        return self.display_name or self.email

    @property
    def is_backoffice(self) -> bool:
        return bool(self.staff_role) or self.is_superuser


class TotpDevice(TimeStamped):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="totp")
    secret = models.CharField(max_length=64)
    confirmed = models.BooleanField(default=False)
    objects = AliveManager()
    all_objects = models.Manager()


class AdvertiserProfile(TimeStamped):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="advertiser")
    org_name = models.CharField(max_length=80)
    verified = models.BooleanField(default=False)
    objects = AliveManager()
    all_objects = models.Manager()


class Membership(TimeStamped):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="memberships")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    source = models.CharField(max_length=40, default="code")
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["-end_at"]


class Entitlement(TimeStamped):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="entitlements")
    key = models.CharField(max_length=40)
    expire_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=40)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "key", "source"], name="uniq_entitlement"),
        ]


class Group(TimeStamped):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    objects = AliveManager()
    all_objects = models.Manager()


class GroupMember(TimeStamped):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["group", "user"], name="uniq_group_member")]


class MagicLink(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ua_hash = models.CharField(max_length=64, blank=True)
