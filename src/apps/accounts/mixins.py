from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles: tuple[str, ...] = ()
    raise_exception = True

    def test_func(self) -> bool:
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("ADMIN",)
