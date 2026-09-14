import pytest

from apps.reporting.forms import ReportingFilterForm

pytestmark = pytest.mark.django_db


def test_filter_rejects_inverted_period(admin_user):
    form = ReportingFilterForm(
        {
            "period_start": "2026-09-10",
            "period_end": "2026-09-01",
        },
        user=admin_user,
    )

    assert not form.is_valid()
    assert "data inicial" in form.non_field_errors()[0]


def test_instructor_filter_lists_only_linked_workshops(
    instructor_user,
    reporting_instructor,
    reporting_workshop,
    unrelated_class,
):
    form = ReportingFilterForm(user=instructor_user)

    assert list(form.fields["workshop"].queryset) == [reporting_workshop]
