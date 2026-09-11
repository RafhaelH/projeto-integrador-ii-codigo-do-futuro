from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.people.models import (
    Guardian,
    GuardianRelationship,
    Institution,
    Instructor,
    Participant,
    ParticipantGuardian,
)

pytestmark = pytest.mark.django_db


def test_participant_normalizes_and_masks_cpf(participant_user):
    participant = Participant.objects.create(
        user=participant_user,
        full_name="Participante Exemplo",
        birth_date=date(2008, 1, 10),
        cpf="529.982.247-25",
        phone="(16) 99999-1234",
    )

    assert participant.cpf == "52998224725"
    assert participant.phone == "16999991234"
    assert participant.formatted_cpf == "529.982.247-25"
    assert participant.masked_cpf == "***.982.247-**"
    assert participant.formatted_phone == "(16) 99999-1234"


def test_participant_user_must_have_participant_role(admin_user):
    participant = Participant(
        user=admin_user,
        full_name="Perfil Inválido",
        birth_date=date(2008, 1, 10),
    )

    with pytest.raises(ValidationError, match="perfil participante"):
        participant.full_clean()


def test_instructor_user_must_have_instructor_role(participant_user):
    instructor = Instructor(user=participant_user)

    with pytest.raises(ValidationError, match="perfil instrutor"):
        instructor.full_clean()


def test_only_one_primary_guardian_is_allowed(participant_user):
    participant = Participant.objects.create(
        user=participant_user,
        full_name="Participante Exemplo",
        birth_date=date(2010, 5, 1),
    )
    first = Guardian.objects.create(full_name="Primeiro Responsável", phone="16999990001")
    second = Guardian.objects.create(full_name="Segundo Responsável", phone="16999990002")
    ParticipantGuardian.objects.create(
        participant=participant,
        guardian=first,
        relationship=GuardianRelationship.MOTHER,
        is_primary=True,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        ParticipantGuardian.objects.create(
            participant=participant,
            guardian=second,
            relationship=GuardianRelationship.FATHER,
            is_primary=True,
        )


def test_institution_normalizes_document_and_phone():
    institution = Institution.objects.create(
        name="Instituição Exemplo",
        document="11.222.333/0001-81",
        contact_phone="(16) 3600-1234",
    )

    assert institution.document == "11222333000181"
    assert institution.contact_phone == "1636001234"
    assert institution.formatted_contact_phone == "(16) 3600-1234"
