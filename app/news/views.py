from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from content.models import ContentNode
from news.models import Issue


def news_list(request: HttpRequest) -> HttpResponse:
    items = ContentNode.objects.filter(kind="news", status="published")[:50]
    return render(request, "site/news.html", {"items": items, "r4": {"href": "/subscribe", "label": "订阅周报", "lead": "快讯每 10 条一处推荐位。"}})


def news_item(request: HttpRequest, slug: str) -> HttpResponse:
    from content.views import article

    return article(request, slug)


def digest(request: HttpRequest, kind: str) -> HttpResponse:
    issue = Issue.objects.filter(kind=kind, status="published").order_by("-published_at").first()
    return render(request, "site/digest.html", {"issue": issue, "kind": kind})


def digest_daily(request: HttpRequest, day: str) -> HttpResponse:
    issue = Issue.objects.filter(kind="daily", slug=f"daily-{day}").first()
    if issue is None:
        parsed = parse_date(day)
        if parsed:
            issue = Issue.objects.filter(kind="daily", published_at__date=parsed).first()
    return render(request, "site/digest.html", {"issue": issue, "kind": "daily", "day": day})


def digest_weekly(request: HttpRequest, slug: str) -> HttpResponse:
    issue = get_object_or_404(Issue, kind="weekly", slug=slug)
    return render(request, "site/digest.html", {"issue": issue, "kind": "weekly"})


def digest_deep(request: HttpRequest, slug: str) -> HttpResponse:
    issue = get_object_or_404(Issue, kind="deep", slug=slug)
    return render(request, "site/digest.html", {"issue": issue, "kind": "deep"})


def digest_outdated(request: HttpRequest, month: str) -> HttpResponse:
    issue = Issue.objects.filter(kind="outdated", slug=f"outdated-{month}").first()
    if issue is None:
        issue = Issue.objects.filter(kind="outdated").order_by("-published_at").first()
    return render(request, "site/digest.html", {"issue": issue, "kind": "outdated", "month": month})


def timeline(request: HttpRequest) -> HttpResponse:
    news = list(ContentNode.objects.filter(kind="news", status="published")[:40])
    items = [n for n in news if "milestone" in (n.tags or [])] or news
    return render(request, "site/timeline.html", {"items": items})
