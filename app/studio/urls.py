from django.urls import path

from studio import views

urlpatterns = [
    path("", views.studio_home, name="studio_home"),
    path("posts", views.studio_posts, name="studio_posts"),
    path("review", views.studio_review, name="studio_review"),
    path("publish/<slug:slug>", views.studio_publish, name="studio_publish"),
    path("topics", views.studio_topics, name="studio_topics"),
    path("briefs", views.studio_briefs, name="studio_briefs"),
    path("generate", views.studio_generate, name="studio_generate"),
    path("editor", views.studio_editor_new, name="studio_editor_new"),
    path("editor/<slug:slug>", views.studio_editor, name="studio_editor"),
    path("qa/<slug:slug>", views.studio_qa, name="studio_qa"),
    path("facts/<slug:slug>", views.studio_facts, name="studio_facts"),
    path("issues", views.studio_issues, name="studio_issues"),
    path("graph", views.studio_graph, name="studio_graph"),
    path("sources", views.studio_sources, name="studio_sources"),
    path("entities", views.studio_entities, name="studio_entities"),
    path("refresh", views.studio_refresh, name="studio_refresh"),
    path("errata", views.studio_errata, name="studio_errata"),
    path("assets", views.studio_assets, name="studio_assets"),
    path("prompts", views.studio_prompts, name="studio_prompts"),
    path("costs", views.studio_costs, name="studio_costs"),
]
