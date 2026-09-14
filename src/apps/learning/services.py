from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus, EnrollmentStatusHistory
from apps.people.models import Instructor
from apps.workshops.models import ClassGroup, ClassGroupStatus, Meeting, MeetingStatus
from apps.workshops.services import transition_class_group

from .models import Attendance, AttendanceStatus, Evaluation, StudentProject

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


@dataclass(frozen=True)
class CompletionSummary:
    approved: int
    not_completed: int


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


def _validate_learning_actor(actor: User, class_group_id) -> None:
    if not user_can_manage_class_attendance(actor, class_group_id):
        raise PermissionDenied("Você não pode acompanhar participantes desta turma.")


def _validate_active_enrollment(enrollment: Enrollment) -> None:
    if enrollment.status != EnrollmentStatus.CONFIRMED:
        raise ValidationError("Somente inscrições confirmadas aceitam registros acadêmicos.")
    if enrollment.class_group.status != ClassGroupStatus.IN_PROGRESS:
        raise ValidationError("Os registros acadêmicos só podem ser alterados durante a turma.")


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


@transaction.atomic
def save_student_project(
    enrollment: Enrollment,
    *,
    data: dict,
    actor: User,
) -> StudentProject:
    locked_enrollment = (
        Enrollment.objects.select_for_update()
        .select_related("participant", "class_group")
        .get(pk=enrollment.pk)
    )
    if actor.role != UserRole.PARTICIPANT or locked_enrollment.participant.user_id != actor.pk:
        raise PermissionDenied("Você só pode registrar seu próprio projeto.")
    _validate_active_enrollment(locked_enrollment)

    delivered = bool(data.get("is_delivered"))
    project, _ = StudentProject.objects.select_for_update().get_or_create(
        enrollment=locked_enrollment,
        defaults={
            "title": data["title"].strip(),
            "description": data["description"].strip(),
        },
    )
    was_delivered = project.is_delivered
    project.title = data["title"].strip()
    project.description = data["description"].strip()
    project.repository_url = data.get("repository_url", "").strip()
    project.demonstration_url = data.get("demonstration_url", "").strip()
    project.is_delivered = delivered
    if delivered and not was_delivered:
        project.delivered_at = timezone.now()
    elif not delivered:
        project.delivered_at = None
    project.full_clean()
    project.save()
    return project


@transaction.atomic
def review_student_project(
    project: StudentProject,
    *,
    review_notes: str,
    actor: User,
) -> StudentProject:
    locked_project = (
        StudentProject.objects.select_for_update()
        .select_related("enrollment__class_group")
        .get(pk=project.pk)
    )
    _validate_learning_actor(actor, locked_project.enrollment.class_group_id)
    _validate_active_enrollment(locked_project.enrollment)
    locked_project.review_notes = review_notes.strip()
    locked_project.save(update_fields=["review_notes", "updated_at"])
    return locked_project


@transaction.atomic
def save_evaluation(
    enrollment: Enrollment,
    *,
    final_score: Decimal,
    feedback: str,
    publish: bool,
    actor: User,
) -> Evaluation:
    locked_enrollment = (
        Enrollment.objects.select_for_update().select_related("class_group").get(pk=enrollment.pk)
    )
    _validate_learning_actor(actor, locked_enrollment.class_group_id)
    _validate_active_enrollment(locked_enrollment)
    evaluation, _ = Evaluation.objects.select_for_update().get_or_create(
        enrollment=locked_enrollment,
        defaults={
            "final_score": final_score,
            "feedback": feedback.strip(),
            "evaluated_by": actor,
        },
    )
    evaluation.final_score = final_score
    evaluation.feedback = feedback.strip()
    evaluation.evaluated_by = actor
    if publish and not evaluation.published_at:
        evaluation.published_at = timezone.now()
    elif not publish:
        evaluation.published_at = None
    evaluation.full_clean()
    evaluation.save()
    return evaluation


def _non_completion_reasons(
    *,
    attendance: AttendanceSummary,
    evaluation: Evaluation,
    project: StudentProject | None,
) -> list[str]:
    reasons = []
    if attendance.percentage < MINIMUM_ATTENDANCE_PERCENTAGE:
        reasons.append(f"frequência mínima de 75% (obtida {attendance.percentage}%)")
    if evaluation.final_score < Decimal("6.0"):
        reasons.append(f"nota mínima 6,0 (obtida {evaluation.final_score})")
    if not project or not project.is_delivered:
        reasons.append("projeto entregue")
    return reasons


@transaction.atomic
def complete_class_group(class_group: ClassGroup, *, actor: User) -> CompletionSummary:
    if actor.role != UserRole.ADMIN:
        raise PermissionDenied("Somente administradores podem concluir turmas.")
    current = ClassGroup.objects.select_for_update().get(pk=class_group.pk)
    if current.status != ClassGroupStatus.IN_PROGRESS:
        raise ValidationError("Somente turmas em andamento podem ser concluídas.")

    meetings = list(
        Meeting.objects.select_for_update()
        .filter(class_group=current)
        .exclude(status=MeetingStatus.CANCELLED)
    )
    if not meetings:
        raise ValidationError("A turma precisa possuir ao menos um encontro realizado.")
    if any(
        meeting.status != MeetingStatus.COMPLETED or meeting.ends_at > timezone.now()
        for meeting in meetings
    ):
        raise ValidationError("Processe todos os encontros não cancelados antes da conclusão.")

    enrollments = list(
        Enrollment.objects.select_for_update()
        .filter(class_group=current, status=EnrollmentStatus.CONFIRMED)
        .select_related("participant")
    )
    if not enrollments:
        raise ValidationError("A turma não possui inscrições confirmadas para concluir.")
    evaluations = {
        evaluation.enrollment_id: evaluation
        for evaluation in Evaluation.objects.select_for_update().filter(enrollment__in=enrollments)
    }
    projects = {
        project.enrollment_id: project
        for project in StudentProject.objects.select_for_update().filter(enrollment__in=enrollments)
    }
    missing_evaluations = [
        enrollment.participant.full_name
        for enrollment in enrollments
        if enrollment.pk not in evaluations
    ]
    if missing_evaluations:
        raise ValidationError(
            "Registre a avaliação final de todos os participantes antes da conclusão: "
            + ", ".join(missing_evaluations)
            + "."
        )

    approved = 0
    not_completed = 0
    for enrollment in enrollments:
        reasons = _non_completion_reasons(
            attendance=calculate_attendance_summary(enrollment),
            evaluation=evaluations[enrollment.pk],
            project=projects.get(enrollment.pk),
        )
        target = EnrollmentStatus.NOT_COMPLETED if reasons else EnrollmentStatus.APPROVED
        reason = "Critérios não atendidos: " + "; ".join(reasons) + "." if reasons else ""
        enrollment.status = target
        enrollment.status_reason = reason
        enrollment.save(update_fields=["status", "status_reason", "updated_at"])
        EnrollmentStatusHistory.objects.create(
            enrollment=enrollment,
            from_status=EnrollmentStatus.CONFIRMED,
            to_status=target,
            reason=reason,
            changed_by=actor,
        )
        if target == EnrollmentStatus.APPROVED:
            approved += 1
        else:
            not_completed += 1

    transition_class_group(
        current,
        ClassGroupStatus.COMPLETED,
        academic_completion_validated=True,
    )
    return CompletionSummary(approved=approved, not_completed=not_completed)
