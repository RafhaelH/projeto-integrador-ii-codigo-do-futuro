from datetime import date, datetime

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.workshops.models import ClassGroup, Meeting, Workshop, WorkshopStatus

pytestmark = pytest.mark.django_db


def test_workshop_is_created_as_draft(admin_user):
    workshop = Workshop.objects.create(
        title="Web para iniciantes",
        slug="web-iniciantes",
        summary="HTML e CSS.",
        objective="Criar uma página.",
        syllabus="HTML e CSS",
        estimated_hours=8,
        created_by=admin_user,
    )

    assert workshop.status == WorkshopStatus.DRAFT
    assert str(workshop) == "Web para iniciantes"


def test_class_rejects_unpublished_workshop(admin_user):
    workshop = Workshop.objects.create(
        title="Rascunho",
        slug="rascunho",
        summary="Resumo",
        objective="Objetivo",
        syllabus="Conteúdo",
        estimated_hours=8,
        created_by=admin_user,
    )
    class_group = ClassGroup(
        workshop=workshop,
        code="T-01",
        title="Turma",
        location="Sala",
        capacity=10,
        registration_opens_at=timezone.make_aware(datetime(2026, 9, 1, 8)),
        registration_closes_at=timezone.make_aware(datetime(2026, 9, 10, 18)),
        start_date=date(2026, 9, 11),
        end_date=date(2026, 9, 30),
        created_by=admin_user,
    )

    with pytest.raises(ValidationError, match="oficina publicada"):
        class_group.full_clean()


def test_class_rejects_inconsistent_dates(planned_class):
    planned_class.registration_closes_at = planned_class.registration_opens_at.replace(day=1)

    with pytest.raises(ValidationError):
        planned_class.full_clean()


def test_meeting_rejects_period_outside_class(planned_class):
    meeting = Meeting(
        class_group=planned_class,
        title="Encontro antecipado",
        starts_at=timezone.make_aware(datetime(2026, 9, 25, 9)),
        ends_at=timezone.make_aware(datetime(2026, 9, 25, 11)),
    )

    with pytest.raises(ValidationError, match="período da turma"):
        meeting.full_clean()


def test_meeting_rejects_end_before_start(planned_class):
    meeting = Meeting(
        class_group=planned_class,
        title="Horário inválido",
        starts_at=timezone.make_aware(datetime(2026, 10, 10, 11)),
        ends_at=timezone.make_aware(datetime(2026, 10, 10, 9)),
    )

    with pytest.raises(ValidationError, match="posterior ao início"):
        meeting.full_clean()
