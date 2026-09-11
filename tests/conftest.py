import pytest

from apps.accounts.models import User, UserRole


@pytest.fixture
def participant_user(db) -> User:
    return User.objects.create_user(
        email="participante@example.com",
        password="uma-senha-segura-123",
        full_name="Participante Exemplo",
        role=UserRole.PARTICIPANT,
    )


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_user(
        email="admin@example.com",
        password="uma-senha-segura-123",
        full_name="Administrador Exemplo",
        role=UserRole.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def instructor_user(db) -> User:
    return User.objects.create_user(
        email="instrutor@example.com",
        password="uma-senha-segura-123",
        full_name="Instrutor Exemplo",
        role=UserRole.INSTRUCTOR,
    )
