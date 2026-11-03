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


class InstructorAccessCreationForm(DjangoUserCreationForm):
    """Functional administrators can provision instructors, never privileged accounts."""

    biography = forms.CharField(label="Biografia", required=False, widget=forms.Textarea)
    specialties = forms.CharField(label="Especialidades", required=False, max_length=255)

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "full_name")

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"]).lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso. Informe outro endereço.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserRole.INSTRUCTOR
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        if commit:
            user.save()
        return user


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
