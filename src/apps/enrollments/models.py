from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import UUIDTimestampedModel
from apps.people.models import Participant
from apps.workshops.models import ClassGroup


class EnrollmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pendente"
    CONFIRMED = "CONFIRMED", "Confirmada"
    WAITLISTED = "WAITLISTED", "Lista de espera"
    REJECTED = "REJECTED", "Rejeitada"
    CANCELLED = "CANCELLED", "Cancelada"
    APPROVED = "APPROVED", "Aprovada"
    NOT_COMPLETED = "NOT_COMPLETED", "Não concluída"


class Enrollment(UUIDTimestampedModel):
    participant = models.ForeignKey(
        Participant,
        verbose_name="participante",
        related_name="enrollments",
        on_delete=models.PROTECT,
    )
    class_group = models.ForeignKey(
        ClassGroup,
        verbose_name="turma",
        related_name="enrollments",
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        "situação",
        max_length=30,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDING,
    )
    status_reason = models.TextField("motivo da situação", blank=True)
    waitlisted_at = models.DateTimeField("entrada na lista de espera", null=True, blank=True)
    confirmed_at = models.DateTimeField("confirmação", null=True, blank=True)
    cancelled_at = models.DateTimeField("cancelamento", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="registrada por",
        related_name="created_enrollments",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "inscrição"
        verbose_name_plural = "inscrições"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "class_group"],
                name="enrollments_participant_class_unique",
            )
        ]
        indexes = [
            models.Index(
                fields=["class_group", "status", "created_at"],
                name="enrollments_class_status_idx",
            ),
            models.Index(
                fields=["class_group", "status", "waitlisted_at"],
                name="enrollments_waitlist_idx",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.status == EnrollmentStatus.REJECTED and not self.status_reason.strip():
            raise ValidationError({"status_reason": "Informe o motivo da rejeição."})

    def delete(self, *args, **kwargs):
        if self.status != EnrollmentStatus.PENDING:
            raise ValidationError("Uma inscrição processada não pode ser excluída.")
        return super().delete(*args, **kwargs)

    @property
    def waitlist_position(self) -> int | None:
        if self.status != EnrollmentStatus.WAITLISTED or not self.waitlisted_at:
            return None
        return (
            Enrollment.objects.filter(
                class_group=self.class_group,
                status=EnrollmentStatus.WAITLISTED,
            )
            .filter(
                Q(waitlisted_at__lt=self.waitlisted_at)
                | Q(waitlisted_at=self.waitlisted_at, created_at__lt=self.created_at)
                | Q(
                    waitlisted_at=self.waitlisted_at,
                    created_at=self.created_at,
                    pk__lt=self.pk,
                )
            )
            .count()
            + 1
        )

    def __str__(self) -> str:
        return f"{self.participant} — {self.class_group.code}"


class EnrollmentStatusHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    enrollment = models.ForeignKey(
        Enrollment,
        verbose_name="inscrição",
        related_name="status_history",
        on_delete=models.CASCADE,
    )
    from_status = models.CharField(
        "situação anterior",
        max_length=30,
        choices=EnrollmentStatus.choices,
        null=True,
        blank=True,
    )
    to_status = models.CharField("nova situação", max_length=30, choices=EnrollmentStatus.choices)
    reason = models.TextField("motivo", blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="alterada por",
        related_name="enrollment_status_changes",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField("alterada em", auto_now_add=True)

    class Meta:
        verbose_name = "histórico da inscrição"
        verbose_name_plural = "históricos das inscrições"
        ordering = ["created_at", "pk"]

    def __str__(self) -> str:
        return f"{self.enrollment}: {self.get_to_status_display()}"
