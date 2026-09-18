from __future__ import annotations

from core.models import SiteSetting
from core.services import snapshot


def site(request):
    flags = getattr(request, "flags", None) or snapshot()
    try:
        setting = SiteSetting.load()
    except Exception:
        setting = None
    return {
        "flags": flags,
        "site_notice": getattr(setting, "notice", "") if setting else "",
        "card_shop_url": getattr(setting, "card_shop_url", "") if setting else "",
        "csp_nonce": getattr(request, "csp_nonce", ""),
        "supporter_price": getattr(setting, "supporter_price", "") if setting else "",
    }
