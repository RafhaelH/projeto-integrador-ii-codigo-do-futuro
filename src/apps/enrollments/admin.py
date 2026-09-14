from django.contrib import admin

from .models import Enrollment, EnrollmentStatusHistory


class EnrollmentStatusHistoryInline(admin.TabularInline):
    model = EnrollmentStatusHistory
    extra = 0
    can_delete = False
    readonly_fields = ("from_status", "to_status", "reason", "changed_by", "created_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("participant", "class_group", "status", "created_at")
    list_filter = ("status", "class_group")
    search_fields = ("participant__full_name", "class_group__code", "class_group__title")
    readonly_fields = ("waitlisted_at", "confirmed_at", "cancelled_at", "created_at", "updated_at")
    inlines = (EnrollmentStatusHistoryInline,)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EnrollmentStatusHistory)
class EnrollmentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("to_status",)
    readonly_fields = (
        "enrollment",
        "from_status",
        "to_status",
        "reason",
        "changed_by",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
