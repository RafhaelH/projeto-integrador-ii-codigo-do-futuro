from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.accounts.models import UserRole
from apps.core.models import UUIDTimestampedModel

from .validators import format_phone, only_digits, validate_cnpj, validate_cpf, validate_phone


class Participant(UUIDTimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        related_name="participant_profile",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    full_name = models.CharField("nome completo", max_length=150)
    birth_date = models.DateField("data de nascimento")
    cpf = models.CharField(
        "CPF",
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_cpf],
    )
    contact_email = models.EmailField("e-mail de contato", blank=True)
    phone = models.CharField(
        "telefone",
        max_length=11,
        blank=True,
        validators=[validate_phone],
    )
    is_active = models.BooleanField("ativo", default=True)
    privacy_consent_at = models.DateTimeField(
        "consentimento de privacidade em", null=True, blank=True
    )
    image_authorization = models.BooleanField("autorização de imagem", default=False)

    class Meta:
        verbose_name = "participante"
        verbose_name_plural = "participantes"
        ordering = ["full_name"]

    def clean(self) -> None:
        super().clean()
        if self.user_id and self.user.role != UserRole.PARTICIPANT:
            raise ValidationError({"user": "O usuário vinculado deve possuir perfil participante."})

    def save(self, *args, **kwargs):
        self.cpf = only_digits(self.cpf) or None
        self.phone = only_digits(self.phone)
        super().save(*args, **kwargs)

    @property
    def formatted_cpf(self) -> str:
        if not self.cpf:
            return "Não informado"
        return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"

    @property
    def masked_cpf(self) -> str:
        if not self.cpf:
            return "—"
        return f"***.{self.cpf[3:6]}.{self.cpf[6:9]}-**"

    @property
    def formatted_phone(self) -> str:
        return format_phone(self.phone) if self.phone else "Não informado"

    def __str__(self) -> str:
        return self.full_name


class Guardian(UUIDTimestampedModel):
    full_name = models.CharField("nome completo", max_length=150)
    phone = models.CharField("telefone", max_length=11, validators=[validate_phone])
    email = models.EmailField("e-mail", blank=True)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "responsável"
        verbose_name_plural = "responsáveis"
        ordering = ["full_name"]

    def save(self, *args, **kwargs):
        self.phone = only_digits(self.phone)
        super().save(*args, **kwargs)

    @property
    def formatted_phone(self) -> str:
        return format_phone(self.phone)

    def __str__(self) -> str:
        return self.full_name


class GuardianRelationship(models.TextChoices):
    MOTHER = "MOTHER", "Mãe"
    FATHER = "FATHER", "Pai"
    LEGAL_GUARDIAN = "LEGAL_GUARDIAN", "Tutor legal"
    OTHER = "OTHER", "Outro"


class ParticipantGuardian(UUIDTimestampedModel):
    participant = models.ForeignKey(
        Participant,
        verbose_name="participante",
        related_name="guardian_links",
        on_delete=models.CASCADE,
    )
    guardian = models.ForeignKey(
        Guardian,
        verbose_name="responsável",
        related_name="participant_links",
        on_delete=models.PROTECT,
    )
    relationship = models.CharField(
        "vínculo",
        max_length=30,
        choices=GuardianRelationship.choices,
    )
    is_primary = models.BooleanField("responsável principal", default=False)

    class Meta:
        verbose_name = "vínculo com responsável"
        verbose_name_plural = "vínculos com responsáveis"
        ordering = ["-is_primary", "guardian__full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "guardian"],
                name="people_participant_guardian_unique",
            ),
            models.UniqueConstraint(
                fields=["participant"],
                condition=Q(is_primary=True),
                name="people_participant_primary_guardian_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.participant} — {self.guardian}"


class Instructor(UUIDTimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        related_name="instructor_profile",
        on_delete=models.PROTECT,
    )
    biography = models.TextField("biografia", blank=True)
    specialties = models.CharField("especialidades", max_length=255, blank=True)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "instrutor"
        verbose_name_plural = "instrutores"
        ordering = ["user__full_name"]

    def clean(self) -> None:
        super().clean()
        if self.user_id and self.user.role != UserRole.INSTRUCTOR:
            raise ValidationError({"user": "O usuário vinculado deve possuir perfil instrutor."})

    def __str__(self) -> str:
        return self.user.full_name


class Institution(UUIDTimestampedModel):
    name = models.CharField("nome", max_length=150)
    document = models.CharField(
        "CNPJ",
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_cnpj],
    )
    contact_name = models.CharField("pessoa de contato", max_length=150, blank=True)
    contact_email = models.EmailField("e-mail de contato", blank=True)
    contact_phone = models.CharField(
        "telefone de contato",
        max_length=11,
        blank=True,
        validators=[validate_phone],
    )
    address = models.CharField("endereço", max_length=255, blank=True)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        verbose_name = "instituição parceira"
        verbose_name_plural = "instituições parceiras"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.document = only_digits(self.document) or None
        self.contact_phone = only_digits(self.contact_phone)
        super().save(*args, **kwargs)

    @property
    def formatted_contact_phone(self) -> str:
        return format_phone(self.contact_phone) if self.contact_phone else "—"

    def __str__(self) -> str:
        return self.name
