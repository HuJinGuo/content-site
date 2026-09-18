import pyotp
from django.core.management.base import BaseCommand

from accounts.models import TotpDevice, User


class Command(BaseCommand):
    help = "打印某个员工当前六位 TOTP（本机登录用，不打印密钥）"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@localhost")

    def handle(self, *args, **opts):
        user = User.all_objects.filter(email=opts["email"].lower()).first()
        if user is None:
            self.stderr.write("没有这个账号。先 bootstrap。")
            return
        device = TotpDevice.objects.filter(user=user, confirmed=True).first()
        if device is None:
            self.stderr.write("这个账号没有 TOTP。")
            return
        self.stdout.write(pyotp.TOTP(device.secret).now())
