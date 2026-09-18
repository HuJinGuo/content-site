from __future__ import annotations

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import AdvertiserProfile
from ads.models import AdCampaign, AdCreative, GoClick
from codes.models import RedeemError, redeem
from content.models import new_public_id


def _portal_user(request: HttpRequest):
    if not request.user.is_authenticated:
        return None
    if request.user.staff_role in {"advertiser", "adops", "admin"} or request.user.is_superuser:
        return request.user
    if AdvertiserProfile.objects.filter(user=request.user, verified=True).exists():
        return request.user
    return None


def ads_dashboard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("/login?next=/ads/")
    user = _portal_user(request)
    if user is None:
        return render(request, "ads/onboard.html")
    campaigns = AdCampaign.objects.filter(owner=request.user)
    return render(request, "ads/dashboard.html", {"campaigns": campaigns})


@require_http_methods(["GET", "POST"])
def ads_onboard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("/login?next=/ads/onboard")
    error = ""
    if request.method == "POST":
        org = (request.POST.get("org_name") or "")[:80]
        url = request.POST.get("official_url") or ""
        if not org or not url.startswith("https://"):
            error = "请填写主体名称和 https 官网。"
        else:
            AdvertiserProfile.objects.update_or_create(
                user=request.user, defaults={"org_name": org, "verified": True}
            )
            if not request.user.staff_role:
                request.user.staff_role = "advertiser"
                request.user.save(update_fields=["staff_role"])
            return redirect("/ads/")
    return render(request, "ads/onboard.html", {"error": error})


@require_http_methods(["GET", "POST"])
def ads_new(request: HttpRequest) -> HttpResponse:
    if _portal_user(request) is None:
        return HttpResponseForbidden("需要广告主身份")
    error = ""
    if request.method == "POST":
        title = (request.POST.get("title") or "")[:24]
        body = (request.POST.get("body") or "")[:60]
        url = request.POST.get("url") or ""
        if not title or not url.startswith("https://"):
            error = "标题和 https 落地链接必填。不能传脚本。"
        else:
            camp = AdCampaign.objects.create(owner=request.user, title=title, status="pending_review")
            AdCreative.objects.create(
                campaign=camp,
                public_id=new_public_id(),
                title=title,
                body=body,
                url=url,
                status="review",
            )
            return redirect("/ads/")
    return render(request, "ads/new.html", {"error": error})


@require_http_methods(["GET", "POST"])
def ads_redeem(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("/login?next=/ads/redeem")
    error = ""
    if request.method == "POST":
        try:
            redeem(request.user, request.POST.get("code") or "")
            AdvertiserProfile.objects.get_or_create(
                user=request.user, defaults={"org_name": request.user.email, "verified": True}
            )
            if not request.user.staff_role:
                request.user.staff_role = "advertiser"
                request.user.save(update_fields=["staff_role"])
            AdCampaign.objects.create(owner=request.user, title="待填活动（广告码）", status="draft")
            return redirect("/ads/")
        except RedeemError as exc:
            error = exc.message
    return render(request, "ads/redeem.html", {"error": error})


def ads_billing(request: HttpRequest) -> HttpResponse:
    if _portal_user(request) is None:
        return redirect("/ads/")
    campaigns = AdCampaign.objects.filter(owner=request.user)
    return render(request, "ads/billing.html", {"campaigns": campaigns})


def go(request: HttpRequest, public_id: str) -> HttpResponse:
    flags = request.flags
    if not flags.get("ads.enabled"):
        raise Http404()
    creative = AdCreative.objects.filter(public_id=public_id).first()
    if not creative:
        raise Http404()
    GoClick.objects.create(public_id=str(public_id), slot="")
    return redirect(creative.url)
