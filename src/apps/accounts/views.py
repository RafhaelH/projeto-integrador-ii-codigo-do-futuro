from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import OwnProfileForm


class OwnProfileView(LoginRequiredMixin, UpdateView):
    form_class = OwnProfileForm
    template_name = "accounts/own_profile.html"
    success_url = reverse_lazy("accounts:profile")
    success_message = "Seu perfil foi atualizado."
    http_method_names = ["get", "post", "head", "options"]

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # Save only the whitelist, even if another request changes permissions concurrently.
        self.object = form.save(commit=False)
        try:
            with transaction.atomic():
                self.object.save(update_fields=["full_name", "email", "updated_at"])
        except IntegrityError as error:
            constraint = getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)
            sqlite_duplicate = str(error) in {
                "UNIQUE constraint failed: accounts_user.email",
                "UNIQUE constraint failed: index 'accounts_user_email_ci_unique'",
            }
            if (
                constraint not in {"accounts_user_email_key", "accounts_user_email_ci_unique"}
                and not sqlite_duplicate
            ):
                raise
            form.add_error("email", "Este e-mail já está em uso.")
            return self.form_invalid(form)
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())
