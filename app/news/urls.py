from django.urls import path

from news import views

urlpatterns = [
    path("news", views.news_list, name="news"),
    path("news/<slug:slug>", views.news_item, name="news_item"),
    path("digest/", views.digest, {"kind": "daily"}, name="digest_index"),
    path("digest/daily/<str:day>", views.digest_daily, name="digest_daily"),
    path("digest/weekly/<slug:slug>", views.digest_weekly, name="digest_weekly"),
    path("digest/deep/<slug:slug>", views.digest_deep, name="digest_deep"),
    path("digest/outdated/<str:month>", views.digest_outdated, name="digest_outdated"),
    path("digest/<slug:kind>", views.digest, name="digest"),
    path("timeline", views.timeline, name="timeline"),
]
