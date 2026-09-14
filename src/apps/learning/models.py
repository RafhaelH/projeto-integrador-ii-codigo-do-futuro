from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import UUIDTimestampedModel
from apps.enrollments.models import Enrollment
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
