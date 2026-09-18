from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from django.core.cache import cache

from core.flags import ADS_DEPENDENT, FLAG_DEFAULTS

CACHE_KEY = "flags:snapshot"
CACHE_TTL = 30


class Flags:
    def __init__(self, data: dict[str, Any], version: int = 1):
        self._data = data
        self.version = version

    def get(self, key: str, default: Any = None) -> Any:
        if key.startswith("ads.") and key != "ads.enabled" and key in ADS_DEPENDENT:
            if not self._data.get("ads.enabled"):
                if key == "ads.max_per_page":
                    return self._data.get(key, 2)
                if key == "ads.preview_roles":
                    return self._data.get(key, ["admin"])
                return False
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def ads_on(self) -> bool:
        return bool(self.get("ads.enabled"))

    def as_dict(self) -> dict[str, Any]:
        return dict(self._data)


def snapshot() -> Flags:
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached
    data = dict(FLAG_DEFAULTS)
    version = 1
    try:
        from core.models import FeatureFlag, SiteSetting

        setting = SiteSetting.load()
        version = setting.flags_version
        for row in FeatureFlag.objects.all():
            data[row.key] = row.value
    except Exception:
        pass
    flags = Flags(data, version=version)
    cache.set(CACHE_KEY, flags, CACHE_TTL)
    return flags


def invalidate() -> None:
    cache.delete(CACHE_KEY)


def set_flag(key: str, value: Any, *, actor, reason: str) -> Flags:
    if key not in FLAG_DEFAULTS:
        raise ValueError(f"unknown flag {key}")
    if not reason:
        raise ValueError("reason required")
    from core.models import AuditLog, FeatureFlag, SiteSetting

    row, _ = FeatureFlag.all_objects.get_or_create(key=key, defaults={"value": value})
    before = row.value
    row.value = value
    row.deleted_at = None
    row.save()
    setting = SiteSetting.load()
    setting.flags_version += 1
    setting.save(update_fields=["flags_version", "updated_at"])
    AuditLog.objects.create(
        actor_id=getattr(actor, "id", None),
        action="flag.set",
        obj_type="feature_flag",
        obj_id=key,
        before=before,
        after=value,
        reason=reason,
    )
    invalidate()
    return snapshot()


def ip_hash(ip: str) -> str:
    salt = date.today().isoformat()
    return hashlib.sha256(f"{ip}:{salt}".encode()).hexdigest()
