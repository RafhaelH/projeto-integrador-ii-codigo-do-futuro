from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.enrollments.models import EnrollmentStatus
from apps.learning.models import (
    Attendance,
    AttendanceStatus,
    Certificate,
    Evaluation,
    StudentProject,
)
from apps.learning.services import (
    calculate_attendance_summary,
    calculate_certificate_workload,
    complete_class_group,
    issue_certificate,
    record_meeting_attendance,
    revoke_certificate,
    review_student_project,
    save_evaluation,
    save_student_project,
)
from apps.workshops.models import ClassGroupStatus, Meeting, MeetingStatus

pytestmark = pytest.mark.django_db


def attendance_records(*enrollments, status=AttendanceStatus.PRESENT):
    return {str(enrollment.pk): {"status": status, "note": ""} for enrollment in enrollments}


def test_admin_records_complete_call_and_marks_meeting_completed(
    confirmed_enrollment, second_confirmed_enrollment, past_meeting, admin_user
):
    saved = record_meeting_attendance(
        past_meeting,
        records=attendance_records(confirmed_enrollment, second_confirmed_enrollment),
        actor=admin_user,
    )
    past_meeting.refresh_from_db()

    assert len(saved) == 2
    assert past_meeting.status == MeetingStatus.COMPLETED
    assert Attendance.objects.filter(meeting=past_meeting).count() == 2
    assert {attendance.recorded_by for attendance in saved} == {admin_user}


def test_correction_updates_existing_record_and_authorship(
    confirmed_enrollment, past_meeting, admin_user, assigned_instructor
):
    record_meeting_attendance(
        past_meeting,
        records=attendance_records(confirmed_enrollment, status=AttendanceStatus.ABSENT),
        actor=admin_user,
    )

    corrected = record_meeting_attendance(
        past_meeting,
        records={
            str(confirmed_enrollment.pk): {
                "status": AttendanceStatus.JUSTIFIED,
                "note": "Atestado apresentado.",
            }
        },
        actor=assigned_instructor.user,
    )[0]

    assert Attendance.objects.filter(meeting=past_meeting).count() == 1
    assert corrected.status == AttendanceStatus.JUSTIFIED
    assert corrected.note == "Atestado apresentado."
    assert corrected.recorded_by == assigned_instructor.user


def test_unassigned_instructor_cannot_record_call(
    confirmed_enrollment, past_meeting, instructor_user
):
    with pytest.raises(PermissionDenied):
        record_meeting_attendance(
            past_meeting,
            records=attendance_records(confirmed_enrollment),
            actor=instructor_user,
        )


def test_future_meeting_rejects_call(confirmed_enrollment, learning_class, admin_user):
    starts = timezone.now() + timedelta(days=1)
    meeting = Meeting.objects.create(
        class_group=learning_class,
        title="Encontro futuro",
        starts_at=starts,
        ends_at=starts + timedelta(hours=2),
    )

    with pytest.raises(ValidationError, match="após o término"):
        record_meeting_attendance(
            meeting,
            records=attendance_records(confirmed_enrollment),
            actor=admin_user,
        )


def test_cancelled_meeting_rejects_call(confirmed_enrollment, past_meeting, admin_user):
    past_meeting.status = MeetingStatus.CANCELLED
    past_meeting.save()

    with pytest.raises(ValidationError, match="cancelado"):
        record_meeting_attendance(
            past_meeting,
            records=attendance_records(confirmed_enrollment),
            actor=admin_user,
        )


def test_call_requires_every_confirmed_participant(
    confirmed_enrollment, second_confirmed_enrollment, past_meeting, admin_user
):
    with pytest.raises(ValidationError, match="todos os participantes"):
        record_meeting_attendance(
            past_meeting,
            records=attendance_records(confirmed_enrollment),
            actor=admin_user,
        )


def test_call_requires_confirmed_participants(confirmed_enrollment, past_meeting, admin_user):
    confirmed_enrollment.status = EnrollmentStatus.CANCELLED
    confirmed_enrollment.save()

    with pytest.raises(ValidationError, match="não possui participantes"):
        record_meeting_attendance(past_meeting, records={}, actor=admin_user)


def test_invalid_attendance_status_is_rejected(confirmed_enrollment, past_meeting, admin_user):
    with pytest.raises(ValidationError, match="situação de frequência inválida"):
        record_meeting_attendance(
            past_meeting,
            records={str(confirmed_enrollment.pk): {"status": "UNKNOWN", "note": ""}},
            actor=admin_user,
        )


