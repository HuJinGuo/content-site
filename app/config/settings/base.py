from __future__ import annotations

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

BASE_DIR = Path(__file__).resolve().parents[2]  # app/
REPO_DIR = BASE_DIR.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-for-prod")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

SITE_ORIGIN = os.environ.get("SITE_ORIGIN", "http://127.0.0.1:8000")
CARD_SHOP_URL = os.environ.get("CARD_SHOP_URL", "")
IMPORT_TOKEN = os.environ.get("IMPORT_TOKEN", "")
MAIL_WEBHOOK_SECRET = os.environ.get("MAIL_WEBHOOK_SECRET", "")
NORNLESS_API_BASE = os.environ.get("NORNLESS_API_BASE", "")
NORNLESS_API_KEY = os.environ.get("NORNLESS_API_KEY", "")
NORNLESS_MODEL = os.environ.get("NORNLESS_MODEL", "grok-4")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django_htmx",
    "core",
    "accounts",
    "access",
    "codes",
    "graph",
    "content",
    "learning",
    "news",
    "issues",
    "entities",
    "search",
    "ask",
    "generation",
    "ads",
    "zones",
    "mail",
    "seo",
    "telemetry",
    "studio",
    "ops",
    "api",
]

MIDDLEWARE = [
    "core.middleware.SecurityHeadersMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "core.middleware.MaintenanceMiddleware",
    "core.middleware.FlagSnapshotMiddleware",
    "core.middleware.RedirectMiddleware",
    "core.middleware.RateLimitMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context.site",
            ],
        },
    }
]

STATIC_URL = "static/"
STATIC_ROOT = REPO_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = REPO_DIR / "media"

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/app"
LOGOUT_REDIRECT_URL = "/"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
# 后台会话 12h，在 accounts 登录时按角色缩短

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")


def _database() -> dict:
    url = os.environ.get("DATABASE_URL", f"sqlite:///{REPO_DIR / 'db.sqlite3'}")
    if url.startswith("sqlite"):
        path = url.split("sqlite:///")[-1]
        if path in {"", "sqlite"}:
            path = str(REPO_DIR / "db.sqlite3")
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": path,
            }
        }
    if url.startswith("postgres"):
        try:
            import dj_database_url  # type: ignore
        except ImportError:
            # 最小解析
            from urllib.parse import urlparse

            u = urlparse(url)
            return {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": (u.path or "/nornless").lstrip("/"),
                    "USER": u.username or "",
                    "PASSWORD": u.password or "",
                    "HOST": u.hostname or "127.0.0.1",
                    "PORT": str(u.port or 5432),
                }
            }
        return {"default": dj_database_url.parse(url)}
    raise ImproperlyConfigured(f"unsupported DATABASE_URL: {url}")


DATABASES = _database()

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "nornless",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
