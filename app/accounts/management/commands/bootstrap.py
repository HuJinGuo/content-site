from __future__ import annotations

import pyotp
from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import TotpDevice, User
from core.models import SiteSetting


class Command(BaseCommand):
    help = "建站长账号（含 TOTP）、写入开关默认值"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@localhost")
        parser.add_argument("--password", default="admin123456")

    def handle(self, *args, **opts):
        call_command("seed_flags")
        SiteSetting.load()
        email = opts["email"].lower()
        user = User.all_objects.filter(email=email).first()
        if user is None:
            user = User.objects.create_superuser(email, opts["password"], display_name="站长")
        else:
            user.set_password(opts["password"])
            user.is_staff = True
            user.is_superuser = True
            user.staff_role = "admin"
            user.save()
        secret = pyotp.random_base32()
        TotpDevice.all_objects.update_or_create(
            user=user, defaults={"secret": secret, "confirmed": True, "deleted_at": None}
        )
        uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="ai.nornless.com")
        self.stdout.write(self.style.WARNING("TOTP secret（只显示一次，请写入认证器）："))
        self.stdout.write(secret)
        self.stdout.write(uri)
        self.stdout.write(f"login {email} / 设定的密码 + 六位验证码")
