from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from django.utils import timezone

from core.services import snapshot


@dataclass
class Entitlements:
    keys: set[str] = field(default_factory=set)
    ask_quota: int = 0
    groups: set[str] = field(default_factory=set)

    def has(self, key: str) -> bool:
        return key in self.keys


def entitlements(user) -> Entitlements:
    flags = snapshot()
    result = Entitlements()
    if user is None or not getattr(user, "is_authenticated", False):
        return result
    result.ask_quota = 3 if flags.get("ask.enabled") else 0
    now = timezone.now()
    from accounts.models import Entitlement, Membership

    for _m in Membership.objects.filter(user=user, start_at__lte=now, end_at__gte=now):
        result.keys.update({"ad_free", "paid_content", "assets_all", "member_rss"})
        result.ask_quota = 20
    for e in Entitlement.objects.filter(user=user):
        if e.expire_at and e.expire_at < now:
            continue
        result.keys.add(e.key)
        if e.key.startswith("group:"):
            result.groups.add(e.key.split(":", 1)[1])
    return result


def visible(user, node) -> bool:
    if getattr(node, "deleted_at", None):
        return False
    status = getattr(node, "status", "")
    if status not in {"published", "archived"}:
        return False
    if node.access == "group":
        ent = entitlements(user)
        gid = getattr(node, "group_slug", "") or ""
        return gid in ent.groups
    return True


def can_read_full(user, node) -> bool:
    flags = snapshot()
    if not flags.get("paywall.enabled"):
        return True
    if node.access == "free":
        return True
    ent = entitlements(user)
    if node.access == "supporter":
        return ent.has("paid_content")
    if node.access == "code":
        if ent.has("paid_content"):
            return True
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        from codes.models import ContentUnlock

        return ContentUnlock.objects.filter(user=user, node=node).exists()
    if node.access == "group":
        gid = getattr(node, "group_slug", "") or ""
        return gid in entitlements(user).groups
    return False


def sees_ads(user, slot: str = "S3") -> bool:
    flags = snapshot()
    if not flags.get("ads.enabled"):
        return False
    if slot in {"S3", "S4", "S5", "S6"} and entitlements(user).has("ad_free"):
        return False
    return True


STAFF_ACTIONS = {
    "create_draft": {"author", "editor", "publisher", "admin"},
    "factcheck": {"factchecker", "editor", "publisher", "admin"},
    "edit": {"editor", "publisher", "admin"},
    "publish": {"publisher", "admin"},
    "ads": {"adops", "admin"},
    "codes": {"finance", "admin"},
    "users": {"ops", "admin"},
    "flags": {"admin"},
    "audit": {"ops", "finance", "adops", "admin"},
}


def can(actor, action: str, obj=None) -> bool:
    if actor is None or not getattr(actor, "is_authenticated", False):
        return False
    if actor.is_superuser or actor.staff_role == "admin":
        return True
    allowed = STAFF_ACTIONS.get(action, set())
    return actor.staff_role in allowed


def grant_membership(user, *, days: int, source: str, actor=None) -> None:
    from accounts.models import Entitlement, Membership

    now = timezone.now()
    Membership.objects.create(user=user, start_at=now, end_at=now + timedelta(days=days), source=source)
    for key in ("ad_free", "paid_content", "assets_all", "member_rss"):
        Entitlement.objects.get_or_create(
            user=user, key=key, source=source, defaults={"expire_at": now + timedelta(days=days)}
        )
