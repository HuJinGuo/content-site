from __future__ import annotations

import pyotp
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import TotpDevice, User

PENDING_TOTP = "pending_totp_uid"


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    totp = forms.CharField(required=False, max_length=8)


def _safe_next(url: str) -> str:
    if url.startswith("/") and not url.startswith("//"):
        return url
    return ""


def _staff_next(request: HttpRequest) -> str:
    return _safe_next(request.GET.get("next") or request.POST.get("next") or "")


def _totp_ok(user, token: str) -> bool:
    device = TotpDevice.objects.filter(user=user, confirmed=True).first()
    if device is None:
        return True
    return bool(token) and pyotp.TOTP(device.secret).verify(token, valid_window=1)


def _finish_login(request: HttpRequest, user, next_url: str) -> HttpResponse:
    request.session.pop(PENDING_TOTP, None)
    if user.is_backoffice:
        request.session.set_expiry(60 * 60 * 12)
    login(request, user)
    if user.is_backoffice:
        return redirect(next_url or "/studio/")
    return redirect(next_url or "/app/")


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    next_url = _staff_next(request)
    staff_intent = request.GET.get("staff") == "1" or next_url.startswith(("/studio", "/admin", "/ops"))
    error = ""
    pending_id = request.session.get(PENDING_TOTP)

    if request.GET.get("cancel"):
        request.session.pop(PENDING_TOTP, None)
        return redirect("/login" + ("?staff=1" if staff_intent else ""))

    if request.user.is_authenticated and not pending_id:
        if request.user.is_backoffice and next_url:
            return redirect(next_url)
        if request.user.is_backoffice and staff_intent:
            return redirect("/studio/")

    if request.method == "POST" and pending_id:
        user = User.objects.filter(pk=pending_id).first()
        if user is None:
            request.session.pop(PENDING_TOTP, None)
            error = "登录已过期，请重新输入邮箱和密码。"
        elif _totp_ok(user, (request.POST.get("totp") or "").strip()):
            return _finish_login(request, user, next_url)
        else:
            error = "验证码不对。打开认证器看当前六位数字。"
        return render(
            request,
            "accounts/login.html",
            {
                "error": error,
                "need_totp": True,
                "pending_email": getattr(user, "email", ""),
                "next": next_url,
                "staff_intent": True,
            },
        )

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"].lower(),
            password=form.cleaned_data["password"],
        )
        if user is None:
            error = "邮箱或密码不对。"
        elif user.is_backoffice and TotpDevice.objects.filter(user=user, confirmed=True).exists():
            token = (form.cleaned_data.get("totp") or "").strip()
            if token and _totp_ok(user, token):
                return _finish_login(request, user, next_url)
            request.session[PENDING_TOTP] = user.pk
            request.session.modified = True
            return render(
                request,
                "accounts/login.html",
                {
                    "error": "",
                    "need_totp": True,
                    "pending_email": user.email,
                    "next": next_url,
                    "staff_intent": True,
                },
            )
        else:
            return _finish_login(request, user, next_url)

    if pending_id:
        pending = User.objects.filter(pk=pending_id).first()
        return render(
            request,
            "accounts/login.html",
            {
                "error": error,
                "need_totp": True,
                "pending_email": getattr(pending, "email", ""),
                "next": next_url,
                "staff_intent": True,
            },
        )

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "error": error,
            "need_totp": False,
            "next": next_url,
            "staff_intent": staff_intent,
            "reader_logged_in": request.user.is_authenticated and not request.user.is_backoffice,
        },
    )


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        name = (request.POST.get("display_name") or "").strip()[:40]
        if not email or len(password) < 10:
            error = "请填写邮箱，密码至少 10 位。"
        elif User.objects.filter(email=email).exists():
            error = "这个邮箱已经注册过。直接登录即可。"
        else:
            user = User.objects.create_user(email=email, password=password, display_name=name)
            login(request, user)
            return redirect("/app/")
    return render(request, "accounts/register.html", {"error": error})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    next_url = _safe_next(request.POST.get("next") or "")
    return redirect(next_url or "/")


@login_required
def account_view(request: HttpRequest) -> HttpResponse:
    return render(request, "app/account.html")


@require_http_methods(["GET", "POST"])
def magic_request(request: HttpRequest) -> HttpResponse:
    import hashlib
    import secrets
    from datetime import timedelta

    from django.core.mail import send_mail
    from django.utils import timezone

    from accounts.models import MagicLink

    sent = False
    error = ""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        user = User.objects.filter(email=email).first()
        if not user:
            error = "这个邮箱还没注册。先注册或用密码登录。"
        else:
            raw = secrets.token_urlsafe(24)
            MagicLink.objects.create(
                user=user,
                token_hash=hashlib.sha256(raw.encode()).hexdigest(),
                expires_at=timezone.now() + timedelta(minutes=15),
            )
            send_mail("登录链接", f"打开 /login/magic/{raw} 完成登录。15 分钟有效。", None, [email])
            sent = True
    return render(request, "accounts/magic.html", {"sent": sent, "error": error})


@require_http_methods(["GET"])
def magic_login(request: HttpRequest, token: str) -> HttpResponse:
    import hashlib

    from django.utils import timezone

    from accounts.models import MagicLink

    digest = hashlib.sha256(token.encode()).hexdigest()
    link = MagicLink.objects.filter(token_hash=digest, used_at__isnull=True).first()
    if link is None or link.expires_at < timezone.now():
        return render(request, "accounts/magic.html", {"error": "链接无效或已过期。", "sent": False})
    link.used_at = timezone.now()
    link.save(update_fields=["used_at"])
    return _finish_login(request, link.user, _safe_next(request.GET.get("next") or ""))


@login_required
@require_http_methods(["POST"])
def account_export(request: HttpRequest) -> HttpResponse:
    from learning.models import Bookmark, Highlight, Progress

    lines = ["# 导出\n"]
    for p in Progress.objects.filter(user=request.user).select_related("node"):
        lines.append(f"- 进度 {p.node.title}\n")
    for b in Bookmark.objects.filter(user=request.user).select_related("node"):
        lines.append(f"- 收藏 {b.node.title}\n")
    for h in Highlight.objects.filter(user=request.user).select_related("node"):
        lines.append(f"- 划线 {h.quote}\n")
    resp = HttpResponse("".join(lines), content_type="text/markdown; charset=utf-8")
    resp["Content-Disposition"] = "attachment; filename=nornless-export.md"
    return resp


@login_required
@require_http_methods(["POST"])
def account_delete(request: HttpRequest) -> HttpResponse:
    from django.utils import timezone

    if request.POST.get("confirm") != "DELETE":
        return render(request, "app/account.html", {"error": "请输入 DELETE 确认。"})
    request.user.delete_requested_at = timezone.now()
    request.user.save(update_fields=["delete_requested_at"])
    return render(request, "app/account.html", {"notice": "已申请删除，7 天内可登录撤销。"})
