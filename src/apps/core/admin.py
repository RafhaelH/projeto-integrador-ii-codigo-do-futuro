from django.contrib import admin


class DomainRecordAdmin(admin.ModelAdmin):
    """Academic writes use application services, preserving eligibility and authorship."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
