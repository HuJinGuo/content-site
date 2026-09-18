from django.urls import path

from learning import views

urlpatterns = [
    path("", views.app_home, name="app_home"),
    path("library", views.library, name="library"),
    path("downloads", views.downloads, name="downloads"),
    path("briefing", views.briefing, name="briefing"),
    path("ask", views.ask, name="ask"),
]
