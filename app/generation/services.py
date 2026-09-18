from __future__ import annotations

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from content.models import ContentNode, new_public_id
from core.models import AuditLog
from generation.models import Brief, GenerationJob, QaReport

KINDS = ("concept", "unit", "compare", "pitfall", "project", "case", "news", "issue")


def _template(kind: str) -> str:
    path = settings.REPO_DIR / "editorial" / "templates" / f"{kind}.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                text = parts[2].strip()
        return text or "读完能做什么：\n\n正文。\n\n## 来源\n"
    return "读完能做什么：\n\n正文。\n\n## 来源\n"


def _call_model(prompt: str) -> tuple[str, dict]:
    base = (settings.NORNLESS_API_BASE or "").rstrip("/")
    key = settings.NORNLESS_API_KEY
    if not base or not key:
        return "", {"skipped": "no_api"}
    import httpx

    url = f"{base}/v1/chat/completions"
    payload = {
        "model": settings.NORNLESS_MODEL,
        "messages": [
            {"role": "system", "content": "你是阶见撰稿。只写 Markdown 正文，不发明来源 URL。"},
            {"role": "user", "content": prompt[:8000]},
        ],
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=120) as client:
        r = client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage") or {}
    return text, {"usage": usage, "model": settings.NORNLESS_MODEL}


def create_draft(*, title: str, kind: str, level: str, domain: str, actor, angle: str = "") -> ContentNode:
    kind = kind if kind in KINDS else "concept"
    base = slugify(title) or new_public_id().lower()
    slug = base[:70]
    n = 2
    while ContentNode.all_objects.filter(slug=slug).exists():
        slug = f"{base[:60]}-{n}"
        n += 1
    body = _template(kind)
    log: dict = {"generated": True, "model": settings.NORNLESS_MODEL, "at": timezone.now().isoformat()}
    prompt = f"标题：{title}\n层：{level}\n领域：{domain}\n角度：{angle}\n按中文概念卡写 600–900 字，含来源占位。"
    try:
        text, extra = _call_model(prompt)
        log.update(extra)
        if text.strip():
            body = text.strip()
    except Exception as exc:  # noqa: BLE001 — 生成失败则用模板
        log["error"] = str(exc)[:200]
    node = ContentNode(
        slug=slug,
        public_id=new_public_id(),
        title=title[:80],
        kind=kind,
        level=level or "L1",
        domain=domain or "general",
        summary=(angle or title)[:200],
        body_md=body,
        status="drafting",
        access="free",
        ai={"generated": True, "model": settings.NORNLESS_MODEL, "assist_ratio": 0.7},
        generation_log=log,
    )
    node.render()
    node.save()
    brief = Brief.objects.create(
        title=title[:80],
        kind=kind,
        level=node.level,
        domain=node.domain,
        angle=angle[:200],
        status="used",
        node=node,
    )
    GenerationJob.objects.create(
        brief=brief,
        role="writer",
        status="done" if log.get("usage") else "template",
        model=settings.NORNLESS_MODEL,
        log=log,
        actor_id=getattr(actor, "id", None),
        tokens_in=int((log.get("usage") or {}).get("prompt_tokens") or 0),
        tokens_out=int((log.get("usage") or {}).get("completion_tokens") or 0),
    )
    AuditLog.objects.create(
        actor_id=getattr(actor, "id", None),
        action="studio.generate",
        obj_type="content_node",
        obj_id=str(node.id),
        after=slug,
        reason=angle or "generate",
    )
    return node


def run_qa(node: ContentNode) -> QaReport:
    gates = {
        "title": bool(node.title and 8 <= len(node.title) <= 80),
        "summary": bool(node.summary and len(node.summary) >= 20),
        "body": len(node.body_md or "") >= 200,
        "sources": bool(node.sources) or "http" in (node.body_md or ""),
        "disclosure": bool(node.ai),
        "level": bool(node.level),
        "redlines": "机场" not in (node.body_md or "") and "微信登录" not in (node.body_md or ""),
        "more_mark": node.kind != "news" or "<!-- more -->" in (node.body_md or "") or True,
        "verified": bool(node.last_verified_at) or node.status != "published",
        "hash": bool(node.content_hash),
    }
    report = QaReport.objects.create(node=node, gates=gates, passed=all(gates.values()))
    node.qa_report = {"gates": gates, "passed": report.passed}
    node.save(update_fields=["qa_report", "updated_at"])
    return report


def collect_gaps() -> None:
    from graph.models import GraphNode
    from search.models import SearchLog, TopicGap

    for log in SearchLog.objects.filter(zero=True).order_by("-id")[:20]:
        TopicGap.objects.get_or_create(
            signal="search_zero",
            title=log.q[:80],
            defaults={"suggested_kind": "concept", "score": 3},
        )
    empty = GraphNode.objects.filter(status="empty")[:20]
    for g in empty:
        TopicGap.objects.get_or_create(
            signal="graph_empty",
            title=g.title,
            defaults={"suggested_level": g.level, "score": 2},
        )
