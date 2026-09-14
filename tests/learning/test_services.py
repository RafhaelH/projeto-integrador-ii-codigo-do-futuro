from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.enrollments.models import EnrollmentStatus
from apps.learning.models import Attendance, AttendanceStatus
from apps.learning.services import calculate_attendance_summary, record_meeting_attendance
from apps.workshops.models import Meeting, MeetingStatus

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
