from __future__ import annotations

from datetime import date
from urllib.parse import urlparse

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from access.services import can_read_full, visible
from accounts.models import User
from content.models import ContentNode, Erratum, Feedback, GlossaryTerm, StaticPage
from content.services import published, slot_cards
from graph.models import LearningPath, PathItem
from learning.models import Bookmark, ErrorReport, Highlight, Progress
from learning.views import _cookie_slugs


def home(request: HttpRequest) -> HttpResponse:
    concepts = published().filter(kind="concept")[:6]
    paths = LearningPath.objects.filter(status="published")[:6]
    news = published().filter(kind="news")[:5]
    continue_node = None
    if request.user.is_authenticated:
        last = Progress.objects.filter(user=request.user).select_related("node").order_by("-updated_at").first()
        continue_node = last.node if last else None
    from entities.models import Entity

    tools = Entity.objects.filter(kind="tool")[:4]
    door_slugs = ["what-is-llm", "prompt-basics", "need-a-kb", "when-not-agent", "cost-estimate", "task-brief"]
    by_slug = {n.slug: n for n in published().filter(slug__in=door_slugs)}
    doors = [by_slug[s] for s in door_slugs if s in by_slug]
    return render(
        request,
        "site/home.html",
        {
            "concepts": concepts,
            "paths": paths,
            "news_items": news,
            "continue_node": continue_node,
            "tools": tools,
            "doors": doors,
            "r1": slot_cards("R1"),
        },
    )


def article(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, slug=slug, deleted_at__isnull=True)
    if not visible(request.user, node):
        raise Http404()
    full = can_read_full(request.user, node)
    html = node.html
    locked = False
    if not full:
        html, _rest = node.preview_and_rest()
        locked = True
    stale = False
    archived = node.status == "archived"
    if node.review_by and date.today() > node.review_by and request.flags.get("outdated.banner"):
        stale = True
    prereq = published().filter(slug__in=node.prereqs)
    nxt = published().filter(slug__in=node.next_nodes)
    bookmarked = False
    read = False
    if request.user.is_authenticated:
        bookmarked = Bookmark.objects.filter(user=request.user, node=node).exists()
        read = Progress.objects.filter(user=request.user, node=node, read=True).exists()
    if not read:
        read = node.slug in _cookie_slugs(request)
    return render(
        request,
        "site/article.html",
        {
            "node": node,
            "html": html,
            "locked": locked,
            "stale": stale,
            "archived": archived,
            "prereqs": prereq,
            "next_nodes": nxt,
            "errata": node.errata.all(),
            "r2": slot_cards("R2", node=node),
            "bookmarked": bookmarked,
            "read": read,
        },
    )


POST_KINDS = ("concept", "unit", "news", "pitfall", "compare", "case", "project")
START_SLUGS = ("what-is-llm", "when-to-use-ai", "prompt-basics", "need-a-kb")
DOOR_SPEC = [
    ("what-is-llm", "听不懂别人在说 Token、幻觉", "先用三分钟搞清模型在干什么。"),
    ("prompt-basics", "要把一次提问写清楚", "任务、约束、格式，比堆形容词有用。"),
    ("need-a-kb", "被要求做内部知识库", "先判断要不要做，再谈模型和产品。"),
    ("when-not-agent", "有人要上 Agent", "多数需求停在检索问答或工作流。"),
]


