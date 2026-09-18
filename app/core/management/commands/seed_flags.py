from django.core.management.base import BaseCommand

from core.flags import FLAG_DEFAULTS
from core.models import FeatureFlag, SiteSetting


class Command(BaseCommand):
    help = "写入开关默认值与站点设置行"

    def handle(self, *args, **opts):
        SiteSetting.load()
        for key, value in FLAG_DEFAULTS.items():
            FeatureFlag.all_objects.get_or_create(key=key, defaults={"value": value})
        self.stdout.write("flags seeded")
