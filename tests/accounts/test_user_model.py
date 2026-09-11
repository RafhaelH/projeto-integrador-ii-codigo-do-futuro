import pytest
from django.db import IntegrityError

from apps.accounts.models import User, UserRole

pytestmark = pytest.mark.django_db


def test_create_user_normalizes_email_and_hashes_password():
    user = User.objects.create_user(
        email="  Pessoa@EXAMPLE.COM  ",
        password="senha-forte-123",
        full_name="Pessoa Exemplo",
    )

    assert user.email == "pessoa@example.com"
    assert user.role == UserRole.PARTICIPANT
    assert user.check_password("senha-forte-123")
    assert user.password != "senha-forte-123"


def test_email_is_unique_ignoring_case():
    User.objects.create_user(
        email="pessoa@example.com",
        password="senha-forte-123",
        full_name="Primeira Pessoa",
    )

    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email="PESSOA@example.com",
            password="outra-senha-123",
            full_name="Segunda Pessoa",
        )


def test_create_superuser_forces_administrator_role():
    user = User.objects.create_superuser(
        email="admin@example.com",
        password="senha-administrativa-123",
        full_name="Administrador Exemplo",
    )

    assert user.is_staff
    assert user.is_superuser
    assert user.role == UserRole.ADMIN


def test_short_name_uses_first_part_of_full_name(participant_user):
    assert participant_user.get_short_name() == "Participante"
