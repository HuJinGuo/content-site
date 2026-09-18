from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from content.models import ContentNode
from graph.models import LearningPath
from learning.models import Assessment, Bookmark, DigestAction, Highlight, Progress


def _pub():
    return ContentNode.objects.filter(status="published")


@require_http_methods(["GET", "POST"])
def assess(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        goal = request.POST.get("goal") or ""
        time = request.POST.get("time") or ""
        role = request.POST.get("role") or ""
        answers = {"goal": goal, "time": time, "role": role, "tools": request.POST.getlist("tools")}
        level = "L0"
        start_slug = "what-is-llm"
        short_slug = "ask-better"
        if goal in {"ship"}:
            level = "L3"
            start_slug = "need-a-kb"
            short_slug = "doc-qa"
        elif goal in {"agent"}:
            level = "L4"
            start_slug = "when-not-agent"
            short_slug = "hold-agent"
        elif goal in {"choose"}:
            level = "L2"
            start_slug = "cost-estimate"
            short_slug = "doc-qa"
        elif goal in {"understand"}:
            level = "L1"
            start_slug = "what-is-llm"
            short_slug = "ask-better"
        Assessment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            answers=answers,
            suggested_level=level,
            suggested_path=short_slug,
        )
        start = _pub().filter(slug=start_slug).first()
        return render(
            request,
            "site/assess_result.html",
            {
                "level": level,
                "start": start,
                "short": LearningPath.objects.filter(slug=short_slug).first(),
                "path": LearningPath.objects.filter(slug="doc-qa").first(),
                "skip": ["先不要追评测榜", "先不要微调", "先不要自建训练集群", "先不要把学习当成必须按 1 到 10 读完"],
            },
        )
    return render(request, "site/assess.html")


@login_required
def app_home(request: HttpRequest) -> HttpResponse:
    progress = Progress.objects.filter(user=request.user).select_related("node").order_by("-updated_at")[:12]
    next_unit = _pub().filter(kind="unit").first()
    concept = _pub().filter(kind="concept").first()
    news = _pub().filter(kind="news").first()
    tasks = [x for x in (next_unit, concept, news) if x]
    stale = _pub().filter(review_by__isnull=False)[:5]
    return render(request, "app/home.html", {"progress": progress, "tasks": tasks, "stale": stale})


@login_required
def library(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "app/library.html",
        {
            "bookmarks": Bookmark.objects.filter(user=request.user).select_related("node"),
            "highlights": Highlight.objects.filter(user=request.user).select_related("node"),
        },
    )


@login_required
def downloads(request: HttpRequest) -> HttpResponse:
    from content.models import Asset

    return render(request, "app/downloads.html", {"assets": Asset.objects.all()[:20]})


@login_required
@require_http_methods(["GET", "POST"])
def briefing(request: HttpRequest) -> HttpResponse:
    from news.models import Issue

    issues = Issue.objects.filter(status="published").order_by("-published_at")[:20]
    if request.method == "POST":
        DigestAction.objects.update_or_create(
            user=request.user,
            issue_slug=request.POST.get("issue_slug") or "",
            item_key=request.POST.get("item_key") or "action",
            defaults={"done": True},
        )
        return redirect("/app/briefing")
    return render(request, "app/briefing.html", {"issues": issues})


READ_COOKIE = "nornless_read"


def _cookie_slugs(request: HttpRequest) -> list[str]:
    raw = request.COOKIES.get(READ_COOKIE) or ""
    return [s for s in raw.split("|") if s]


@require_POST
def mark_read(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, slug=slug, status="published")
    undo = bool(request.POST.get("undo"))
    if request.user.is_authenticated:
        obj, _ = Progress.objects.get_or_create(user=request.user, node=node)
        obj.read = not undo
        obj.save()
    slugs = _cookie_slugs(request)
    if undo:
        slugs = [s for s in slugs if s != slug]
    elif slug not in slugs:
        slugs.append(slug)
    nxt = ""
    if not undo:
        nxt = node.next_nodes[0] if node.next_nodes else ""
    resp = redirect("article", slug=nxt or slug)
    resp.set_cookie(READ_COOKIE, "|".join(slugs[:80]), max_age=86400 * 400, samesite="Lax")
    return resp


@login_required
@require_http_methods(["GET", "POST"])
def ask(request: HttpRequest) -> HttpResponse:
    from ask.models import AskThread
    from search.models import TopicGap

    error = ""
    answer = ""
    citations: list = []
    if request.method == "POST":
        q = (request.POST.get("q") or "").strip()[:500]
        if not q:
            error = "请输入问题。"
        else:
            from access.services import entitlements

            ent = entitlements(request.user)
            today = timezone.localdate()
            used = AskThread.objects.filter(user=request.user, created_at__date=today).count()
            if used >= max(ent.ask_quota, 0):
                error = "今日问答额度用尽。"
            else:
                hits = list(ContentNode.objects.filter(status="published", title__icontains=q[:40])[:3])
                if not hits:
                    TopicGap.objects.get_or_create(signal="ask_zero", title=q[:80], defaults={"score": 4})
                    answer = "本站还没写过，已记入选题缺口。"
                else:
                    citations = [{"title": n.title, "slug": n.slug, "summary": n.summary} for n in hits]
                    answer = "根据已审条目：" + "；".join(n.title for n in hits)
                AskThread.objects.create(user=request.user, question=q, answer=answer, citations=citations)
    threads = AskThread.objects.filter(user=request.user)[:20]
    return render(request, "app/ask.html", {"error": error, "answer": answer, "citations": citations, "threads": threads})
