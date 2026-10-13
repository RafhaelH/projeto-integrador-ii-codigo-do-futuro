from django import forms
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm

from .models import User, UserRole


class OwnProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("full_name", "email")
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"]).lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "full_name", "role")


class UserChangeForm(DjangoUserChangeForm):
    def clean(self):
        cleaned = super().clean()
        if self.instance.pk:
            current = User.objects.get(pk=self.instance.pk)
            remains_admin = (
                cleaned.get("role") == UserRole.ADMIN
                and cleaned.get("is_active")
                and cleaned.get("is_staff")
            )
            if (
                current.role == UserRole.ADMIN
                and current.is_active
                and not remains_admin
                and not User.objects.filter(role=UserRole.ADMIN, is_active=True, is_staff=True)
                .exclude(pk=current.pk)
                .exists()
            ):
                raise forms.ValidationError(
                    "Não é possível desativar ou retirar o acesso do único administrador ativo."
                )
        return cleaned

    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "full_name",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
        )
