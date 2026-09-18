from __future__ import annotations

from content.models import ContentNode


def published():
    return ContentNode.objects.filter(status="published")


def slot_cards(slot: str, *, node=None):
    qs = published().exclude(kind="news")
    if node:
        qs = qs.exclude(pk=node.pk)
        if node.level:
            qs = qs.filter(level=node.level)
    items = list(qs[:3])
    if slot == "R1":
        href, label = "/digest/outdated", "本月过时清单"
        lead = "过时的文章会汇总在这里。收藏过的变化会在学习台提醒你。"
    elif slot == "R2":
        href, label = "/learn", "下一课"
        lead = "不硬锁。建议先读前置，再进下一单元。"
    elif slot == "R3":
        href, label = "/subscribe", "订阅早报与周报"
        lead = "早报可选，周报默认。退订一键。"
    elif slot == "R4":
        href, label = "/tools", "相关工具实测"
        lead = "认证与置顶只在黄页开关打开后影响排序。"
    else:
        href, label = "/glossary", "相关概念"
        lead = "术语与概念卡互相链接。"
    return {"slot": slot, "href": href, "label": label, "lead": lead, "items": items}
