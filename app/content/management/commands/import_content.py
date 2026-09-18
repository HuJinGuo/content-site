from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from content.models import import_markdown


class Command(BaseCommand):
    help = "导入 content/ 下 Markdown（front-matter v3）"

    def add_arguments(self, parser):
        parser.add_argument("root", nargs="?", default=str(settings.REPO_DIR / "content" if hasattr(settings, "REPO_DIR") else Path("content")))

    def handle(self, *args, **opts):
        from django.conf import settings as dj

        root = Path(opts["root"])
        if not root.is_absolute():
            root = dj.REPO_DIR / root
        if not root.exists():
            self.stderr.write(f"missing {root}")
            return
        n = 0
        for path in sorted(root.rglob("*.md")):
            node = import_markdown(path)
            n += 1
            self.stdout.write(f"imported {node.slug} ({node.status})")
        self.stdout.write(f"done {n}")
