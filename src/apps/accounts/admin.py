from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db import transaction

from .forms import UserChangeForm, UserCreationForm
from .models import User, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        with transaction.atomic():
            if request.method == "POST":
                # Serialize administrator removals before validating the form.
                list(
                    User.objects.select_for_update()
                    .filter(role=UserRole.ADMIN, is_active=True)
                    .order_by("pk")
                )
            return super().changeform_view(request, object_id, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        # Accounts with history are deactivated instead (RN-007).
        return False

    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    ordering = ("full_name",)
    list_display = ("email", "full_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "full_name")
    readonly_fields = ("last_login", "date_joined", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Identificação", {"fields": ("full_name", "role")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "role", "password1", "password2"),
            },
        ),
    )
