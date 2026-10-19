from datetime import date, datetime
from html.parser import HTMLParser
from types import SimpleNamespace

import pytest
from django.utils import timezone, translation

from apps.people.forms import ParticipantForm
from apps.reporting.forms import ReportingFilterForm
from apps.workshops.forms import ClassGroupForm, MeetingForm


class InputValues(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.inputs = {}
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input":
            self.inputs[attrs["name"]] = attrs


@pytest.mark.parametrize(
    ("kind", "field", "input_type"),
    [
        ("participant", "birth_date", "date"),
        ("participant", "privacy_consent_at", "datetime-local"),
        ("class", "registration_opens_at", "datetime-local"),
        ("class", "registration_closes_at", "datetime-local"),
        ("class", "start_date", "date"),
        ("class", "end_date", "date"),
        ("meeting", "starts_at", "datetime-local"),
        ("meeting", "ends_at", "datetime-local"),
        ("report", "period_start", "date"),
        ("report", "period_end", "date"),
    ],
)
def test_native_date_input_keeps_existing_value_in_portuguese(kind, field, input_type):
    with translation.override("pt-br"), timezone.override("America/Sao_Paulo"):
        value = (
            date(2026, 10, 19)
            if input_type == "date"
            else timezone.make_aware(datetime(2026, 10, 19, 14, 35))
        )
        constructors = {
            "participant": ParticipantForm,
            "class": ClassGroupForm,
            "meeting": MeetingForm,
            "report": lambda **kwargs: ReportingFilterForm(
                user=SimpleNamespace(role="ADMIN"), **kwargs
            ),
        }
        form = constructors[kind](initial={field: value})
        attrs = InputValues(str(form[field])).inputs[field]
        expected = "2026-10-19" if input_type == "date" else "2026-10-19T14:35"

        assert attrs["type"] == input_type
        assert attrs["value"] == expected
        # The ISO value accepted by the browser also round-trips through Django.
        cleaned = form.fields[field].clean(attrs["value"])
        assert cleaned == value
