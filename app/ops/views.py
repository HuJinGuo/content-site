from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from access.services import grant_membership
from accounts.models import User
from ads.models import AdCampaign, AdCreative, HouseAd
from codes.models import RedeemError, issue_codes, void_plain
from content.models import ContentNode
from core.flags import FLAG_DEFAULTS
from core.models import AuditLog, SiteSetting
from core.services import set_flag, snapshot
from mail.models import MailTemplate, Subscriber, Suppression
from seo.models import RedirectRule
from studio.auth import staff_required
from telemetry.models import MetricsDaily, ServerEvent
from zones.models import Deal, EventItem, JobPost, Launch, SponsoredPost


@staff_required("flags")
def ops_home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "admin/home.html",
        {
            "flags": snapshot(),
            "users": User.objects.count(),
            "published": ContentNode.objects.filter(status="published").count(),
            "drafts": ContentNode.objects.exclude(status__in=["published", "archived"]).count(),
        },
    )


@staff_required("flags")
@require_http_methods(["GET", "POST"])
def ops_flags(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        key = request.POST.get("key") or ""
        value = request.POST.get("value") == "on"
        reason = request.POST.get("reason") or ""
        try:
            set_flag(key, value, actor=request.user, reason=reason)
        except ValueError as exc:
            error = str(exc)
    rows = []
    flags = snapshot()
    for key, default in FLAG_DEFAULTS.items():
        if isinstance(default, bool):
            rows.append((key, bool(flags.get(key)), default))
    return render(request, "admin/flags.html", {"rows": rows, "error": error})


@staff_required("codes")
@require_http_methods(["GET", "POST"])
def ops_codes(request: HttpRequest) -> HttpResponse:
    plains: list[str] = []
    error = ""
    if request.method == "POST":
        action = request.POST.get("action") or "issue"
        reason = request.POST.get("reason") or ""
        if action == "void":
            try:
                void_plain(plain=request.POST.get("code") or "", actor=request.user, reason=reason)
            except (ValueError, RedeemError) as exc:
                error = str(exc)
        else:
            kind = request.POST.get("kind") or "member"
            try:
                count = int(request.POST.get("count") or "1")
                days = int(request.POST.get("days") or "31")
            except ValueError:
                count, days = 1, 31
            node_slug = request.POST.get("node_slug") or ""
            try:
                _batch, plains = issue_codes(
                    kind=kind, count=min(count, 50), days=days, actor=request.user, reason=reason, node_slug=node_slug
                )
            except ValueError as exc:
                error = str(exc)
    from codes.models import Code

    recent = Code.objects.select_related("batch").order_by("-id")[:40]
    return render(request, "admin/codes.html", {"plains": plains, "error": error, "recent": recent})


@staff_required("users")
@require_http_methods(["GET", "POST"])
def ops_users(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        user = get_object_or_404(User, pk=request.POST.get("id"))
        action = request.POST.get("action") or "grant"
        reason = request.POST.get("reason") or action
        if action == "ban":
            user.is_active = False
            user.save(update_fields=["is_active"])
            AuditLog.objects.create(
                actor_id=request.user.id,
                action="user.ban",
                obj_type="user",
                obj_id=str(user.id),
                reason=reason,
            )
        elif action == "unban":
            user.is_active = True
            user.save(update_fields=["is_active"])
        else:
            days = int(request.POST.get("days") or "31")
            grant_membership(user, days=days, source="admin", actor=request.user)
        return redirect("/admin/users")
    return render(request, "admin/users.html", {"users": User.objects.all()[:100], "error": error})


@staff_required("audit")
def ops_audit(request: HttpRequest) -> HttpResponse:
    return render(request, "admin/audit.html", {"logs": AuditLog.objects.all()[:200]})


@staff_required("flags")
@require_http_methods(["GET", "POST"])
def ops_paywall(request: HttpRequest) -> HttpResponse:
    nodes = ContentNode.objects.filter(access__in=["supporter", "code", "group"])[:50]
    if request.method == "POST":
        node = get_object_or_404(ContentNode, slug=request.POST.get("slug"))
        node.access = request.POST.get("access") or node.access
        node.save(update_fields=["access", "updated_at"])
        return redirect("/admin/paywall")
    return render(request, "admin/paywall.html", {"nodes": nodes})


@staff_required("users")
@require_http_methods(["GET", "POST"])
def ops_groups(request: HttpRequest) -> HttpResponse:
    from accounts.models import Group

    if request.method == "POST":
        slug = (request.POST.get("slug") or "").strip()
        name = (request.POST.get("name") or slug)[:80]
        if slug:
            Group.objects.update_or_create(slug=slug, defaults={"name": name})
        return redirect("/admin/groups")
    return render(request, "admin/groups.html", {"groups": Group.objects.all()})


@staff_required("ads")
@require_http_methods(["GET", "POST"])
def ops_ads(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "house":
            HouseAd.objects.create(
                slot=request.POST.get("slot") or "R1",
                title=(request.POST.get("title") or "")[:80],
                body=(request.POST.get("body") or "")[:200],
                url=request.POST.get("url") or "/",
            )
        elif action == "review":
            c = get_object_or_404(AdCreative, pk=request.POST.get("id"))
            c.status = request.POST.get("status") or "approved"
            c.save()
        return redirect("/admin/ads")
    return render(
        request,
        "admin/ads.html",
        {
            "campaigns": AdCampaign.objects.all()[:40],
            "creatives": AdCreative.objects.all()[:40],
            "house": HouseAd.objects.all(),
        },
    )


@staff_required("ads")
@require_http_methods(["GET", "POST"])
def ops_zones(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        kind = request.POST.get("kind")
        pk = request.POST.get("id")
        status = request.POST.get("status") or "published"
        model = {
            "job": JobPost,
            "launch": Launch,
            "event": EventItem,
            "deal": Deal,
            "sponsored": SponsoredPost,
        }.get(kind)
        if model:
            model.objects.filter(pk=pk).update(status=status)
        return redirect("/admin/zones")
    return render(
        request,
        "admin/zones.html",
        {
            "jobs": JobPost.objects.all()[:30],
            "launches": Launch.objects.all()[:30],
            "events": EventItem.objects.all()[:30],
            "deals": Deal.objects.all()[:30],
            "sponsored": SponsoredPost.objects.all()[:30],
        },
    )


@staff_required("users")
@require_http_methods(["GET", "POST"])
def ops_mail(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        MailTemplate.objects.update_or_create(
            key=(request.POST.get("key") or "notice")[:40],
            defaults={
                "subject": (request.POST.get("subject") or "")[:80],
                "body_md": request.POST.get("body_md") or "",
            },
        )
        return redirect("/admin/mail")
    return render(
        request,
        "admin/mail.html",
        {
            "subscribers": Subscriber.objects.all()[:50],
            "suppressions": Suppression.objects.all()[:20],
            "templates": MailTemplate.objects.all(),
        },
    )


@staff_required("flags")
def ops_metrics(request: HttpRequest) -> HttpResponse:
    from datetime import date

    numbers = {
        "published": ContentNode.objects.filter(status="published").count(),
        "users": User.objects.count(),
        "events": ServerEvent.objects.count(),
    }
    MetricsDaily.objects.update_or_create(day=date.today(), defaults={"numbers": numbers})
    return render(
        request,
        "admin/metrics.html",
        {
            "events": ServerEvent.objects.all()[:30],
            "daily": MetricsDaily.objects.all()[:14],
            "published": numbers["published"],
            "numbers": numbers,
        },
    )


@staff_required("flags")
@require_http_methods(["GET", "POST"])
def ops_seo(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        RedirectRule.objects.update_or_create(
            src=request.POST.get("src") or "/",
            defaults={"dst": request.POST.get("dst") or "/", "code": int(request.POST.get("code") or 301)},
        )
        return redirect("/admin/seo")
    return render(request, "admin/seo.html", {"rules": RedirectRule.objects.all()[:50]})


@staff_required("flags")
def ops_system(request: HttpRequest) -> HttpResponse:
    return render(request, "admin/system.html", {"setting": SiteSetting.load()})


@staff_required("flags")
@require_http_methods(["GET", "POST"])
def ops_settings(request: HttpRequest) -> HttpResponse:
    setting = SiteSetting.load()
    if request.method == "POST":
        setting.notice = (request.POST.get("notice") or "")[:80]
        setting.maintenance = request.POST.get("maintenance") == "on"
        setting.card_shop_url = request.POST.get("card_shop_url") or ""
        setting.supporter_price = (request.POST.get("supporter_price") or setting.supporter_price)[:40]
        setting.from_email = request.POST.get("from_email") or ""
        setting.save()
        return redirect("/admin/settings")
    return render(request, "admin/settings.html", {"setting": setting})
