from __future__ import annotations

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_flag_cache():
    cache.clear()
    yield
    cache.clear()
