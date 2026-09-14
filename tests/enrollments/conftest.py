from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.people.models import Participant
from apps.workshops.models import ClassGroup, ClassGroupStatus, Workshop, WorkshopStatus


@pytest.fixture
def published_workshop(db, admin_user):
    return Workshop.objects.create(
        title="Introdução à Programação",
        slug="introducao-programacao-inscricoes",
        summary="Fundamentos de programação para jovens.",
        objective="Desenvolver raciocínio lógico.",
        syllabus="Lógica, algoritmos e Python.",
        estimated_hours=Decimal("16.00"),
        status=WorkshopStatus.PUBLISHED,
        created_by=admin_user,
    )


@pytest.fixture
def planned_class(db, admin_user, published_workshop):
    now = timezone.now()
    return ClassGroup.objects.create(
        workshop=published_workshop,
        code="CDF-ENROLL-01",
        title="Turma de Inscrições",
        location="Biblioteca Municipal",
        capacity=20,
        registration_opens_at=now - timedelta(days=1),
        registration_closes_at=now + timedelta(days=1),
        start_date=timezone.localdate() + timedelta(days=2),
        end_date=timezone.localdate() + timedelta(days=32),
        created_by=admin_user,
    )


@pytest.fixture
def adult_participant(participant_user) -> Participant:
    return Participant.objects.create(
        user=participant_user,
        full_name=participant_user.full_name,
        birth_date=date(2008, 1, 10),
        contact_email=participant_user.email,
        is_active=True,
    )


@pytest.fixture
def second_participant(db) -> Participant:
    user = User.objects.create_user(
        email="segundo@example.com",
        password="uma-senha-segura-123",
        full_name="Segundo Participante",
        role=UserRole.PARTICIPANT,
    )
    return Participant.objects.create(
        user=user,
        full_name=user.full_name,
        birth_date=date(2007, 5, 20),
        contact_email=user.email,
        is_active=True,
    )


@pytest.fixture
def open_class(planned_class):
    now = timezone.now()
    planned_class.status = ClassGroupStatus.OPEN
    planned_class.capacity = 1
    planned_class.registration_opens_at = now - timedelta(days=1)
    planned_class.registration_closes_at = now + timedelta(days=1)
    planned_class.start_date = timezone.localdate() + timedelta(days=2)
    planned_class.end_date = timezone.localdate() + timedelta(days=32)
    planned_class.save()
    return planned_class
