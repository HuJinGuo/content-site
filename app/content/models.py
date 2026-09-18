from __future__ import annotations

import hashlib
import json
from pathlib import Path

import frontmatter
from django.db import models
from django.utils import timezone
from markdown_it import MarkdownIt
from mdit_py_plugins.gfm import gfm_plugin

from core.models import AliveManager, StateTransition, TimeStamped

KINDS = [
    ("concept", "概念卡"),
    ("unit", "教程单元"),
    ("compare", "对照"),
    ("pitfall", "坑"),
    ("project", "项目课"),
    ("case", "案例"),
    ("news", "快讯"),
    ("issue", "期刊"),
    ("entity", "实体"),
    ("glossary", "术语"),
    ("asset", "资源"),
    ("lab", "实验"),
    ("quiz", "测验"),
]
STATUSES = [
    ("idea", "选题"),
    ("assigned", "已派"),
    ("researching", "调研"),
    ("drafting", "起草"),
    ("machine_qa", "机审"),
    ("factcheck", "事实清单"),
    ("editing", "编辑"),
    ("legal", "法务"),
    ("scheduled", "排期"),
    ("published", "已发布"),
    ("needs_update", "待更新"),
    ("archived", "作废"),
]
ACCESS = [("free", "免费"), ("supporter", "支持者"), ("code", "内容码"), ("group", "分组")]

md = MarkdownIt("commonmark", {"typographer": False}).use(gfm_plugin)

ALLOWED = {
    "idea": {"assigned", "researching"},
    "assigned": {"researching", "drafting"},
    "researching": {"drafting"},
    "drafting": {"machine_qa", "idea"},
    "machine_qa": {"factcheck", "drafting"},
    "factcheck": {"editing", "drafting"},
    "editing": {"scheduled", "published", "legal", "drafting"},
    "legal": {"scheduled", "editing"},
    "scheduled": {"published", "editing"},
    "published": {"needs_update", "archived"},
    "needs_update": {"editing", "archived", "published"},
    "archived": set(),
}


