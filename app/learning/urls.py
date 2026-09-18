from django.urls import path

from learning import views

urlpatterns = [
    path("assess", views.assess, name="assess"),
    path("articles/<slug:slug>/read", views.mark_read, name="mark_read"),
]