def test_six_presences_in_eight_completed_meetings_equals_seventy_five_percent(
    confirmed_enrollment, learning_class, admin_user
):
    statuses = [AttendanceStatus.PRESENT] * 6 + [
        AttendanceStatus.ABSENT,
        AttendanceStatus.JUSTIFIED,
    ]
    for index, status in enumerate(statuses, start=1):
        end = timezone.now() - timedelta(days=index)
        meeting = Meeting.objects.create(
            class_group=learning_class,
            title=f"Encontro {index}",
            starts_at=end - timedelta(hours=2),
            ends_at=end,
            status=MeetingStatus.COMPLETED,
        )
        Attendance.objects.create(
            enrollment=confirmed_enrollment,
            meeting=meeting,
            status=status,
            recorded_by=admin_user,
        )

    summary = calculate_attendance_summary(confirmed_enrollment)

    assert summary.completed_meetings == 8
    assert summary.presents == 6
    assert summary.absences == 1
    assert summary.justified_absences == 1
    assert summary.percentage == Decimal("75.00")


def test_frequency_without_completed_meetings_is_zero(confirmed_enrollment):
    summary = calculate_attendance_summary(confirmed_enrollment)

    assert summary.completed_meetings == 0
    assert summary.percentage == Decimal("0.00")


def test_participant_creates_and_delivers_own_project(confirmed_enrollment):
    project = save_student_project(
        confirmed_enrollment,
        data={
            "title": "  Meu portfólio  ",
            "description": "  Página com meus projetos.  ",
            "repository_url": "https://github.com/exemplo/portfolio",
            "demonstration_url": "",
            "is_delivered": True,
        },
        actor=confirmed_enrollment.participant.user,
    )

    assert project.title == "Meu portfólio"
    assert project.delivered_at is not None
    assert project.is_delivered is True


def test_participant_cannot_change_another_project(
    confirmed_enrollment, second_confirmed_enrollment
):
    with pytest.raises(PermissionDenied, match="próprio projeto"):
        save_student_project(
            confirmed_enrollment,
            data={"title": "X", "description": "Y", "is_delivered": False},
            actor=second_confirmed_enrollment.participant.user,
        )


def test_assigned_instructor_reviews_project(confirmed_enrollment, assigned_instructor):
    project = StudentProject.objects.create(
        enrollment=confirmed_enrollment,
        title="Robô virtual",
        description="Automação educacional.",
    )

    reviewed = review_student_project(
        project,
        review_notes="  Explique melhor o público-alvo.  ",
        actor=assigned_instructor.user,
    )

    assert reviewed.review_notes == "Explique melhor o público-alvo."


def test_evaluation_records_author_and_publication(confirmed_enrollment, assigned_instructor):
    evaluation = save_evaluation(
        confirmed_enrollment,
        final_score=Decimal("8.5"),
        feedback="Ótima evolução.",
        publish=True,
        actor=assigned_instructor.user,
    )

    assert evaluation.evaluated_by == assigned_instructor.user
    assert evaluation.published_at is not None


def test_unassigned_instructor_cannot_evaluate(confirmed_enrollment, instructor_user):
    with pytest.raises(PermissionDenied):
        save_evaluation(
            confirmed_enrollment,
            final_score=Decimal("8.0"),
            feedback="Não autorizado.",
            publish=False,
            actor=instructor_user,
        )


def test_completion_approves_only_participant_who_meets_all_criteria(
    confirmed_enrollment,
    second_confirmed_enrollment,
    past_meeting,
    admin_user,
):
    past_meeting.status = MeetingStatus.COMPLETED
    past_meeting.save()
    Attendance.objects.create(
        enrollment=confirmed_enrollment,
        meeting=past_meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )
    StudentProject.objects.create(
        enrollment=confirmed_enrollment,
        title="Projeto entregue",
        description="Solução completa.",
        is_delivered=True,
        delivered_at=timezone.now(),
    )
    Evaluation.objects.create(
        enrollment=confirmed_enrollment,
        final_score=Decimal("6.0"),
        feedback="Aprovado.",
        evaluated_by=admin_user,
    )
    Evaluation.objects.create(
        enrollment=second_confirmed_enrollment,
        final_score=Decimal("5.0"),
        feedback="Critérios pendentes.",
        evaluated_by=admin_user,
    )

    result = complete_class_group(confirmed_enrollment.class_group, actor=admin_user)
    confirmed_enrollment.refresh_from_db()
    second_confirmed_enrollment.refresh_from_db()
    confirmed_enrollment.class_group.refresh_from_db()

    assert result.approved == 1
    assert result.not_completed == 1
    assert confirmed_enrollment.status == EnrollmentStatus.APPROVED
    assert second_confirmed_enrollment.status == EnrollmentStatus.NOT_COMPLETED
    assert "frequência mínima" in second_confirmed_enrollment.status_reason
    assert "nota mínima" in second_confirmed_enrollment.status_reason
    assert "projeto entregue" in second_confirmed_enrollment.status_reason
    assert confirmed_enrollment.class_group.status == ClassGroupStatus.COMPLETED
    assert confirmed_enrollment.status_history.filter(
        to_status=EnrollmentStatus.APPROVED,
        changed_by=admin_user,
    ).exists()


