from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.people.models import Instructor
from apps.workshops.models import Meeting, MeetingStatus

from .models import Attendance, AttendanceStatus

MINIMUM_ATTENDANCE_PERCENTAGE = Decimal("75.00")
ACADEMIC_ENROLLMENT_STATUSES = (
    EnrollmentStatus.CONFIRMED,
    EnrollmentStatus.APPROVED,
    EnrollmentStatus.NOT_COMPLETED,
)


@dataclass(frozen=True)
class AttendanceSummary:
    completed_meetings: int
    presents: int
    absences: int
    justified_absences: int
    percentage: Decimal


def user_can_manage_class_attendance(user: User, class_group_id) -> bool:
    if user.role == UserRole.ADMIN:
        return True
    return (
        user.role == UserRole.INSTRUCTOR
        and Instructor.objects.filter(
            user=user,
            is_active=True,
            class_links__class_group_id=class_group_id,
        ).exists()
    )


def _validate_attendance_actor(actor: User, meeting: Meeting) -> None:
    if not user_can_manage_class_attendance(actor, meeting.class_group_id):
        raise PermissionDenied("Você não pode registrar frequência nesta turma.")


def _validate_meeting_for_attendance(meeting: Meeting) -> None:
    if meeting.status == MeetingStatus.CANCELLED:
        raise ValidationError("Um encontro cancelado não aceita chamada.")
    if meeting.ends_at > timezone.now():
        raise ValidationError("A chamada só pode ser registrada após o término do encontro.")


@transaction.atomic
def record_meeting_attendance(
    meeting: Meeting,
    *,
    records: dict,
    actor: User,
) -> list[Attendance]:
    locked_meeting = (
        Meeting.objects.select_for_update().select_related("class_group").get(pk=meeting.pk)
    )
    _validate_attendance_actor(actor, locked_meeting)
    _validate_meeting_for_attendance(locked_meeting)

    enrollments = list(
        Enrollment.objects.select_for_update()
        .filter(
            class_group=locked_meeting.class_group,
            status__in=ACADEMIC_ENROLLMENT_STATUSES,
        )
        .select_related("participant")
        .order_by("participant__full_name")
    )
    if not enrollments:
        raise ValidationError("A turma não possui participantes confirmados para a chamada.")

    normalized_records = {str(enrollment_id): data for enrollment_id, data in records.items()}
    expected_ids = {str(enrollment.pk) for enrollment in enrollments}
    provided_ids = set(normalized_records)
    if provided_ids != expected_ids:
        raise ValidationError("Registre a situação de todos os participantes confirmados.")

    saved = []
    valid_statuses = set(AttendanceStatus.values)
    for enrollment in enrollments:
        data = normalized_records[str(enrollment.pk)]
        status = data["status"]
        if status not in valid_statuses:
            raise ValidationError("Existe uma situação de frequência inválida.")
        attendance, _ = Attendance.objects.update_or_create(
            enrollment=enrollment,
            meeting=locked_meeting,
            defaults={
                "status": status,
                "note": data.get("note", "").strip(),
                "recorded_by": actor,
            },
        )
        saved.append(attendance)

    if locked_meeting.status != MeetingStatus.COMPLETED:
        locked_meeting.status = MeetingStatus.COMPLETED
        locked_meeting.save(update_fields=["status", "updated_at"])
    return saved


def calculate_attendance_summary(
    enrollment: Enrollment,
    *,
    reference_time=None,
) -> AttendanceSummary:
    reference_time = reference_time or timezone.now()
    completed_meetings = enrollment.class_group.meetings.filter(
        status=MeetingStatus.COMPLETED,
        ends_at__lte=reference_time,
    ).count()
    attendances = enrollment.attendances.filter(
        meeting__status=MeetingStatus.COMPLETED,
        meeting__ends_at__lte=reference_time,
    )
    presents = attendances.filter(status=AttendanceStatus.PRESENT).count()
    absences = attendances.filter(status=AttendanceStatus.ABSENT).count()
    justified = attendances.filter(status=AttendanceStatus.JUSTIFIED).count()
    percentage = (
        (Decimal(presents) / Decimal(completed_meetings) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if completed_meetings
        else Decimal("0.00")
    )
    return AttendanceSummary(
        completed_meetings=completed_meetings,
        presents=presents,
        absences=absences,
        justified_absences=justified,
        percentage=percentage,
    )
