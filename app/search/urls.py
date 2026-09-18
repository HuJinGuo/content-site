from django.urls import path

from search.views import search_view

urlpatterns = [path("search", search_view, name="search")]
