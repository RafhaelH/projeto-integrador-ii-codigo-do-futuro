import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import UUIDTimestampedModel
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.workshops.models import Meeting


class AttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Presente"
    ABSENT = "ABSENT", "Ausente"
    JUSTIFIED = "JUSTIFIED", "Falta justificada"


class Attendance(UUIDTimestampedModel):
    enrollment = models.ForeignKey(
        Enrollment,
        verbose_name="inscrição",
        related_name="attendances",
        on_delete=models.PROTECT,
    )
    meeting = models.ForeignKey(
        Meeting,
        verbose_name="encontro",
        related_name="attendances",
        on_delete=models.PROTECT,
    )
    status = models.CharField("situação", max_length=20, choices=AttendanceStatus.choices)
    note = models.CharField("justificativa ou observação", max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="registrada por",
        related_name="recorded_attendances",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "frequência"
        verbose_name_plural = "frequências"
        ordering = ["meeting__starts_at", "enrollment__participant__full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "meeting"],
                name="learning_attendance_enrollment_meeting_unique",
            )
        ]
        indexes = [
            models.Index(
                fields=["enrollment", "status"],
                name="learning_att_enrollment_idx",
            ),
            models.Index(
                fields=["meeting", "status"],
                name="learning_att_meeting_idx",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if (
            self.enrollment_id
            and self.meeting_id
            and self.enrollment.class_group_id != self.meeting.class_group_id
        ):
            raise ValidationError(
                {"meeting": "O encontro e a inscrição devem pertencer à mesma turma."}
            )

    def __str__(self) -> str:
        return f"{self.enrollment.participant} — {self.meeting.title}"


class StudentProject(UUIDTimestampedModel):
    enrollment = models.OneToOneField(
        Enrollment,
        verbose_name="inscrição",
        related_name="student_project",
        on_delete=models.PROTECT,
    )
    title = models.CharField("título", max_length=150)
    description = models.TextField("descrição")
    repository_url = models.URLField("repositório", blank=True)
    demonstration_url = models.URLField("demonstração", blank=True)
    is_delivered = models.BooleanField("entregue", default=False)
    delivered_at = models.DateTimeField("entregue em", null=True, blank=True)
    review_notes = models.TextField("devolutiva", blank=True)

    class Meta:
        verbose_name = "projeto do participante"
        verbose_name_plural = "projetos dos participantes"
        ordering = ["enrollment__participant__full_name"]

    def clean(self) -> None:
        super().clean()
        if self.is_delivered and not self.delivered_at:
            raise ValidationError({"delivered_at": "Informe quando o projeto foi entregue."})
        if not self.is_delivered and self.delivered_at:
            raise ValidationError(
                {"delivered_at": "Um projeto não entregue não pode ter data de entrega."}
            )

    def __str__(self) -> str:
        return f"{self.title} — {self.enrollment.participant}"


class Evaluation(UUIDTimestampedModel):
    enrollment = models.OneToOneField(
        Enrollment,
        verbose_name="inscrição",
        related_name="evaluation",
        on_delete=models.PROTECT,
    )
    final_score = models.DecimalField(
        "nota final",
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    feedback = models.TextField("devolutiva")
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="avaliada por",
        related_name="recorded_evaluations",
        on_delete=models.PROTECT,
    )
    published_at = models.DateTimeField("publicada em", null=True, blank=True)

    class Meta:
        verbose_name = "avaliação final"
        verbose_name_plural = "avaliações finais"
        ordering = ["enrollment__participant__full_name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(final_score__gte=0, final_score__lte=10),
                name="learning_evaluation_score_range",
            )
        ]

    def __str__(self) -> str:
        return f"{self.enrollment.participant} — {self.final_score}"


def generate_certificate_code() -> str:
    return f"CDF-{uuid.uuid4().hex.upper()}"


class Certificate(UUIDTimestampedModel):
    enrollment = models.OneToOneField(
        Enrollment,
        verbose_name="inscrição",
        related_name="certificate",
        on_delete=models.PROTECT,
    )
    verification_code = models.CharField(
        "código de identificação",
        max_length=40,
        unique=True,
        default=generate_certificate_code,
        editable=False,
    )
    issued_at = models.DateTimeField("emitido em", default=timezone.now)
    workload_hours = models.DecimalField(
        "carga horária",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField("ativo", default=True)
    revoked_at = models.DateTimeField("revogado em", null=True, blank=True)
    revocation_reason = models.TextField("motivo da revogação", blank=True)

    class Meta:
        verbose_name = "certificado"
        verbose_name_plural = "certificados"
        ordering = ["-issued_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        is_active=True,
                        revoked_at__isnull=True,
                        revocation_reason="",
                    )
                    | (
                        models.Q(is_active=False, revoked_at__isnull=False)
                        & ~models.Q(revocation_reason="")
                    )
                ),
                name="learning_certificate_revocation_state",
            )
        ]

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.enrollment_id and self.enrollment.status != EnrollmentStatus.APPROVED:
            errors["enrollment"] = "Somente uma inscrição aprovada pode receber certificado."
        if self.is_active and (self.revoked_at or self.revocation_reason.strip()):
            errors["is_active"] = "Um certificado ativo não pode possuir dados de revogação."
        if not self.is_active:
            if not self.revoked_at:
                errors["revoked_at"] = "Informe quando o certificado foi revogado."
            if not self.revocation_reason.strip():
                errors["revocation_reason"] = "Informe o motivo da revogação."
        if errors:
            raise ValidationError(errors)

    def delete(self, *args, **kwargs):
        raise ValidationError("Certificados devem ser revogados, não excluídos.")

    def __str__(self) -> str:
        return f"{self.enrollment.participant} — {self.verification_code}"
