import pytest
from django.core import mail
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_active_user_can_sign_in(client, participant_user):
    response = client.post(
        reverse("login"),
        {"username": participant_user.email, "password": "uma-senha-segura-123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("home")


def test_inactive_user_cannot_sign_in(client, participant_user):
    participant_user.is_active = False
    participant_user.save(update_fields=["is_active", "updated_at"])

    response = client.post(
        reverse("login"),
        {"username": participant_user.email, "password": "uma-senha-segura-123"},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert "E-mail ou senha inválidos" in response.content.decode()


def test_password_reset_sends_email_without_exposing_account(client, participant_user):
    response = client.post(reverse("password_reset"), {"email": participant_user.email})

    assert response.status_code == 302
    assert response.url == reverse("password_reset_done")
    assert len(mail.outbox) == 1
    assert participant_user.email in mail.outbox[0].to


def test_password_reset_unknown_email_has_same_response(client):
    response = client.post(reverse("password_reset"), {"email": "ausente@example.com"})

    assert response.status_code == 302
    assert response.url == reverse("password_reset_done")
    assert mail.outbox == []
