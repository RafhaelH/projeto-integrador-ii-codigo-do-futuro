from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.contrib import admin
from django.db import connections
from django.test import Client
from django.urls import reverse

from apps.accounts.forms import UserChangeForm
from apps.accounts.models import User, UserRole

pytestmark = pytest.mark.django_db


@pytest.fixture
def sole_admin():
    return User.objects.create_superuser(
        email="sole@example.com", full_name="Único Admin", password="secret", role=UserRole.ADMIN
    )


@pytest.mark.parametrize(
    "change", [{"is_active": False}, {"role": UserRole.INSTRUCTOR}, {"is_staff": False}]
)
def test_only_active_administrator_cannot_lose_access(client, sole_admin, change):
    client.force_login(sole_admin)
    before = User.objects.values().get(pk=sole_admin.pk)
    payload = {
        "email": sole_admin.email,
        "full_name": "Não deve gravar",
        "role": "ADMIN",
        "is_active": True,
        "is_staff": True,
        "is_superuser": True,
    } | change
    response = client.post(reverse("admin:accounts_user_change", args=[sole_admin.pk]), payload)
    assert response.status_code == 200
    assert "único administrador ativo" in response.content.decode()
    assert User.objects.values().get(pk=sole_admin.pk) == before


def test_last_admin_guard_allows_legitimate_edits_and_another_admin(sole_admin):
    data = {
        "email": sole_admin.email,
        "full_name": "Nome Atualizado",
        "role": "ADMIN",
        "is_active": True,
        "is_staff": True,
        "is_superuser": True,
    }
    form = UserChangeForm(data, instance=sole_admin)
    assert form.is_valid(), form.errors
    form.save()
    User.objects.create_superuser(
        email="second@example.com", full_name="Segundo Admin", password="secret", role="ADMIN"
    )
    form = UserChangeForm(data | {"is_active": False}, instance=sole_admin)
    assert form.is_valid(), form.errors
    form.save()
    sole_admin.refresh_from_db()
    assert not sole_admin.is_active


def test_admin_deletion_is_disabled(client, sole_admin):
    client.force_login(sole_admin)
    assert (
        client.post(
            reverse("admin:accounts_user_delete", args=[sole_admin.pk]), {"post": "yes"}
        ).status_code
        == 403
    )
    assert "delete_selected" not in admin.site._registry[User].get_actions(
        client.get(reverse("admin:accounts_user_changelist")).wsgi_request
    )
    assert User.objects.filter(pk=sole_admin.pk, is_active=True).exists()


@pytest.mark.django_db(transaction=True)
def test_concurrent_admin_deactivations_leave_one_active(sole_admin):
    second = User.objects.create_superuser(
        email="second@example.com", full_name="Segundo Admin", password="secret", role="ADMIN"
    )
    barrier = Barrier(2)
    clients = [Client(), Client()]
    for test_client, user in zip(clients, [sole_admin, second], strict=True):
        test_client.force_login(user)

    def deactivate(test_client, user):
        try:
            barrier.wait(timeout=10)
            return test_client.post(
                reverse("admin:accounts_user_change", args=[user.pk]),
                {
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": "ADMIN",
                    "is_staff": "on",
                    "is_superuser": "on",
                },
            ).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(deactivate, test_client, user)
            for test_client, user in zip(clients, [sole_admin, second], strict=True)
        ]
        statuses = [future.result(timeout=15) for future in futures]
    assert sorted(statuses) == [200, 302]
    assert User.objects.filter(role="ADMIN", is_active=True, is_staff=True).count() == 1
