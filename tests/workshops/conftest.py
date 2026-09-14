from datetime import date, datetime
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.workshops.models import ClassGroup, Workshop, WorkshopStatus


@pytest.fixture
def published_workshop(db, admin_user):
    return Workshop.objects.create(
        title="Introdução à Programação",
        slug="introducao-programacao",
        summary="Fundamentos de programação para jovens.",
        objective="Desenvolver raciocínio lógico.",
        syllabus="Lógica, algoritmos e Python.",
        estimated_hours=Decimal("16.00"),
        status=WorkshopStatus.PUBLISHED,
        created_by=admin_user,
    )


@pytest.fixture
def planned_class(db, admin_user, published_workshop):
    return ClassGroup.objects.create(
        workshop=published_workshop,
        code="CDF-2026-01",
        title="Turma de Primavera",
        location="Biblioteca Municipal",
        capacity=20,
        registration_opens_at=timezone.make_aware(datetime(2026, 9, 15, 8)),
        registration_closes_at=timezone.make_aware(datetime(2026, 9, 30, 18)),
        start_date=date(2026, 10, 1),
        end_date=date(2026, 11, 30),
        created_by=admin_user,
    )
