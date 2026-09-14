from django.contrib import admin

from .models import Attendance, Evaluation, StudentProject


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


@admin.register(StudentProject)
class StudentProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "enrollment", "is_delivered", "delivered_at", "updated_at")
    list_filter = ("is_delivered", "enrollment__class_group")
    search_fields = ("title", "enrollment__participant__full_name")
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "final_score", "evaluated_by", "published_at", "updated_at")
    list_filter = ("enrollment__class_group", "published_at")
    search_fields = ("enrollment__participant__full_name",)
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False
