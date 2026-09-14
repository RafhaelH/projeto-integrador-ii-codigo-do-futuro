from django.contrib import admin

from .models import ClassGroup, ClassInstructor, Meeting, Workshop


class ClassInstructorInline(admin.TabularInline):
    model = ClassInstructor
    extra = 0


class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("title", "estimated_hours", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "workshop", "start_date", "status")
    list_filter = ("status", "workshop")
    search_fields = ("code", "title", "location")
    inlines = (ClassInstructorInline, MeetingInline)


@admin.register(ClassInstructor)
class ClassInstructorAdmin(admin.ModelAdmin):
    list_display = ("class_group", "instructor", "is_lead")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "class_group", "starts_at", "status")
    list_filter = ("status",)