def test_completion_requires_all_meetings_processed(confirmed_enrollment, past_meeting, admin_user):
    Evaluation.objects.create(
        enrollment=confirmed_enrollment,
        final_score=Decimal("8.0"),
        feedback="Bom trabalho.",
        evaluated_by=admin_user,
    )

    with pytest.raises(ValidationError, match="todos os encontros"):
        complete_class_group(confirmed_enrollment.class_group, actor=admin_user)


def test_completion_requires_every_final_evaluation(confirmed_enrollment, past_meeting, admin_user):
    past_meeting.status = MeetingStatus.COMPLETED
    past_meeting.save()

    with pytest.raises(ValidationError, match="avaliação final"):
        complete_class_group(confirmed_enrollment.class_group, actor=admin_user)

    confirmed_enrollment.refresh_from_db()
    assert confirmed_enrollment.status == EnrollmentStatus.CONFIRMED



def prepare_approved_enrollment(enrollment, meeting):
    enrollment.status = EnrollmentStatus.APPROVED
    enrollment.save(update_fields=["status", "updated_at"])
    meeting.status = MeetingStatus.COMPLETED
    meeting.save(update_fields=["status", "updated_at"])


def test_certificate_workload_sums_completed_meetings(confirmed_enrollment, past_meeting):
    prepare_approved_enrollment(confirmed_enrollment, past_meeting)

    assert calculate_certificate_workload(confirmed_enrollment) == Decimal("2.00")


def test_admin_issues_certificate_for_approved_enrollment(
    confirmed_enrollment,
    past_meeting,
    admin_user,
):
    prepare_approved_enrollment(confirmed_enrollment, past_meeting)

    certificate = issue_certificate(confirmed_enrollment, actor=admin_user)

    assert certificate.enrollment == confirmed_enrollment
    assert certificate.workload_hours == Decimal("2.00")
    assert certificate.verification_code.startswith("CDF-")
    assert certificate.is_active


def test_certificate_issue_is_idempotent(confirmed_enrollment, past_meeting, admin_user):
    prepare_approved_enrollment(confirmed_enrollment, past_meeting)

    first = issue_certificate(confirmed_enrollment, actor=admin_user)
    second = issue_certificate(confirmed_enrollment, actor=admin_user)

    assert first.pk == second.pk
    assert Certificate.objects.count() == 1


def test_non_approved_enrollment_cannot_receive_certificate(
    confirmed_enrollment,
    admin_user,
):
    with pytest.raises(ValidationError, match="aprovadas"):
        issue_certificate(confirmed_enrollment, actor=admin_user)


def test_instructor_cannot_issue_certificate(
    confirmed_enrollment,
    past_meeting,
    assigned_instructor,
):
    prepare_approved_enrollment(confirmed_enrollment, past_meeting)

    with pytest.raises(PermissionDenied, match="administradores"):
        issue_certificate(
            confirmed_enrollment,
            actor=assigned_instructor.user,
        )


def test_admin_revokes_certificate(
    confirmed_enrollment,
    past_meeting,
    admin_user,
):
    prepare_approved_enrollment(confirmed_enrollment, past_meeting)
    certificate = issue_certificate(confirmed_enrollment, actor=admin_user)

    revoked = revoke_certificate(
        certificate,
        reason="Nome corrigido no cadastro.",
        actor=admin_user,
    )

    assert not revoked.is_active
    assert revoked.revoked_at is not None
    assert revoked.revocation_reason == "Nome corrigido no cadastro."


def test_revocation_requires_reason(confirmed_enrollment, past_meeting, admin_user):
    prepare_approved_enrollment(confirmed_enrollment, past_meeting)
    certificate = issue_certificate(confirmed_enrollment, actor=admin_user)

    with pytest.raises(ValidationError, match="motivo"):
        revoke_certificate(certificate, reason="  ", actor=admin_user)
