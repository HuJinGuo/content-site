from django.urls import path

from accounts import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("login/magic", views.magic_request, name="magic_request"),
    path("login/magic/<str:token>", views.magic_login, name="magic_login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("app/account", views.account_view, name="account"),
    path("app/account/export", views.account_export, name="account_export"),
    path("app/account/delete", views.account_delete, name="account_delete"),
]
