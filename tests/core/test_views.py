import pytest
from django.db.utils import OperationalError
from django.urls import reverse


def test_health_check_is_public(client):
    response = client.get(reverse("health-check"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "codigo-do-futuro"}


@pytest.mark.django_db
def test_readiness_check_confirms_database_connection(client):
    response = client.get(reverse("readiness-check"))

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "codigo-do-futuro"}


@pytest.mark.django_db
def test_readiness_check_hides_database_error(client, monkeypatch):
    monkeypatch.setattr(
        "apps.core.views.connection.cursor",
        lambda: (_ for _ in ()).throw(OperationalError("sensitive database detail")),
    )

    response = client.get(reverse("readiness-check"))

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "service": "codigo-do-futuro",
    }
    assert b"sensitive database detail" not in response.content


def test_home_redirects_anonymous_user_to_login(client):
    response = client.get(reverse("home"))

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next=/"


@pytest.mark.django_db
def test_home_is_available_to_authenticated_user(client, participant_user):
    client.force_login(participant_user)

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert "Bem-vindo ao Código do Futuro" in response.content.decode()
