from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "meeting", "status", "recorded_by", "updated_at")
    list_filter = ("status", "meeting__class_group")
    search_fields = ("enrollment__participant__full_name", "meeting__title")
    readonly_fields = (
        "enrollment",
        "meeting",
        "status",
        "note",
        "recorded_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
