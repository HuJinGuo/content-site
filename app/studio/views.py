from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from content.models import ALLOWED, Asset, ContentNode, Erratum, transition
from generation.models import Brief, FactClaim, GenerationJob, PromptVersion
from generation.services import collect_gaps, create_draft, run_qa
from graph.models import GraphNode, NodeEdge
from news.models import Issue, Source
from search.models import TopicGap
from studio.auth import staff_required


def parse_tags(raw: str) -> list[str]:
    parts = [t.strip()[:40] for t in (raw or "").replace("，", ",").split(",") if t.strip()]
    return parts[:12]


@staff_required("edit")
def studio_posts(request: HttpRequest) -> HttpResponse:
    kind = request.GET.get("kind") or ""
    qs = ContentNode.objects.exclude(status="archived").order_by("-updated_at")
    if kind in {"concept", "unit", "news", "pitfall", "compare", "project"}:
        qs = qs.filter(kind=kind)
    posts = list(qs[:80])
    return render(request, "studio/posts.html", {"posts": posts, "kind": kind})


@staff_required("edit")
def studio_home(request: HttpRequest) -> HttpResponse:
    drafts = ContentNode.objects.exclude(status__in=["published", "archived"])[:40]
    due = ContentNode.objects.filter(status="published", review_by__lt=timezone.now().date())[:10]
    gaps = TopicGap.objects.filter(status="open")[:10]
    jobs = GenerationJob.objects.all()[:8]
    recent = ContentNode.objects.filter(status="published").order_by("-published_at")[:8]
    return render(
        request,
        "studio/home.html",
        {"drafts": drafts, "due": due, "gaps": gaps, "jobs": jobs, "recent": recent},
    )


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_review(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        node = get_object_or_404(ContentNode, slug=request.POST.get("slug"))
        try:
            transition(node, request.POST.get("to") or "", request.user, request.POST.get("reason") or "review")
        except (ValueError, PermissionError) as exc:
            error = str(exc)
    queue = ContentNode.objects.filter(status__in=["factcheck", "editing", "machine_qa", "scheduled"])
    return render(request, "studio/review.html", {"queue": queue, "error": error, "allowed": ALLOWED})


@staff_required("publish")
@require_http_methods(["POST"])
def studio_publish(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, slug=slug)
    reason = request.POST.get("reason") or "publish"
    try:
        transition(node, "published", request.user, reason)
    except (ValueError, PermissionError) as exc:
        queue = ContentNode.objects.filter(status__in=["factcheck", "editing", "machine_qa"])
        return render(request, "studio/review.html", {"queue": queue, "error": str(exc)})
    return redirect("/studio/review")


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_topics(request: HttpRequest) -> HttpResponse:
    collect_gaps()
    error = ""
    if request.method == "POST":
        pk = request.POST.get("id")
        gap = get_object_or_404(TopicGap, pk=pk)
        action = request.POST.get("action")
        if action == "ignore":
            gap.status = "ignored"
            gap.note = (request.POST.get("reason") or "ignore")[:200]
            gap.save()
        elif action == "adopt":
            node = create_draft(
                title=gap.title,
                kind=gap.suggested_kind or "concept",
                level="L1",
                domain="general",
                actor=request.user,
                angle=gap.signal,
            )
            gap.status = "adopted"
            gap.save()
            return redirect(f"/studio/editor/{node.slug}")
    gaps = TopicGap.objects.exclude(status="ignored")[:50]
    return render(request, "studio/topics.html", {"gaps": gaps, "error": error})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_briefs(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        Brief.objects.create(
            title=(request.POST.get("title") or "未命名")[:80],
            kind=request.POST.get("kind") or "concept",
            level="L1",
            domain="general",
            angle=(request.POST.get("angle") or request.POST.get("tags") or "")[:200],
        )
        return redirect("/studio/briefs")
    return render(request, "studio/briefs.html", {"briefs": Brief.objects.all()[:50]})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_generate(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        if not title:
            error = "标题必填。"
        else:
            node = create_draft(
                title=title,
                kind=request.POST.get("kind") or "concept",
                level="L1",
                domain="general",
                actor=request.user,
                angle=request.POST.get("angle") or request.POST.get("tags") or "",
            )
            tags = parse_tags(request.POST.get("tags") or "")
            if tags:
                node.tags = tags
                node.save(update_fields=["tags"])
            return redirect(f"/studio/editor/{node.slug}")
    return render(request, "studio/generate.html", {"error": error, "jobs": GenerationJob.objects.all()[:20]})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_editor_new(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        title = (request.POST.get("title") or "未命名稿").strip()[:80]
        slug = slugify(request.POST.get("slug") or title) or new_slug()
        if ContentNode.all_objects.filter(slug=slug).exists():
            slug = f"{slug}-{new_slug()[-4:]}"
        from content.models import new_public_id

        node = ContentNode(
            slug=slug[:80],
            public_id=new_public_id(),
            title=title,
            kind=request.POST.get("kind") or "concept",
            level="L1",
            domain="general",
            summary=(request.POST.get("summary") or title)[:200],
            body_md=request.POST.get("body_md") or "正文。",
            status="drafting",
            access=request.POST.get("access") or "free",
            track=(request.POST.get("track") or "")[:80],
            tags=parse_tags(request.POST.get("tags") or ""),
        )
        node.render()
        node.save()
        return redirect(f"/studio/editor/{node.slug}")
    return render(request, "studio/editor.html", {"node": None, "next_states": [], "error": ""})


def new_slug() -> str:
    from content.models import new_public_id

    return new_public_id().lower()


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_editor(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, slug=slug)
    error = ""
    if request.method == "POST":
        action = request.POST.get("action") or "save"
        if action == "save":
            node.title = (request.POST.get("title") or node.title)[:80]
            node.summary = (request.POST.get("summary") or node.summary)[:200]
            node.body_md = request.POST.get("body_md") or node.body_md
            node.kind = request.POST.get("kind") or node.kind
            node.access = request.POST.get("access") or node.access
            node.track = request.POST.get("track") or ""
            if "tags" in request.POST:
                node.tags = parse_tags(request.POST.get("tags") or "")
            node.render()
            node.save()
        elif action == "transition":
            try:
                transition(node, request.POST.get("to") or "", request.user, request.POST.get("reason") or "edit")
            except (ValueError, PermissionError) as exc:
                error = str(exc)
                nxt = sorted(ALLOWED.get(node.status, set()))
                return render(request, "studio/editor.html", {"node": node, "next_states": nxt, "error": error})
        return redirect(f"/studio/editor/{node.slug}")
    nxt = sorted(ALLOWED.get(node.status, set()))
    return render(request, "studio/editor.html", {"node": node, "next_states": nxt, "error": error})


# the redirect-on-error path above can return None — fix in a follow-up if needed

@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_qa(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, slug=slug)
    if request.method == "POST":
        run_qa(node)
        return redirect(f"/studio/qa/{node.slug}")
    report = node.qa_reports.first() if hasattr(node, "qa_reports") else None
    return render(request, "studio/qa.html", {"node": node, "report": report})


@staff_required("factcheck")
@require_http_methods(["GET", "POST"])
def studio_facts(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, slug=slug)
    if request.method == "POST":
        if request.POST.get("claim"):
            FactClaim.objects.create(
                node=node,
                claim=request.POST.get("claim")[:240],
                source_url=request.POST.get("source_url") or "",
            )
        cid = request.POST.get("claim_id")
        if cid:
            claim = get_object_or_404(FactClaim, pk=cid, node=node)
            claim.status = request.POST.get("status") or "verified"
            claim.save()
        return redirect(f"/studio/facts/{node.slug}")
    return render(request, "studio/facts.html", {"node": node, "claims": node.claims.all()})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_issues(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        kind = request.POST.get("kind") or "daily"
        slug = request.POST.get("slug") or f"{kind}-{timezone.now().date().isoformat()}"
        Issue.objects.update_or_create(
            slug=slug,
            defaults={
                "kind": kind,
                "title": (request.POST.get("title") or slug)[:80],
                "body_md": request.POST.get("body_md") or "",
                "html": "",
                "status": request.POST.get("status") or "draft",
                "items": [],
            },
        )
        return redirect("/studio/issues")
    return render(request, "studio/issues.html", {"issues": Issue.objects.all()[:40]})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_graph(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        GraphNode.objects.update_or_create(
            node_id=slugify(request.POST.get("node_id") or request.POST.get("title") or "")[:80],
            defaults={
                "title": (request.POST.get("title") or "")[:80],
                "level": "L1",
                "domain": "general",
                "status": request.POST.get("status") or "empty",
            },
        )
    nodes = GraphNode.objects.all().order_by("title", "node_id")
    edges = NodeEdge.objects.select_related("src", "dst")[:80]
    return render(request, "studio/graph.html", {"nodes": nodes, "edges": edges, "error": error})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_sources(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        Source.objects.update_or_create(
            url=request.POST.get("url") or "https://example.com",
            defaults={"name": (request.POST.get("name") or "源")[:80], "tier": request.POST.get("tier") or "official"},
        )
        return redirect("/studio/sources")
    return render(request, "studio/sources.html", {"sources": Source.objects.all()})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_entities(request: HttpRequest) -> HttpResponse:
    from entities.models import Claim, Entity

    if request.method == "POST":
        Entity.objects.update_or_create(
            slug=slugify(request.POST.get("slug") or request.POST.get("name") or "")[:80],
            defaults={
                "name": (request.POST.get("name") or "")[:80],
                "kind": request.POST.get("kind") or "tool",
                "official_url": request.POST.get("official_url") or "https://example.com",
                "summary": (request.POST.get("summary") or "")[:200],
            },
        )
        return redirect("/studio/entities")
    return render(
        request,
        "studio/entities.html",
        {"entities": Entity.objects.all()[:80], "claims": Claim.objects.filter(status="pending")},
    )


@staff_required("edit")
def studio_refresh(request: HttpRequest) -> HttpResponse:
    today = timezone.now().date()
    stale = ContentNode.objects.filter(status="published", review_by__lt=today)
    return render(request, "studio/refresh.html", {"stale": stale})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_errata(request: HttpRequest) -> HttpResponse:
    from learning.models import ErrorReport

    if request.method == "POST":
        slug = request.POST.get("slug")
        node = get_object_or_404(ContentNode, slug=slug)
        Erratum.objects.create(node=node, body=(request.POST.get("body") or "")[:200])
        rid = request.POST.get("report_id")
        if rid:
            ErrorReport.objects.filter(pk=rid).update(status="done")
        return redirect("/studio/errata")
    return render(
        request,
        "studio/errata.html",
        {"errata": Erratum.objects.select_related("node")[:40], "reports": ErrorReport.objects.filter(status="open")},
    )


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_assets(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        Asset.objects.update_or_create(
            slug=slugify(request.POST.get("slug") or request.POST.get("title") or "")[:80],
            defaults={
                "title": (request.POST.get("title") or "")[:80],
                "access": request.POST.get("access") or "free",
                "path": request.POST.get("path") or "",
                "note": (request.POST.get("note") or "")[:200],
            },
        )
        return redirect("/studio/assets")
    return render(request, "studio/assets.html", {"assets": Asset.objects.all()})


@staff_required("edit")
@require_http_methods(["GET", "POST"])
def studio_prompts(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        PromptVersion.objects.update_or_create(
            name=(request.POST.get("name") or "writer")[:40],
            version=(request.POST.get("version") or "1")[:20],
            defaults={"body": request.POST.get("body") or ""},
        )
        return redirect("/studio/prompts")
    return render(request, "studio/prompts.html", {"prompts": PromptVersion.objects.all()})


@staff_required("edit")
def studio_costs(request: HttpRequest) -> HttpResponse:
    jobs = GenerationJob.objects.all()[:50]
    total = sum(j.cost_cents for j in jobs)
    tokens = sum(j.tokens_in + j.tokens_out for j in jobs)
    return render(request, "studio/costs.html", {"jobs": jobs, "total": total, "tokens": tokens})
