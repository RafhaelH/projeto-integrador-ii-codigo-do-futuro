from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.learning.models import (
    Attendance,
    AttendanceStatus,
    Certificate,
    Evaluation,
    StudentProject,
)
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


def test_only_one_project_is_allowed_per_enrollment(confirmed_enrollment):
    StudentProject.objects.create(
        enrollment=confirmed_enrollment,
        title="Portfólio",
        description="Página pessoal.",
    )

    with pytest.raises(IntegrityError):
        StudentProject.objects.create(
            enrollment=confirmed_enrollment,
            title="Segundo projeto",
            description="Não permitido no MVP.",
        )


def test_delivered_project_requires_delivery_date(confirmed_enrollment):
    project = StudentProject(
        enrollment=confirmed_enrollment,
        title="Portfólio",
        description="Página pessoal.",
        is_delivered=True,
    )

    with pytest.raises(ValidationError, match="quando"):
        project.full_clean()


def test_evaluation_rejects_score_above_ten(confirmed_enrollment, admin_user):
    evaluation = Evaluation(
        enrollment=confirmed_enrollment,
        final_score="10.1",
        feedback="Boa evolução.",
        evaluated_by=admin_user,
    )

    with pytest.raises(ValidationError):
        evaluation.full_clean()


def test_certificate_is_unique_per_enrollment(confirmed_enrollment):
    confirmed_enrollment.status = "APPROVED"
    confirmed_enrollment.save(update_fields=["status", "updated_at"])
    Certificate.objects.create(
        enrollment=confirmed_enrollment,
        workload_hours="2.00",
    )

    with pytest.raises(IntegrityError):
        Certificate.objects.create(
            enrollment=confirmed_enrollment,
            workload_hours="2.00",
        )


def test_certificate_rejects_non_approved_enrollment(confirmed_enrollment):
    certificate = Certificate(
        enrollment=confirmed_enrollment,
        workload_hours="2.00",
    )

    with pytest.raises(ValidationError, match="aprovada"):
        certificate.full_clean()


def test_active_certificate_rejects_revocation_data(confirmed_enrollment):
    confirmed_enrollment.status = "APPROVED"
    confirmed_enrollment.save(update_fields=["status", "updated_at"])
    certificate = Certificate(
        enrollment=confirmed_enrollment,
        workload_hours="2.00",
        revocation_reason="Dados incorretos.",
    )

    with pytest.raises(ValidationError, match="ativo"):
        certificate.full_clean()
