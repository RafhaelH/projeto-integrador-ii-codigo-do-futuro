from django.contrib import admin

from .models import Guardian, Institution, Instructor, Participant, ParticipantGuardian


class ParticipantGuardianInline(admin.TabularInline):
    model = ParticipantGuardian
    extra = 0
    autocomplete_fields = ("guardian",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "masked_cpf", "birth_date", "is_active")
    list_filter = ("is_active", "image_authorization")
    search_fields = ("full_name", "cpf", "contact_email")
    autocomplete_fields = ("user",)
    inlines = (ParticipantGuardianInline,)


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ("full_name", "formatted_phone", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("full_name", "phone", "email")


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("user", "specialties", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__full_name", "user__email", "specialties")
    autocomplete_fields = ("user",)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "formatted_contact_phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "document", "contact_name")
