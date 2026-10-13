from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .forms import MeetingAdminForm, ProtectedStatusAdminForm
from .models import ClassGroup, ClassInstructor, Meeting, Workshop


class ClassInstructorInline(admin.TabularInline):
    model = ClassInstructor
    extra = 0


class MeetingInline(admin.TabularInline):
    model = Meeting
    form = MeetingAdminForm
    readonly_fields = ("status",)
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None):
        return super().has_add_permission(request, obj) and (
            obj is None or obj.status not in {"COMPLETED", "CANCELLED"}
        )


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    form = ProtectedStatusAdminForm
    readonly_fields = ("status", "workflow")
    list_display = ("title", "estimated_hours", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Alterar situação")
    def workflow(self, obj):
        if not obj or not obj.pk:
            return "A oficina será criada como rascunho."
        return format_html(
            '<a href="{}">Publicar ou arquivar na aplicação</a>',
            reverse("workshops:workshop-detail", kwargs={"pk": obj.pk}),
        )


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    form = ProtectedStatusAdminForm
    readonly_fields = ("status", "workflow")
    list_display = ("code", "title", "workshop", "start_date", "status")
    list_filter = ("status", "workshop")
    search_fields = ("code", "title", "location")
    inlines = (ClassInstructorInline, MeetingInline)

    @admin.display(description="Transições e conclusão")
    def workflow(self, obj):
        if not obj or not obj.pk:
            return "A turma será criada como planejada."
        return format_html(
            '<a href="{}">Abrir, iniciar, cancelar ou processar a conclusão na aplicação</a>',
            reverse("workshops:class-detail", kwargs={"pk": obj.pk}),
        )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClassInstructor)
class ClassInstructorAdmin(admin.ModelAdmin):
    list_display = ("class_group", "instructor", "is_lead")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    form = MeetingAdminForm
    readonly_fields = ("status", "workflow")
    list_display = ("title", "class_group", "starts_at", "status")
    list_filter = ("status",)

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (("class_group",) if obj else ())

    @admin.display(description="Processar encontro")
    def workflow(self, obj):
        if not obj or not obj.pk:
            return "O encontro será criado como planejado."
        return format_html(
            '<a href="{}">Cronograma, cancelamento e registro de chamada na aplicação</a>',
            reverse("workshops:class-detail", kwargs={"pk": obj.class_group_id}),
        )

    def has_delete_permission(self, request, obj=None):
        return False