def learn(request: HttpRequest) -> HttpResponse:
    kind = request.GET.get("kind") or "all"
    tag = (request.GET.get("tag") or "").strip()
    filtered = kind in POST_KINDS or bool(tag)
    paths = list(LearningPath.objects.filter(status="published"))
    shorts = [p for p in paths if p.slug != "doc-qa"]
    project = next((p for p in paths if p.slug == "doc-qa"), None)
    qs = published().filter(kind__in=POST_KINDS)
    if kind in POST_KINDS:
        qs = qs.filter(kind=kind)
    posts = list(qs.order_by("-published_at", "-id")[:48])
    if tag:
        posts = [p for p in posts if tag in (p.tags or []) or p.track == tag]
    done_slugs: set[str] = set()
    read_slugs = set(_cookie_slugs(request))
    if request.user.is_authenticated:
        done_slugs = set(
            Progress.objects.filter(user=request.user, read=True).values_list("node__slug", flat=True)
        )
        read_slugs |= done_slugs
    seen = done_slugs | read_slugs
    for p in posts:
        if p.slug in done_slugs:
            p.map_state = "done"
        elif p.slug in read_slugs:
            p.map_state = "read"
        else:
            p.map_state = ""
    by_slug = {p.slug: p for p in published().filter(slug__in=[*START_SLUGS, *[d[0] for d in DOOR_SPEC]])}
    start = None
    for slug in START_SLUGS:
        node = by_slug.get(slug)
        if node and slug not in seen:
            start = node
            break
    if start is None:
        start = by_slug.get("what-is-llm") or (posts[0] if posts else None)
    doors = []
    for slug, question, blurb in DOOR_SPEC:
        node = by_slug.get(slug)
        if node:
            doors.append({"question": question, "blurb": blurb, "node": node})
    if filtered:
        rest = posts
    else:
        rest = [p for p in posts if not start or p.slug != start.slug][:8]
    kind_links = [
        ("all", "全部"),
        ("concept", "概念"),
        ("unit", "教程"),
        ("news", "快讯"),
        ("pitfall", "坑"),
        ("compare", "对照"),
    ]
    tags: dict[str, int] = {}
    for p in published().filter(kind__in=POST_KINDS).only("tags", "track"):
        if p.track:
            tags[p.track] = tags.get(p.track, 0) + 1
        for t in p.tags or []:
            tags[str(t)] = tags.get(str(t), 0) + 1
    tag_links = sorted(tags.items(), key=lambda kv: (-kv[1], kv[0]))[:12]

    def href(next_kind: str, next_tag: str) -> str:
        q = []
        if next_kind and next_kind != "all":
            q.append(f"kind={next_kind}")
        if next_tag:
            q.append(f"tag={next_tag}")
        return "/learn?" + "&".join(q) if q else "/learn"

    return render(
        request,
        "site/learn.html",
        {
            "shorts": shorts,
            "project": project,
            "posts": rest,
            "start": start,
            "doors": doors,
            "filtered": filtered,
            "kind": kind,
            "tag": tag,
            "kind_links": [(k, lab, href(k, tag), k == kind) for k, lab in kind_links],
            "tag_links": [(t, n, href(kind, t), t == tag) for t, n in tag_links],
        },
    )


def track(request: HttpRequest, slug: str) -> HttpResponse:
    path = get_object_or_404(LearningPath, slug=slug)
    items = list(path.items.select_related("node"))
    published_units = sum(1 for i in items if i.node and i.node.status == "published")
    building = published_units < 3
    entries = []
    if len(items) > 4:
        wanted = {1, 5, 9}
        entries = [i for i in items if i.unit_index in wanted and i.node]
    return render(
        request,
        "site/track.html",
        {
            "path": path,
            "items": items,
            "building": building,
            "published_units": published_units,
            "short": len(items) <= 4,
            "entries": entries,
        },
    )


def unit(request: HttpRequest, track: str, unit: str) -> HttpResponse:
    path = get_object_or_404(LearningPath, slug=track)
    item = PathItem.objects.filter(path=path, node__slug=unit).select_related("node").first()
    if item and item.node:
        return article(request, item.node.slug)
    return article(request, unit)


def glossary(request: HttpRequest) -> HttpResponse:
    terms = GlossaryTerm.objects.all().order_by("term")
    groups: dict[str, list] = {}
    for t in terms:
        key = (t.term[:1] or "#").upper()
        groups.setdefault(key, []).append(t)
    return render(request, "site/glossary.html", {"terms": terms, "groups": groups})


def glossary_term(request: HttpRequest, term: str) -> HttpResponse:
    item = get_object_or_404(GlossaryTerm, term=term)
    if request.GET.get("partial"):
        return render(request, "site/_glossary_card.html", {"item": item})
    related = published().filter(kind="concept")[:6]
    return render(request, "site/glossary_term.html", {"item": item, "related": related})


