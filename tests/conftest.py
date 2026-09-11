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
