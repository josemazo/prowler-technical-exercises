from django.contrib import admin

from api import models


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at", "updated_at"]


class ProviderAdmin(BaseModelAdmin):
    fields = BaseModelAdmin.readonly_fields + ["name"]
    list_display = ["name"]


class CheckAdmin(BaseModelAdmin):
    fields = BaseModelAdmin.readonly_fields + ["provider", "name"]
    list_display = ["provider__name", "name"]


class ScanAdmin(BaseModelAdmin):
    fields = BaseModelAdmin.readonly_fields + [
        "provider",
        "status",
        "success",
        "started_at",
        "finished_at",
        "name",
        "comment",
    ]
    readonly_fields = BaseModelAdmin.readonly_fields + ["success"]
    list_display = ["provider__name", "status", "success", "name"]


class FindingAdmin(BaseModelAdmin):
    fields = BaseModelAdmin.readonly_fields + ["scan", "check_parent", "success", "comment"]
    list_display = ["scan__provider__name", "scan__name", "check_name", "success"]

    @admin.display(description="Check name", ordering="check_parent__name")
    def check_name(self, obj):
        """Return `check_parent` label as `check`, as admin ignores the `verbose_name` property"""

        return obj.check_parent.name


admin.site.register(models.Provider, ProviderAdmin)
admin.site.register(models.Check, CheckAdmin)
admin.site.register(models.Scan, ScanAdmin)
admin.site.register(models.Finding, FindingAdmin)
