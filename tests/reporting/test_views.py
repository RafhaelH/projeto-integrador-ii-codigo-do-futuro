import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_dashboard_requires_authentication(client):
    response = client.get(reverse("reporting:dashboard"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_participant_cannot_access_dashboard(client, participant_user):
    client.force_login(participant_user)

    response = client.get(reverse("reporting:dashboard"))

    assert response.status_code == 403


def test_admin_dashboard_shows_reconciled_metrics(
    client,
    admin_user,
    reporting_class,
    reporting_academic_data,
):
    client.force_login(admin_user)

    response = client.get(reverse("reporting:dashboard"))
    content = response.content.decode()

    assert response.status_code == 200
    assert reporting_class.code in content
    assert "100,00%" in content
    assert "10,00%" in content
    assert "todo o período" in content


def test_dashboard_applies_same_period_to_table_and_metrics(
    client,
    admin_user,
    reporting_class,
    unrelated_class,
):
    client.force_login(admin_user)

    response = client.get(
        reverse("reporting:dashboard"),
        {"period_end": reporting_class.start_date.isoformat()},
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert reporting_class.code in content
    assert unrelated_class.code not in content
    assert "1 de 10 vagas" not in content
    assert "Turmas</small><strong>1" in content


def test_instructor_dashboard_hides_unrelated_class(
    client,
    instructor_user,
    reporting_instructor,
    reporting_class,
    unrelated_class,
):
    client.force_login(instructor_user)

    response = client.get(reverse("reporting:dashboard"))
    content = response.content.decode()

    assert response.status_code == 200
    assert reporting_class.code in content
    assert unrelated_class.code not in content
    assert "Inscrições CSV" not in content


@pytest.mark.parametrize("report_kind", ["inscricoes", "frequencia", "conclusao"])
def test_admin_exports_csv_reports(
    client,
    admin_user,
    reporting_class,
    reporting_academic_data,
    report_kind,
):
    client.force_login(admin_user)

    response = client.get(
        reverse(
            "reporting:export",
            kwargs={"report_kind": report_kind},
        )
    )
    content = response.content.decode("utf-8-sig")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert "todo o período" in content
    assert reporting_class.code in content
    assert "52998224725" not in content


def test_instructor_cannot_export_report(
    client,
    instructor_user,
    reporting_instructor,
):
    client.force_login(instructor_user)

    response = client.get(
        reverse(
            "reporting:export",
            kwargs={"report_kind": "inscricoes"},
        )
    )

    assert response.status_code == 403


def test_invalid_filter_returns_empty_dashboard(client, admin_user, reporting_class):
    client.force_login(admin_user)

    response = client.get(
        reverse("reporting:dashboard"),
        {
            "period_start": "2026-09-10",
            "period_end": "2026-09-01",
        },
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert "data inicial" in content
    assert reporting_class.code not in content
