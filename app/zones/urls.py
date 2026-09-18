from django.urls import path

from zones import views

urlpatterns = [
    path("jobs", views.jobs, name="jobs"),
    path("launches", views.launches, name="launches"),
    path("events", views.events, name="events"),
    path("deals", views.deals, name="deals"),
    path("sponsored", views.sponsored, name="sponsored"),
    path("sponsored/<int:pk>", views.sponsored_item, name="sponsored_item"),
    path("advertise", views.advertise, name="advertise"),
]
