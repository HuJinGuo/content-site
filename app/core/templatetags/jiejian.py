from django import template

from core.flags import FLAG_DEFAULTS

register = template.Library()


@register.simple_tag(takes_context=True)
def flag(context, key: str) -> bool:
    flags = context.get("flags")
    if flags is None:
        return bool(FLAG_DEFAULTS.get(key))
    return bool(flags.get(key))


@register.filter
def level_label(value: str) -> str:
    names = {
        "L0": "方向与边界",
        "L1": "常识与工具素养",
        "L2": "选型与成本",
        "L3": "搭建",
        "L4": "工作流与 Agent",
        "L5": "应用与场景",
        "L6": "工程化",
        "L7": "原理与前沿",
    }
    return names.get(value, value)
