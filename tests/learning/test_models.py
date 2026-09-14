from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.learning.models import Attendance, AttendanceStatus
from apps.workshops.models import ClassGroup, Meeting

pytestmark = pytest.mark.django_db


def test_attendance_is_unique_per_enrollment_and_meeting(
    confirmed_enrollment, past_meeting, admin_user
):
    Attendance.objects.create(
        enrollment=confirmed_enrollment,
        meeting=past_meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )

    with pytest.raises(IntegrityError):
        Attendance.objects.create(
            enrollment=confirmed_enrollment,
            meeting=past_meeting,
            status=AttendanceStatus.ABSENT,
            recorded_by=admin_user,
        )


def test_attendance_requires_enrollment_and_meeting_from_same_class(
    confirmed_enrollment, learning_class, learning_workshop, admin_user
):
    other_class = ClassGroup.objects.create(
        workshop=learning_workshop,
        code="CDF-FREQ-OTHER",
        title="Outra turma",
        location="Escola",
        capacity=10,
        registration_opens_at=learning_class.registration_opens_at,
        registration_closes_at=learning_class.registration_closes_at,
        start_date=learning_class.start_date,
        end_date=learning_class.end_date,
        created_by=admin_user,
    )
    end = timezone.now() - timedelta(days=1)
    meeting = Meeting.objects.create(
        class_group=other_class,
        title="Outro encontro",
        starts_at=end - timedelta(hours=2),
        ends_at=end,
    )
    attendance = Attendance(
        enrollment=confirmed_enrollment,
        meeting=meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )

    with pytest.raises(ValidationError, match="mesma turma"):
        attendance.full_clean()


def test_attendance_string_identifies_participant_and_meeting(
    confirmed_enrollment, past_meeting, admin_user
):
    attendance = Attendance.objects.create(
        enrollment=confirmed_enrollment,
        meeting=past_meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )

    assert confirmed_enrollment.participant.full_name in str(attendance)
    assert past_meeting.title in str(attendance)
