from __future__ import annotations

from django.db import models

from core.models import AliveManager, TimeStamped

LEVELS = [(f"L{i}", f"L{i}") for i in range(8)]
DOMAINS = [
    ("general", "通用认知"),
    ("office", "办公与学习"),
    ("dev-agent", "开发与 Agent"),
    ("aigc", "AIGC 创作"),
    ("industry", "行业与岗位"),
    ("theory", "原理与研究"),
]


class GraphNode(TimeStamped):
    """大纲节点（editorial/outline.yml 同步）。"""

    node_id = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=80)
    level = models.CharField(max_length=4, choices=LEVELS)
    domain = models.CharField(max_length=20, choices=DOMAINS)
    status = models.CharField(max_length=20, default="empty")  # empty planned draft published
    objects = AliveManager()
    all_objects = models.Manager()


class NodeEdge(TimeStamped):
    src = models.ForeignKey(GraphNode, on_delete=models.CASCADE, related_name="out_edges")
    dst = models.ForeignKey(GraphNode, on_delete=models.CASCADE, related_name="in_edges")
    kind = models.CharField(max_length=20, default="prereq")
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["src", "dst", "kind"], name="uniq_edge")]


class LearningPath(TimeStamped):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    summary = models.CharField(max_length=200)
    level_from = models.CharField(max_length=4, default="L0")
    level_to = models.CharField(max_length=4, default="L7")
    domain = models.CharField(max_length=20, default="dev-agent")
    status = models.CharField(max_length=20, default="published")
    eta_hours = models.PositiveIntegerField(default=6)
    objects = AliveManager()
    all_objects = models.Manager()


class PathItem(TimeStamped):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="items")
    unit_index = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=80)
    goal = models.CharField(max_length=200)
    node = models.ForeignKey("content.ContentNode", null=True, blank=True, on_delete=models.SET_NULL)
    objects = AliveManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["path", "unit_index"], name="uniq_path_item")]
        ordering = ["unit_index"]