def compare(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(published(), slug=slug, kind="compare")
    return article(request, node.slug)


def compare_list(request: HttpRequest) -> HttpResponse:
    nodes = published().filter(kind="compare")
    return render(request, "site/list.html", {"title": "对照", "nodes": nodes, "lead": "两方案怎么选，结论段由人写。"})


def projects(request: HttpRequest) -> HttpResponse:
    nodes = published().filter(kind="project")
    return render(request, "site/list.html", {"title": "项目课", "nodes": nodes, "lead": "成功标准写在正文里。"})


def topic(request: HttpRequest, slug: str) -> HttpResponse:
    nodes = [
        n
        for n in published()
        if n.track == slug or slug in (n.tags or []) or slug in (n.node_ids or [])
    ]
    path = LearningPath.objects.filter(slug=slug).first()
    title = path.title if path else slug
    return render(request, "site/topic.html", {"slug": slug, "title": title, "nodes": nodes})


def topics_index(request: HttpRequest) -> HttpResponse:
    tags: dict[str, int] = {}
    for node in published().only("tags", "track"):
        if node.track:
            tags[node.track] = tags.get(node.track, 0) + 1
        for t in node.tags or []:
            tags[str(t)] = tags.get(str(t), 0) + 1
    labels = {p.slug: p.title for p in LearningPath.objects.filter(status="published")}
    items = [{"slug": slug, "count": n, "title": labels.get(slug, slug)} for slug, n in sorted(tags.items())]
    return render(request, "site/topics.html", {"items": items})


def tools(request: HttpRequest) -> HttpResponse:
    from entities.models import Entity

    items = Entity.objects.filter(kind="tool")
    return render(request, "site/tools.html", {"items": items})


@require_POST
def claim_tool(request: HttpRequest, slug: str) -> HttpResponse:
    from entities.models import Claim, Entity

    item = get_object_or_404(Entity, slug=slug, kind="tool")
    email = (request.POST.get("email") or "").strip().lower()
    host = (urlparse(item.official_url).hostname or "").lower()
    domain = email.split("@")[-1] if "@" in email else ""
    if not email or (domain not in host and host != domain):
        return render(request, "site/entity.html", {"item": item, "error": "邮箱域名须与官网同域。"})
    pending = Claim.objects.filter(entity=item, status="pending", created_at__gte=date.today().replace(day=1))
    if pending.exists():
        return render(request, "site/entity.html", {"item": item, "error": "该条目已有待处理认领。"})
    Claim.objects.create(entity=item, email=email, contact=(request.POST.get("contact") or "")[:80], fields={"note": request.POST.get("note") or ""})
    return render(request, "site/entity.html", {"item": item, "notice": "认领已提交，等待 AdOps 核对。"})


def entity_page(request: HttpRequest, slug: str) -> HttpResponse:
    from entities.models import Entity

    item = get_object_or_404(Entity, slug=slug)
    related = [n for n in published() if item.slug in (n.tags or []) or item.name in n.title][:8]
    return render(request, "site/entity.html", {"item": item, "related": related})


def entity_list(request: HttpRequest, kind: str) -> HttpResponse:
    from entities.models import Entity

    items = Entity.objects.filter(kind=kind)
    titles = {"model": "模型", "company": "公司", "paper": "论文"}
    return render(request, "site/entities.html", {"title": titles.get(kind, kind), "items": items, "kind": kind})


def author(request: HttpRequest, pk: int) -> HttpResponse:
    person = get_object_or_404(User, pk=pk)
    if not person.staff_role and not person.is_superuser:
        raise Http404()
    name = person.display_name or ""
    nodes = [n for n in published() if (n.ai or {}).get("reviewed_by") == name][:20]
    return render(request, "site/author.html", {"person": person, "nodes": nodes})


def authors(request: HttpRequest) -> HttpResponse:
    people = User.objects.filter(is_staff=True).exclude(staff_role="author")
    return render(request, "site/authors.html", {"people": people})


def static_page(request: HttpRequest, slug: str) -> HttpResponse:
    page = StaticPage.objects.filter(slug=slug).first()
    return render(request, "site/static.html", {"page": page, "slug": slug})


def errata_list(request: HttpRequest) -> HttpResponse:
    items = Erratum.objects.select_related("node").order_by("-published_at")[:50]
    return render(request, "site/errata.html", {"items": items})


@require_POST
def feedback(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(published(), slug=slug)
    kind = request.POST.get("kind") or ""
    mapping = {"useful": "useful", "helpful": "useful", "unclear": "unclear", "confusing": "unclear", "errata": "errata", "outdated": "outdated"}
    kind = mapping.get(kind, "")
    if not kind:
        raise Http404()
    Feedback.objects.create(
        node=node,
        kind=kind,
        note=(request.POST.get("note") or "")[:200],
        user_id=request.user.id if request.user.is_authenticated else None,
    )
    if kind == "outdated":
        from search.models import TopicGap

        TopicGap.objects.get_or_create(signal="feedback_outdated", title=node.title, defaults={"score": 2})
    return redirect("article", slug=slug)


@login_required
@require_POST
def bookmark(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(published(), slug=slug)
    obj = Bookmark.objects.filter(user=request.user, node=node).first()
    if obj:
        obj.delete()
    else:
        Bookmark.objects.create(user=request.user, node=node)
    return redirect("article", slug=slug)


@login_required
@require_POST
def highlight(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(published(), slug=slug)
    quote = (request.POST.get("quote") or "")[:400]
    if quote:
        Highlight.objects.create(user=request.user, node=node, quote=quote)
    return redirect("article", slug=slug)


@require_POST
def report_error(request: HttpRequest, slug: str) -> HttpResponse:
    node = get_object_or_404(published(), slug=slug)
    ErrorReport.objects.create(
        node=node,
        body=(request.POST.get("body") or "")[:500],
        email=(request.POST.get("email") or "")[:80],
        user=request.user if request.user.is_authenticated else None,
    )
    return redirect("article", slug=slug)


def pricing(request: HttpRequest) -> HttpResponse:
    from core.models import SiteSetting

    return render(request, "site/pricing.html", {"setting": SiteSetting.load()})


def join(request: HttpRequest) -> HttpResponse:
    return render(request, "site/join.html")


def page_not_found(request, exception=None) -> HttpResponse:
    return render(request, "404.html", status=404)
