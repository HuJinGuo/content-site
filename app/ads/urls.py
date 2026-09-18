from django.urls import path

from ads import views

urlpatterns = [
    path("", views.ads_dashboard, name="ads_home"),
    path("onboard", views.ads_onboard, name="ads_onboard"),
    path("new", views.ads_new, name="ads_new"),
    path("redeem", views.ads_redeem, name="ads_redeem"),
    path("billing", views.ads_billing, name="ads_billing"),
    path("go/<str:public_id>", views.go, name="go"),
]
