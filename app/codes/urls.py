from django.urls import path

from codes import views

urlpatterns = [
    path("redeem", views.redeem_view, name="redeem"),
]
