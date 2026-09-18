from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from zones.models import Deal, EventItem, JobPost, Launch, SponsoredPost


@require_http_methods(["GET", "POST"])
def jobs(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/login?next=/jobs")
        title = (request.POST.get("title") or "")[:80]
        org = (request.POST.get("org") or "")[:80]
        url = request.POST.get("url") or ""
        if not title or not org or not url.startswith("https://"):
            error = "标题、公司、https 链接必填。"
        else:
            JobPost.objects.create(title=title, org=org, url=url, status="submitted")
            return redirect("/jobs")
    return render(request, "site/jobs.html", {"items": JobPost.objects.filter(status="published"), "error": error})


def launches(request: HttpRequest) -> HttpResponse:
    return render(request, "site/zone.html", {"title": "发布墙", "items": Launch.objects.filter(status="published")})


def events(request: HttpRequest) -> HttpResponse:
    return render(request, "site/zone.html", {"title": "活动", "items": EventItem.objects.filter(status="published")})


def deals(request: HttpRequest) -> HttpResponse:
    return render(request, "site/zone.html", {"title": "优惠", "items": Deal.objects.filter(status="published")})


def sponsored(request: HttpRequest) -> HttpResponse:
    return render(
        request, "site/zone.html", {"title": "赞助内容", "items": SponsoredPost.objects.filter(status="published")}
    )


def sponsored_item(request: HttpRequest, pk: int) -> HttpResponse:
    item = get_object_or_404(SponsoredPost, pk=pk, status="published")
    return render(request, "site/sponsored.html", {"item": item})


def advertise(request: HttpRequest) -> HttpResponse:
    return render(request, "site/advertise.html")
