from __future__ import annotations

import secrets

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control

from core.flags import ZONE_FLAGS
from core.models import SiteSetting
from core.services import snapshot


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["X-Frame-Options"] = "DENY"
        nonce = getattr(request, "csp_nonce", "")
        csp = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "frame-src 'self'; "
            "connect-src 'self'"
        )
        response["Content-Security-Policy"] = csp
        return response


class FlagSnapshotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.flags = snapshot()
        path = request.path
        flags = request.flags
        if path.startswith("/advertise") and not flags.get("ads.enabled"):
            raise Http404()
        for prefix, flag_key in ZONE_FLAGS.items():
            if path == prefix or path.startswith(prefix + "/"):
                if flag_key == "ads.enabled":
                    continue
                if not flags.get("ads.enabled") or not flags.get(flag_key):
                    raise Http404()
        if path.startswith("/pricing") and not flags.get("supporter.enabled"):
            raise Http404()
        if path.startswith("/app/ask") and not flags.get("ask.enabled"):
            raise Http404()
        if path.startswith("/join") and not flags.get("groups.enabled"):
            raise Http404()
        if path.startswith("/quiz") and not flags.get("quiz.enabled"):
            raise Http404()
        if path.startswith("/lab") and not flags.get("labs.enabled"):
            raise Http404()
        if (path == "/ads" or path.startswith("/ads/")) and not flags.get("ads.enabled"):
            user = getattr(request, "user", None)
            roles = flags.get("ads.preview_roles") or ["admin"]
            role = getattr(user, "staff_role", "") if user and getattr(user, "is_authenticated", False) else ""
            if role not in roles and not (user and getattr(user, "is_superuser", False)):
                raise Http404()
        response = self.get_response(request)
        if getattr(request, "user", None) and request.user.is_authenticated:
            patch_cache_control(response, private=True)
        return response


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        try:
            from seo.models import RedirectRule

            rule = RedirectRule.objects.filter(src=path).first()
        except Exception:
            rule = None
        if rule:
            if rule.code == 410:
                raise Http404()
            return redirect(rule.dst, permanent=rule.code == 301)
        return self.get_response(request)


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith("/studio") or path.startswith("/ops") or path.startswith("/admin") or path.startswith("/django-admin") or path.startswith("/api/v1/health"):
            return self.get_response(request)
        try:
            setting = SiteSetting.load()
        except Exception:
            return self.get_response(request)
        if setting.maintenance:
            body = (
                "<!doctype html><meta charset=utf-8><title>维护中</title>"
                "<body style='font-family:system-ui;padding:48px'><h1>站点维护中</h1>"
                "<p>请稍后再来。</p></body>"
            )
            resp = HttpResponse(body, status=503)
            resp["Retry-After"] = "300"
            return resp
        return self.get_response(request)


class RateLimitMiddleware:
    """按 IP 哈希的粗限流；细规则在服务层。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
