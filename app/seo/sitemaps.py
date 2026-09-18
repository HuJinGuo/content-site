from io import BytesIO

from django.contrib.sitemaps import Sitemap
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.views.decorators.http import require_http_methods

from content.models import ContentNode, StaticPage
from mail.models import Subscriber
from news.models import Issue


def robots(request: HttpRequest) -> HttpResponse:
    body = (
        "User-agent: *\nAllow: /\nDisallow: /studio\nDisallow: /admin\nDisallow: /app\n"
        "Disallow: /ads\nDisallow: /api\nDisallow: /redeem\nDisallow: /go\nDisallow: /django-admin\n"
        "Sitemap: /sitemap.xml\n\n"
        "User-agent: GPTBot\nDisallow: /\nUser-agent: ClaudeBot\nDisallow: /\n"
        "User-agent: CCBot\nDisallow: /\nUser-agent: Google-Extended\nDisallow: /\n"
    )
    return HttpResponse(body, content_type="text/plain")


def llms(request: HttpRequest) -> HttpResponse:
    body = (
        "# ai.nornless.com\n"
        "> AI 知识阶梯 + 科技情报站。允许索引摘要与问答引用，禁止将全文用于训练。\n"
        "署名与链回见 /license\n"
        "- [学习地图](/learn)\n- [快讯](/news)\n- [百科](/glossary)\n"
    )
    return HttpResponse(body, content_type="text/plain")


def rss(request: HttpRequest, section: str = "all") -> HttpResponse:
    qs = ContentNode.objects.filter(status="published")
    if section == "news":
        qs = qs.filter(kind="news")
    elif section == "learn":
        qs = qs.filter(kind__in=["concept", "unit"])
    elif section in {"daily", "weekly"}:
        issues = Issue.objects.filter(kind=section, status="published")[:20]
        return render(request, "seo/rss.xml", {"items": issues, "kind": section}, content_type="application/rss+xml")
    items = qs[:50]
    return render(request, "seo/rss.xml", {"items": items, "kind": section}, content_type="application/rss+xml")


def og_png(request: HttpRequest, public_id: str) -> HttpResponse:
    node = get_object_or_404(ContentNode, public_id=public_id, status="published")
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (1200, 630), "#14131c")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1200, 8), fill="#c4a35a")
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Songti.ttc", 48)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Songti.ttc", 28)
    except OSError:
        font = ImageFont.load_default()
        small = font
    draw.text((64, 180), node.title[:28], fill="#f3efe4", font=font)
    draw.text((64, 480), f"{node.level} · ai.nornless.com", fill="#c4a35a", font=small)
    buf = BytesIO()
    img.save(buf, format="PNG")
    resp = HttpResponse(buf.getvalue(), content_type="image/png")
    resp["Cache-Control"] = "public, max-age=86400"
    return resp


@require_http_methods(["GET", "POST"])
def subscribe(request: HttpRequest) -> HttpResponse:
    import hashlib
    import secrets

    from django.core.mail import send_mail

    notice = ""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        if email:
            token = secrets.token_urlsafe(16)
            digest = hashlib.sha256(email.encode()).hexdigest()
            sub, _ = Subscriber.objects.update_or_create(
                email_hash=digest,
                defaults={
                    "email": email,
                    "status": "pending",
                    "confirm_token": token,
                    "prefs": {"weekly": True, "daily": False},
                },
            )
            send_mail("确认订阅", f"打开 /subscribe/confirm/{token}", None, [email])
            notice = "请查收确认信（本机控制台邮件后端会打印）。"
    return render(request, "site/subscribe.html", {"notice": notice})


def subscribe_confirm(request: HttpRequest, token: str) -> HttpResponse:
    sub = Subscriber.objects.filter(confirm_token=token, status="pending").first()
    if sub:
        sub.status = "active"
        sub.manage_token = token
        sub.save()
        return render(request, "site/subscribe.html", {"notice": "订阅已确认。周报默认开启。"})
    return render(request, "site/subscribe.html", {"notice": "确认链接无效。"})


def unsubscribe(request: HttpRequest, token: str) -> HttpResponse:
    sub = Subscriber.objects.filter(manage_token=token).first() or Subscriber.objects.filter(confirm_token=token).first()
    if sub:
        sub.status = "unsubscribed"
        sub.save()
    return render(request, "site/subscribe.html", {"notice": "已退订。"})


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ContentNode.objects.filter(status="published").order_by("-published_at", "id")

    def location(self, obj):
        return f"/articles/{obj.slug}"


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.3

    def items(self):
        return StaticPage.objects.order_by("slug")

    def location(self, obj):
        return f"/{obj.slug}"


class IssueSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Issue.objects.filter(status="published").order_by("-published_at", "id")

    def location(self, obj):
        if obj.kind == "daily":
            return f"/digest/daily/{obj.slug.removeprefix('daily-')}"
        if obj.kind == "weekly":
            return f"/digest/weekly/{obj.slug}"
        if obj.kind == "deep":
            return f"/digest/deep/{obj.slug}"
        if obj.kind == "outdated":
            return f"/digest/outdated/{obj.slug.removeprefix('outdated-')}"
        return f"/digest/{obj.kind}"


sitemaps = {"articles": ArticleSitemap, "pages": PageSitemap, "issues": IssueSitemap}

urlpatterns = [
    path("robots.txt", robots),
    path("llms.txt", llms),
    path("rss.xml", rss),
    path("rss/<slug:section>.xml", rss),
    path("og/<str:public_id>.png", og_png),
    path("subscribe", subscribe, name="subscribe"),
    path("subscribe/confirm/<str:token>", subscribe_confirm, name="subscribe_confirm"),
    path("unsubscribe/<str:token>", unsubscribe, name="unsubscribe"),
]
