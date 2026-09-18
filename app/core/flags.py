"""开关默认值。键名只用 05 §2.2。"""

from __future__ import annotations

from typing import Any

# 默认关：ads.* / paywall / quiz / labs / supporter / ask / groups / wechat_login / search.semantic / tipping
FLAG_DEFAULTS: dict[str, Any] = {
    "ads.enabled": False,
    "ads.preview_roles": ["admin"],
    "ads.house": False,
    "ads.direct": False,
    "ads.self_serve.tools": False,
    "ads.self_serve.jobs": False,
    "ads.launches": False,
    "ads.events": False,
    "ads.deals": False,
    "ads.sponsored_content": False,
    "ads.email_sponsor": False,
    "ads.programmatic": False,
    "ads.slots.R1": False,
    "ads.slots.R2": False,
    "ads.slots.R3": False,
    "ads.slots.R4": False,
    "ads.slots.R5": False,
    "ads.max_per_page": 2,
    "supporter.enabled": False,
    "ask.enabled": False,
    "quiz.enabled": False,
    "paywall.enabled": False,
    "labs.enabled": False,
    "tipping.enabled": False,
    "groups.enabled": False,
    "wechat_login.enabled": False,
    "search.semantic": False,
    "email.digest": True,
    "outdated.banner": True,
}

# 关时必须 404 的路由前缀（按开关）。工具目录 /tools 常开，付费层另判。
FLAG_GATED_PATHS: dict[str, str] = {
    "ads.self_serve.jobs": "/jobs",
    "ads.launches": "/launches",
    "ads.events": "/events",
    "ads.deals": "/deals",
    "ads.sponsored_content": "/sponsored",
    "supporter.enabled": "/pricing",
    "ask.enabled": "/app/ask",
    "groups.enabled": "/join",
    "quiz.enabled": "/quiz",
    "labs.enabled": "/lab",
}

# ads.enabled 关时，所有 ads.* 视为关，且这些路径 404
ADS_DEPENDENT = [
    "ads.house",
    "ads.direct",
    "ads.self_serve.tools",
    "ads.self_serve.jobs",
    "ads.launches",
    "ads.events",
    "ads.deals",
    "ads.sponsored_content",
    "ads.email_sponsor",
    "ads.programmatic",
    "ads.slots.R1",
    "ads.slots.R2",
    "ads.slots.R3",
    "ads.slots.R4",
    "ads.slots.R5",
]

ZONE_FLAGS = {
    "/jobs": "ads.self_serve.jobs",
    "/launches": "ads.launches",
    "/events": "ads.events",
    "/deals": "ads.deals",
    "/sponsored": "ads.sponsored_content",
    "/advertise": "ads.enabled",
}
