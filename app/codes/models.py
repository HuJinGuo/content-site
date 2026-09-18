from __future__ import annotations

import hashlib
import secrets

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from core.models import AliveManager, TimeStamped

CODE_KINDS = [("member", "会员码"), ("content", "内容码"), ("ad", "广告码")]
CODE_STATUS = [("unused", "未兑"), ("redeemed", "已兑"), ("void", "作废")]


def hash_code(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


class CodeBatch(TimeStamped):
    kind = models.CharField(max_length=20, choices=CODE_KINDS)
    note = models.CharField(max_length=120, blank=True)
    days = models.PositiveIntegerField(default=31)
    created_by_id = models.BigIntegerField(null=True, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class Code(TimeStamped):
    batch = models.ForeignKey(CodeBatch, on_delete=models.CASCADE, related_name="codes")
    kind = models.CharField(max_length=20, choices=CODE_KINDS)
    code_hash = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=CODE_STATUS, default="unused")
    days = models.PositiveIntegerField(default=31)
    last4 = models.CharField(max_length=4, blank=True)
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="redeemed_codes"
    )
    redeemed_at = models.DateTimeField(null=True, blank=True)
    node_slug = models.SlugField(blank=True)  # content 码绑定
    objects = AliveManager()
    all_objects = models.Manager()


class ContentUnlock(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    node = models.ForeignKey("content.ContentNode", on_delete=models.CASCADE)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "node"], name="uniq_unlock")]


def generate_plain() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    raw = "".join(secrets.choice(alphabet) for _ in range(12))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:12]}"


@transaction.atomic
def issue_codes(*, kind: str, count: int, days: int, actor, reason: str, node_slug: str = "") -> tuple[CodeBatch, list[str]]:
    if not reason:
        raise ValueError("reason required")
    batch = CodeBatch.objects.create(kind=kind, days=days, note=reason, created_by_id=getattr(actor, "id", None))
    plains: list[str] = []
    for _ in range(count):
        plain = generate_plain()
        Code.objects.create(
            batch=batch,
            kind=kind,
            code_hash=hash_code(plain),
            days=days,
            node_slug=node_slug,
            last4=plain[-4:],
        )
        plains.append(plain)
    from core.models import AuditLog

    AuditLog.objects.create(
        actor_id=getattr(actor, "id", None),
        action="codes.issue",
        obj_type="code_batch",
        obj_id=str(batch.id),
        after={"count": count, "kind": kind},
        reason=reason,
    )
    return batch, plains


class RedeemError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


@transaction.atomic
def redeem(user, plain: str) -> Code:
    from access.services import grant_membership
    from content.models import ContentNode

    normalized = (plain or "").strip().upper().replace(" ", "")
    if not normalized:
        raise RedeemError("empty", "请输入兑换码。")
    digest = hash_code(normalized)
    try:
        code = Code.objects.select_for_update().get(code_hash=digest)
    except Code.DoesNotExist as exc:
        raise RedeemError("invalid", "这张码无效。") from exc
    if code.status == "void":
        raise RedeemError("void", "这张码已作废。")
    if code.status == "redeemed":
        raise RedeemError("used", "这张码已经被兑过。")
    flags = __import__("core.services", fromlist=["snapshot"]).snapshot()
    if code.kind == "member" and not flags.get("supporter.enabled"):
        # 开关关时仍允许兑会员码（权益键存在），定价页 404 但不挡兑码
        pass
    if code.kind == "content" and not flags.get("paywall.enabled"):
        raise RedeemError("paywall_off", "现在没有需要内容码解锁的文章。")
    code.status = "redeemed"
    code.redeemed_by = user
    code.redeemed_at = timezone.now()
    code.save()
    if code.kind == "member":
        grant_membership(user, days=code.days, source=f"code:{code.id}")
    elif code.kind == "content":
        node = ContentNode.objects.filter(slug=code.node_slug).first()
        if node:
            ContentUnlock.objects.get_or_create(user=user, node=node)
    elif code.kind == "ad":
        from accounts.models import User

        user.staff_role = user.staff_role or "advertiser"
        User.objects.filter(pk=user.pk).update(staff_role=user.staff_role)
    return code


@transaction.atomic
def void_plain(*, plain: str, actor, reason: str) -> Code:
    if not reason:
        raise ValueError("reason required")
    normalized = (plain or "").strip().upper().replace(" ", "")
    digest = hash_code(normalized)
    try:
        code = Code.objects.select_for_update().get(code_hash=digest)
    except Code.DoesNotExist as exc:
        raise RedeemError("invalid", "这张码无效。") from exc
    if code.status == "redeemed":
        raise RedeemError("used", "已兑的码不能作废，请改收回权益。")
    prev = code.status
    code.status = "void"
    code.save(update_fields=["status", "updated_at"])
    from core.models import AuditLog

    AuditLog.objects.create(
        actor_id=getattr(actor, "id", None),
        action="codes.void",
        obj_type="code",
        obj_id=str(code.id),
        before=prev,
        after="void",
        reason=reason,
    )
    return code
