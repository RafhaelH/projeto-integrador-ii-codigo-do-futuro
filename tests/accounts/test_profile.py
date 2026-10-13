from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import connections
from django.test import Client
from django.urls import reverse

from apps.accounts.models import User, UserRole

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("role", UserRole.values)
def test_each_role_reads_and_updates_own_profile(client, role):
    user = User.objects.create_user(
        email="profile@example.com", password="secret", full_name="Nome Inicial", role=role
    )
    client.force_login(user)
    path = reverse("accounts:profile")
    response = client.get(path)
    assert response.status_code == 200
    assert set(response.context["form"].fields) == {"full_name", "email"}
    assert path in client.get(reverse("home")).content.decode()

    response = client.post(path, {"full_name": " Nome Atualizado ", "email": "NOVO@EXAMPLE.COM"})
    user.refresh_from_db()
    assert response.status_code == 302
    assert user.full_name == "Nome Atualizado"
    assert user.email == "novo@example.com"
    assert user.role == role
    client.logout()
    assert (
        client.post(reverse("login"), {"username": user.email, "password": "secret"}).status_code
        == 302
    )


@pytest.mark.parametrize("method", ["get", "post"])
def test_anonymous_profile_access_redirects_to_login(client, method):
    response = getattr(client, method)(reverse("accounts:profile"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_profile_ignores_target_and_protected_fields(client, participant_user, admin_user):
    client.force_login(participant_user)
    other_before = User.objects.values().get(pk=admin_user.pk)
    protected_before = {
        field: getattr(participant_user, field)
        for field in ["password", "role", "is_staff", "is_superuser", "is_active"]
    }
    response = client.post(
        reverse("accounts:profile") + f"?user={admin_user.pk}",
        {
            "full_name": "Meu Nome",
            "email": "meu@example.com",
            "pk": str(admin_user.pk),
            "user": str(admin_user.pk),
            "id": str(admin_user.pk),
            "role": "ADMIN",
            "is_staff": "on",
            "is_superuser": "on",
            "is_active": "",
            "password": "changed",
            "groups": [1],
            "user_permissions": [1],
        },
    )
    participant_user.refresh_from_db()
    assert response.status_code == 302
    assert participant_user.full_name == "Meu Nome"
    assert {
        field: getattr(participant_user, field) for field in protected_before
    } == protected_before
    assert not participant_user.groups.exists()
    assert not participant_user.user_permissions.exists()
    assert User.objects.values().get(pk=admin_user.pk) == other_before
    assert client.post(f"/conta/perfil/{admin_user.pk}/", {}).status_code == 404


@pytest.mark.parametrize(
    "name,email,field",
    [
        ("", "valid@example.com", "full_name"),
        ("   ", "valid@example.com", "full_name"),
        ("x" * 151, "valid@example.com", "full_name"),
        ("Nome", "", "email"),
        ("Nome", "invalid", "email"),
        ("Nome", "ADMIN@EXAMPLE.COM", "email"),
    ],
)
def test_invalid_profile_is_not_partially_saved(
    client, participant_user, admin_user, name, email, field
):
    client.force_login(participant_user)
    before = User.objects.values().get(pk=participant_user.pk)
    response = client.post(reverse("accounts:profile"), {"full_name": name, "email": email})
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert User.objects.values().get(pk=participant_user.pk) == before


def test_profile_requires_csrf(participant_user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(participant_user)
    response = client.post(
        reverse("accounts:profile"), {"full_name": "Nome", "email": "valid@example.com"}
    )
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_email_race_returns_error_without_partial_profile_update(
    client, participant_user, admin_user, monkeypatch
):
    client.force_login(participant_user)
    before = User.objects.values().get(pk=participant_user.pk)
    save = User.save

    def racing_save(instance, *args, **kwargs):
        if instance.pk == participant_user.pk and "email" in kwargs.get("update_fields", []):

            def reserve_email():
                try:
                    User.objects.filter(pk=admin_user.pk).update(email=instance.email)
                finally:
                    connections.close_all()

            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(reserve_email).result(timeout=10)
        return save(instance, *args, **kwargs)

    monkeypatch.setattr(User, "save", racing_save)
    response = client.post(
        reverse("accounts:profile"),
        {"full_name": "Não deve gravar", "email": "reserved@example.com"},
    )
    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    assert User.objects.values().get(pk=participant_user.pk) == before
