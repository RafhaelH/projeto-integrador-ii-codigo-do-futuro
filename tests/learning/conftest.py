from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.people.models import Instructor, Participant
from apps.workshops.models import (
    ClassGroup,
    ClassGroupStatus,
    ClassInstructor,
    Meeting,
    Workshop,
    WorkshopStatus,
)


@pytest.fixture
def learning_workshop(db, admin_user):
    return Workshop.objects.create(
        title="Programação com Python",
        slug="programacao-python-frequencia",
        summary="Fundamentos de Python.",
        objective="Criar programas simples.",
        syllabus="Lógica e Python.",
        estimated_hours=Decimal("16.00"),
        status=WorkshopStatus.PUBLISHED,
        created_by=admin_user,
    )


@pytest.fixture
def learning_class(db, admin_user, learning_workshop):
    now = timezone.now()
    return ClassGroup.objects.create(
        workshop=learning_workshop,
        code="CDF-FREQ-01",
        title="Turma de Frequência",
        location="Biblioteca Municipal",
        capacity=20,
        registration_opens_at=now - timedelta(days=30),
        registration_closes_at=now - timedelta(days=20),
        start_date=timezone.localdate() - timedelta(days=15),
        end_date=timezone.localdate() + timedelta(days=15),
        status=ClassGroupStatus.IN_PROGRESS,
        created_by=admin_user,
    )


@pytest.fixture
def learning_participant(participant_user):
    return Participant.objects.create(
        user=participant_user,
        full_name=participant_user.full_name,
        birth_date=date(2008, 1, 10),
        is_active=True,
    )


@pytest.fixture
def another_learning_participant(db):
    user = User.objects.create_user(
        email="outro-aluno@example.com",
        password="uma-senha-segura-123",
        full_name="Outro Aluno",
        role=UserRole.PARTICIPANT,
    )
    return Participant.objects.create(
        user=user,
        full_name=user.full_name,
        birth_date=date(2007, 2, 20),
        is_active=True,
    )


@pytest.fixture
def confirmed_enrollment(learning_participant, learning_class, admin_user):
    return Enrollment.objects.create(
        participant=learning_participant,
        class_group=learning_class,
        status=EnrollmentStatus.CONFIRMED,
        confirmed_at=timezone.now(),
        created_by=admin_user,
    )


@pytest.fixture
def second_confirmed_enrollment(another_learning_participant, learning_class, admin_user):
    return Enrollment.objects.create(
        participant=another_learning_participant,
        class_group=learning_class,
        status=EnrollmentStatus.CONFIRMED,
        confirmed_at=timezone.now(),
        created_by=admin_user,
    )


@pytest.fixture
def past_meeting(learning_class):
    end = timezone.now() - timedelta(days=1)
    return Meeting.objects.create(
        class_group=learning_class,
        title="Lógica de programação",
        starts_at=end - timedelta(hours=2),
        ends_at=end,
    )


@pytest.fixture
def assigned_instructor(instructor_user, learning_class):
    instructor = Instructor.objects.create(user=instructor_user, is_active=True)
    ClassInstructor.objects.create(
        class_group=learning_class,
        instructor=instructor,
        is_lead=True,
    )
    return instructor
