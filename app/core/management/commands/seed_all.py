from django.core.management import call_command
from django.core.management.base import BaseCommand

from content.models import ContentNode
from graph.models import PathItem

PATH_LINKS = [
    ("ask-better", 1, "prompt-basics"),
    ("ask-better", 2, "system-prompt"),
    ("ask-better", 3, "review-an-answer"),
    ("hold-agent", 1, "when-not-agent"),
    ("hold-agent", 2, "agent-vs-workflow"),
    ("hold-agent", 3, "agent-first"),
    ("office-ai", 1, "when-to-use-ai"),
    ("office-ai", 2, "task-brief"),
    ("office-ai", 3, "review-an-answer"),
]


class Command(BaseCommand):
    help = "开关 + 大纲 + 静态页 + 导入 content/"

    def handle(self, *args, **opts):
        call_command("seed_flags")
        call_command("seed_outline")
        call_command("seed_site")
        call_command("import_content")
        for path_slug, idx, node_slug in PATH_LINKS:
            node = ContentNode.objects.filter(slug=node_slug).first()
            if node is None:
                continue
            PathItem.objects.filter(path__slug=path_slug, unit_index=idx).update(node=node)
        self.stdout.write(self.style.SUCCESS("seed_all done"))
