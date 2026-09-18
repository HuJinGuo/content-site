from __future__ import annotations

from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView

from ads.views import go
from api.router import api
from config.admin import site as super_admin
from seo.sitemaps import sitemaps

handler404 = "content.views.page_not_found"

urlpatterns = [
    path("django-admin/", super_admin.urls),
    path("go/<str:public_id>", go, name="go"),
    path("api/v1/", api.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}),
    path("studio/", include("studio.urls")),
    path("admin/", include("ops.urls")),
    path("ops/<path:rest>", RedirectView.as_view(url="/admin/%(rest)s", query_string=True)),
    path("ops/", RedirectView.as_view(url="/admin/", query_string=True)),
    path("ads/", include("ads.urls")),
    path("app/", include("learning.urls_app")),
    path("", include("content.urls")),
    path("", include("accounts.urls")),
    path("", include("codes.urls")),
    path("", include("learning.urls")),
    path("", include("news.urls")),
    path("", include("search.urls")),
    path("", include("entities.urls")),
    path("", include("zones.urls")),
    path("", include("seo.urls")),
]
