from django import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from codes.models import RedeemError, redeem


class RedeemForm(forms.Form):
    code = forms.CharField(max_length=20, label="兑换码")


@require_http_methods(["GET", "POST"])
def redeem_view(request: HttpRequest) -> HttpResponse:
    form = RedeemForm(request.POST or None)
    error = ""
    success = ""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return render(request, "site/redeem.html", {"form": form, "error": "兑码需要先登录。", "need_login": True})
        if form.is_valid():
            try:
                code = redeem(request.user, form.cleaned_data["code"])
                labels = {"member": "会员权益已生效。", "content": "这篇文章已解锁。", "ad": "广告主身份已开通。"}
                success = labels.get(code.kind, "兑换成功。")
            except RedeemError as exc:
                error = exc.message
    return render(request, "site/redeem.html", {"form": form, "error": error, "success": success})
