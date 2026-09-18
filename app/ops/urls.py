from django.urls import path

from ops import views

urlpatterns = [
    path("", views.ops_home, name="ops_home"),
    path("flags", views.ops_flags, name="ops_flags"),
    path("codes", views.ops_codes, name="ops_codes"),
    path("users", views.ops_users, name="ops_users"),
    path("audit", views.ops_audit, name="ops_audit"),
    path("paywall", views.ops_paywall, name="ops_paywall"),
    path("groups", views.ops_groups, name="ops_groups"),
    path("ads", views.ops_ads, name="ops_ads"),
    path("zones", views.ops_zones, name="ops_zones"),
    path("mail", views.ops_mail, name="ops_mail"),
    path("metrics", views.ops_metrics, name="ops_metrics"),
    path("seo", views.ops_seo, name="ops_seo"),
    path("system", views.ops_system, name="ops_system"),
    path("settings", views.ops_settings, name="ops_settings"),
]
