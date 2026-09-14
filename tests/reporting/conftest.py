from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.learning.models import Attendance, AttendanceStatus, Evaluation, StudentProject
from apps.people.models import Instructor, Participant
from apps.workshops.models import (
    ClassGroup,
    ClassGroupStatus,
    ClassInstructor,
    Meeting,
    MeetingStatus,
    Workshop,
    WorkshopStatus,
)


@pytest.fixture
def reporting_workshop(db, admin_user):
    return Workshop.objects.create(
        title="Programação com Python",
        slug="programacao-python-relatorios",
        summary="Fundamentos de Python.",
        objective="Criar programas simples.",
        syllabus="Lógica e Python.",
        estimated_hours=Decimal("20.00"),
        status=WorkshopStatus.PUBLISHED,
        created_by=admin_user,
    )


@pytest.fixture
def reporting_class(db, admin_user, reporting_workshop):
    now = timezone.now()
    return ClassGroup.objects.create(
        workshop=reporting_workshop,
        code="CDF-REL-01",
        title="Turma concluída",
        location="Biblioteca Municipal",
        capacity=10,
        registration_opens_at=now - timedelta(days=90),
        registration_closes_at=now - timedelta(days=80),
        start_date=timezone.localdate() - timedelta(days=60),
        end_date=timezone.localdate() - timedelta(days=30),
        status=ClassGroupStatus.COMPLETED,
        created_by=admin_user,
    )


@pytest.fixture
def reporting_instructor(instructor_user, reporting_class):
    instructor = Instructor.objects.create(user=instructor_user, is_active=True)
    ClassInstructor.objects.create(
        class_group=reporting_class,
        instructor=instructor,
        is_lead=True,
    )
    return instructor


@pytest.fixture
def reporting_participant(participant_user):
    return Participant.objects.create(
        user=participant_user,
        full_name=participant_user.full_name,
        birth_date=date(2007, 4, 10),
        cpf="52998224725",
        is_active=True,
    )


@pytest.fixture
def reporting_enrollment(
    reporting_participant,
    reporting_class,
    admin_user,
):
    return Enrollment.objects.create(
        participant=reporting_participant,
        class_group=reporting_class,
        status=EnrollmentStatus.APPROVED,
        confirmed_at=timezone.now() - timedelta(days=70),
        created_by=admin_user,
    )


@pytest.fixture
def reporting_meeting(reporting_class):
    ends_at = timezone.now() - timedelta(days=40)
    return Meeting.objects.create(
        class_group=reporting_class,
        title="Projeto final",
        starts_at=ends_at - timedelta(hours=2),
        ends_at=ends_at,
        status=MeetingStatus.COMPLETED,
    )


@pytest.fixture
def reporting_academic_data(
    reporting_enrollment,
    reporting_meeting,
    admin_user,
):
    Attendance.objects.create(
        enrollment=reporting_enrollment,
        meeting=reporting_meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )
    StudentProject.objects.create(
        enrollment=reporting_enrollment,
        title="Portal comunitário",
        description="Projeto final da oficina.",
        is_delivered=True,
        delivered_at=timezone.now() - timedelta(days=35),
    )
    Evaluation.objects.create(
        enrollment=reporting_enrollment,
        final_score=Decimal("8.0"),
        feedback="Objetivos atendidos.",
        evaluated_by=admin_user,
        published_at=timezone.now() - timedelta(days=30),
    )
    return reporting_enrollment


@pytest.fixture
def unrelated_class(db, admin_user):
    workshop = Workshop.objects.create(
        title="Robótica",
        slug="robotica-relatorios",
        summary="Introdução à robótica.",
        objective="Montar protótipos.",
        syllabus="Eletrônica e lógica.",
        estimated_hours=Decimal("12.00"),
        status=WorkshopStatus.PUBLISHED,
        created_by=admin_user,
    )
    now = timezone.now()
    return ClassGroup.objects.create(
        workshop=workshop,
        code="CDF-OUTRA-01",
        title="Turma não vinculada",
        location="Escola Parceira",
        capacity=15,
        registration_opens_at=now - timedelta(days=20),
        registration_closes_at=now - timedelta(days=10),
        start_date=timezone.localdate() + timedelta(days=5),
        end_date=timezone.localdate() + timedelta(days=20),
        status=ClassGroupStatus.PLANNED,
        created_by=admin_user,
    )


@pytest.fixture
def unrelated_enrollment(unrelated_class, admin_user):
    user = User.objects.create_user(
        email="aluno-relatorio@example.com",
        password="uma-senha-segura-123",
        full_name="Aluno de Outra Turma",
        role=UserRole.PARTICIPANT,
    )
    participant = Participant.objects.create(
        user=user,
        full_name=user.full_name,
        birth_date=date(2008, 5, 20),
        is_active=True,
    )
    return Enrollment.objects.create(
        participant=participant,
        class_group=unrelated_class,
        status=EnrollmentStatus.PENDING,
        created_by=admin_user,
    )
