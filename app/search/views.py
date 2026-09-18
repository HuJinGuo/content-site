from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from content.models import ContentNode
from search.models import SearchLog, TopicGap


def search_view(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get("q") or "").strip()[:100]
    kind = request.GET.get("kind") or "all"
    results = []
    if len(q) >= 2:
        qs = ContentNode.objects.filter(status="published").filter(Q(title__icontains=q) | Q(summary__icontains=q))
        if kind in {"concept", "unit", "news"}:
            qs = qs.filter(kind=kind)
        results = list(qs[:20])
        SearchLog.objects.create(q=q, zero=not results, hits=len(results))
        if not results:
            TopicGap.objects.get_or_create(signal="search_zero", title=q, defaults={"score": 3})
    return render(request, "site/search.html", {"q": q, "results": results, "kind": kind, "zero": len(q) >= 2 and not results})
