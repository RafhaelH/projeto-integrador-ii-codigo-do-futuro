from django import forms
from django.db.models import Q

from apps.accounts.models import User, UserRole

from .models import Guardian, Institution, Instructor, Participant, ParticipantGuardian
from .validators import format_phone, only_digits, validate_cnpj, validate_cpf, validate_phone


class ParticipantForm(forms.ModelForm):
    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        required=False,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "placeholder": "000.000.000-00"}),
    )
    phone = forms.CharField(
        label="Telefone",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"type": "tel", "placeholder": "(00) 00000-0000"}),
    )

    class Meta:
        model = Participant
        fields = (
            "user",
            "full_name",
            "birth_date",
            "cpf",
            "contact_email",
            "phone",
            "privacy_consent_at",
            "image_authorization",
            "is_active",
        )
        widgets = {
            "birth_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "privacy_consent_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M:%S.%f",
                attrs={"type": "datetime-local", "step": "any"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            cpf = self.initial.get("cpf")
            if cpf and len(cpf) == 11:
                self.initial["cpf"] = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            if self.initial.get("phone"):
                self.initial["phone"] = format_phone(self.initial["phone"])
        self.fields["privacy_consent_at"].help_text = (
            "Registre somente a data e hora de um consentimento de privacidade efetivamente "
            "obtido do titular ou responsável. Deixe em branco se não houver esse registro. "
            "O campo não autoriza uso de imagem; essa autorização é separada."
        )
        available_users = User.objects.filter(role=UserRole.PARTICIPANT, is_active=True)
        if self.instance.pk and self.instance.user_id:
            available_users = available_users.filter(
                Q(participant_profile__isnull=True) | Q(pk=self.instance.user_id)
            )
        else:
            available_users = available_users.filter(participant_profile__isnull=True)
        self.fields["user"].queryset = available_users.order_by("full_name")

    def clean_cpf(self) -> str | None:
        value = only_digits(self.cleaned_data.get("cpf", ""))
        if value:
            validate_cpf(value)
        return value or None

    def clean_phone(self) -> str:
        value = only_digits(self.cleaned_data.get("phone", ""))
        if value:
            validate_phone(value)
        return value


class GuardianForm(forms.ModelForm):
    phone = forms.CharField(label="Telefone", max_length=15)

    class Meta:
        model = Guardian
        fields = ("full_name", "phone", "email", "is_active")

    def clean_phone(self) -> str:
        value = only_digits(self.cleaned_data["phone"])
        validate_phone(value)
        return value


class ParticipantGuardianForm(forms.ModelForm):
    class Meta:
        model = ParticipantGuardian
        fields = ("guardian", "relationship", "is_primary")

    def __init__(self, *args, participant: Participant, **kwargs):
        self.participant = participant
        super().__init__(*args, **kwargs)
        linked_ids = participant.guardian_links.values_list("guardian_id", flat=True)
        self.fields["guardian"].queryset = Guardian.objects.filter(is_active=True).exclude(
            pk__in=linked_ids
        )

    def clean_is_primary(self) -> bool:
        is_primary = self.cleaned_data["is_primary"]
        if is_primary and self.participant.guardian_links.filter(is_primary=True).exists():
            raise forms.ValidationError("O participante já possui um responsável principal.")
        return is_primary


class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ("user", "biography", "specialties", "is_active")
        widgets = {"biography": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_users = User.objects.filter(role=UserRole.INSTRUCTOR, is_active=True)
        if self.instance.pk and self.instance.user_id:
            available_users = available_users.filter(
                Q(instructor_profile__isnull=True) | Q(pk=self.instance.user_id)
            )
        else:
            available_users = available_users.filter(instructor_profile__isnull=True)
        self.fields["user"].queryset = available_users.order_by("full_name")
        self.fields["user"].help_text = (
            "Selecione um acesso ativo de instrutor ainda não vinculado. "
            "Se não houver opção, use ‘Criar acesso e cadastrar instrutor’ nesta página."
        )


class InstitutionForm(forms.ModelForm):
    document = forms.CharField(label="CNPJ", max_length=18, required=False)
    contact_phone = forms.CharField(label="Telefone de contato", max_length=15, required=False)

    class Meta:
        model = Institution
        fields = (
            "name",
            "document",
            "contact_name",
            "contact_email",
            "contact_phone",
            "address",
            "is_active",
        )

    def clean_document(self) -> str | None:
        value = only_digits(self.cleaned_data.get("document", ""))
        if value:
            validate_cnpj(value)
        return value or None

    def clean_contact_phone(self) -> str:
        value = only_digits(self.cleaned_data.get("contact_phone", ""))
        if value:
            validate_phone(value)
        return value