class ContentNode(TimeStamped):
    slug = models.SlugField(max_length=80, unique=True)
    public_id = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=80)
    kind = models.CharField(max_length=20, choices=KINDS)
    level = models.CharField(max_length=4, default="L1")
    domain = models.CharField(max_length=20, default="general")
    track = models.SlugField(blank=True)
    unit_index = models.PositiveSmallIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=200)
    body_md = models.TextField()
    html = models.TextField(blank=True)
    content_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="drafting")
    access = models.CharField(max_length=20, choices=ACCESS, default="free")
    group_slug = models.SlugField(blank=True)
    tags = models.JSONField(default=list)
    sources = models.JSONField(default=list)
    node_ids = models.JSONField(default=list)
    prereqs = models.JSONField(default=list)
    next_nodes = models.JSONField(default=list)
    ai = models.JSONField(default=dict)
    published_at = models.DateTimeField(null=True, blank=True)
    last_verified_at = models.DateField(null=True, blank=True)
    review_by = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    changelog = models.JSONField(default=list)
    generation_log = models.JSONField(null=True, blank=True)
    qa_report = models.JSONField(null=True, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["-published_at", "-id"]

    def __str__(self) -> str:
        return self.title

    def render(self) -> None:
        self.html = md.render(self.body_md or "")
        self.content_hash = hashlib.sha256(self.body_md.encode()).hexdigest()

    def preview_and_rest(self) -> tuple[str, str]:
        text = self.body_md or ""
        if "<!-- more -->" in text:
            head, rest = text.split("<!-- more -->", 1)
        else:
            cut = max(int(len(text) * 0.3), 1)
            # 段落边界
            para = text.rfind("\n\n", 0, cut)
            head = text[: para if para > 40 else cut]
            rest = text[len(head) :]
        return md.render(head), rest


class ContentVersion(TimeStamped):
    node = models.ForeignKey(ContentNode, on_delete=models.CASCADE, related_name="versions")
    body_md = models.TextField()
    editor_id = models.BigIntegerField(null=True, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class GlossaryTerm(TimeStamped):
    term = models.CharField(max_length=40, unique=True)
    definition = models.CharField(max_length=60)
    body = models.CharField(max_length=300, blank=True)
    node = models.ForeignKey(ContentNode, null=True, blank=True, on_delete=models.SET_NULL)
    objects = AliveManager()
    all_objects = models.Manager()


class StaticPage(TimeStamped):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    body_md = models.TextField()
    html = models.TextField(blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class Erratum(TimeStamped):
    node = models.ForeignKey(ContentNode, on_delete=models.CASCADE, related_name="errata")
    body = models.CharField(max_length=200)
    published_at = models.DateTimeField(default=timezone.now)
    objects = AliveManager()
    all_objects = models.Manager()


class Feedback(TimeStamped):
    node = models.ForeignKey(ContentNode, on_delete=models.CASCADE, related_name="feedbacks")
    kind = models.CharField(max_length=20)  # useful / unclear / errata
    note = models.CharField(max_length=200, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


class Asset(TimeStamped):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    access = models.CharField(max_length=20, default="free")
    path = models.CharField(max_length=200, blank=True)
    note = models.CharField(max_length=200, blank=True)
    objects = AliveManager()
    all_objects = models.Manager()


def new_public_id() -> str:
    import secrets

    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    return "".join(secrets.choice(alphabet) for _ in range(12))


def transition(node: ContentNode, to: str, actor, reason: str) -> ContentNode:
    if not reason:
        raise ValueError("reason required")
    allowed = ALLOWED.get(node.status, set())
    if to not in allowed:
        raise ValueError(f"illegal {node.status} → {to}")
    from access.services import can

    if to == "published" and not can(actor, "publish"):
        raise PermissionError("publish denied")
    if actor is not None and getattr(actor, "staff_role", "") == "author" and to == "published":
        raise PermissionError("bot cannot publish")
    prev = node.status
    node.status = to
    if to == "published" and not node.published_at:
        node.published_at = timezone.now()
    node.save()
    StateTransition.objects.create(
        obj_type="content_node",
        obj_id=str(node.id),
        from_state=prev,
        to_state=to,
        actor_id=getattr(actor, "id", None),
        reason=reason,
    )
    from core.models import AuditLog

    AuditLog.objects.create(
        actor_id=getattr(actor, "id", None),
        action="content.transition",
        obj_type="content_node",
        obj_id=str(node.id),
        before=prev,
        after=to,
        reason=reason,
    )
    return node


def _jsonable(obj):
    from datetime import date, datetime

    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.date().isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


def _as_date(val):
    from datetime import date, datetime

    if val in (None, ""):
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return val


def import_markdown(path: Path) -> ContentNode:
    post = frontmatter.load(str(path))
    meta = dict(post.metadata)
    slug = meta["slug"]
    node, _ = ContentNode.all_objects.get_or_create(
        slug=slug,
        defaults={
            "public_id": new_public_id(),
            "title": meta.get("title", slug),
            "kind": meta.get("kind", "concept"),
            "summary": meta.get("summary", "")[:200],
            "body_md": post.content,
        },
    )
    node.title = meta.get("title", node.title)
    node.kind = meta.get("kind", node.kind)
    node.level = meta.get("level", node.level)
    node.domain = meta.get("domain", node.domain)
    node.track = meta.get("track", "") or ""
    node.unit_index = meta.get("unit_index")
    node.summary = (meta.get("summary") or "")[:200]
    node.body_md = post.content
    node.access = meta.get("access", "free")
    node.tags = _jsonable(meta.get("tags") or [])
    node.sources = _jsonable(meta.get("sources") or [])
    node.node_ids = _jsonable(meta.get("node_ids") or [])
    node.prereqs = _jsonable(meta.get("prereqs") or [])
    node.next_nodes = _jsonable(meta.get("next") or [])
    node.ai = _jsonable(meta.get("ai") or {})
    if meta.get("last_verified_at"):
        node.last_verified_at = _as_date(meta["last_verified_at"])
    if meta.get("review_by"):
        node.review_by = _as_date(meta["review_by"])
    if meta.get("expires_at"):
        node.expires_at = _as_date(meta["expires_at"])
    node.changelog = _jsonable(meta.get("changelog") or [])
    log_path = path.with_suffix(".log.json")
    qa_path = path.with_name(path.stem + ".qa.json")
    if log_path.exists():
        node.generation_log = json.loads(log_path.read_text())
    if qa_path.exists():
        node.qa_report = json.loads(qa_path.read_text())
    node.render()
    if meta.get("status") == "published" or node.status == "published":
        node.status = "published"
        if not node.published_at:
            node.published_at = timezone.now()
    else:
        # 导入已发布稿（样例）默认 published
        if node.status in {"idea", "drafting"} and node.generation_log:
            node.status = "published"
            node.published_at = node.published_at or timezone.now()
        elif node.status in {"idea", "drafting"}:
            node.status = "published"
            node.published_at = node.published_at or timezone.now()
    node.deleted_at = None
    node.save()
    if node.node_ids:
        from graph.models import GraphNode

        GraphNode.objects.filter(node_id__in=node.node_ids).update(status="published")
    if node.track and node.unit_index:
        from graph.models import PathItem

        PathItem.objects.filter(path__slug=node.track, unit_index=node.unit_index).update(node=node)
    return node
