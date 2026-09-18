from django.contrib import admin
from django.contrib.admin import AdminSite

from accounts.models import User
from ads.models import AdCampaign, AdCreative
from content.models import ContentNode, StaticPage
from core.models import AuditLog, FeatureFlag, SiteSetting
from news.models import Issue


class SuperAdminSite(AdminSite):
    site_header = "ai.nornless.com"
    site_title = "django-admin"
    index_title = "仅 Super"

    def has_permission(self, request):
        return bool(getattr(request.user, "is_active", False) and getattr(request.user, "is_superuser", False))


site = SuperAdminSite(name="superadmin")


class ReadWriteAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return bool(request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


for model in (User, ContentNode, StaticPage, FeatureFlag, SiteSetting, AuditLog, Issue, AdCampaign, AdCreative):
    site.register(model, ReadWriteAdmin)
