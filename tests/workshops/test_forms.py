from datetime import datetime

import pytest
from django.utils import timezone

from apps.workshops.forms import ClassGroupForm, MeetingForm

pytestmark = pytest.mark.django_db


def test_class_form_rejects_dates_in_wrong_order(published_workshop):
    form = ClassGroupForm(
        data={
            "workshop": published_workshop.pk,
            "code": "CDF-INVALIDA",
            "title": "Turma inválida",
            "location": "Biblioteca",
            "capacity": 18,
            "registration_opens_at": "2026-09-20T08:00",
            "registration_closes_at": "2026-09-10T18:00",
            "start_date": "2026-10-01",
            "end_date": "2026-11-30",
        }
    )

    assert not form.is_valid()
    assert "registration_closes_at" in form.errors


def test_meeting_form_uses_class_period(planned_class):
    form = MeetingForm(
        data={
            "title": "Fora do período",
            "starts_at": "2026-12-10T09:00",
            "ends_at": "2026-12-10T11:00",
        },
        class_group=planned_class,
    )

    assert not form.is_valid()
    assert "starts_at" in form.errors


def test_meeting_form_accepts_valid_schedule(planned_class):
    form = MeetingForm(
        data={
            "title": "Lógica de programação",
            "description": "Algoritmos",
            "starts_at": timezone.localtime(
                timezone.make_aware(datetime(2026, 10, 10, 9))
            ).strftime("%Y-%m-%dT%H:%M"),
            "ends_at": "2026-10-10T11:00",
        },
        class_group=planned_class,
    )

    assert form.is_valid(), form.errors
