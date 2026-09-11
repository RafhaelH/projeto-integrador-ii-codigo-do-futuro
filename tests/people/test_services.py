from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.people.models import Guardian, GuardianRelationship, Participant, ParticipantGuardian
from apps.people.services import calculate_age, validate_participant_eligibility

pytestmark = pytest.mark.django_db


def test_calculate_age_before_and_after_birthday():
    birth_date = date(2010, 9, 20)

    assert calculate_age(birth_date, date(2026, 9, 19)) == 15
    assert calculate_age(birth_date, date(2026, 9, 20)) == 16


@pytest.mark.parametrize("birth_date", [date(2012, 6, 1), date(2005, 6, 1)])
def test_eligibility_accepts_age_boundaries_with_adult_or_guardian(birth_date):
    participant = Participant.objects.create(full_name="Participante", birth_date=birth_date)
    if birth_date.year == 2012:
        guardian = Guardian.objects.create(full_name="Responsável", phone="16999991234")
        ParticipantGuardian.objects.create(
            participant=participant,
            guardian=guardian,
            relationship=GuardianRelationship.LEGAL_GUARDIAN,
            is_primary=True,
        )

    validate_participant_eligibility(participant, date(2026, 6, 1))


def test_eligibility_rejects_minor_without_active_guardian():
    participant = Participant.objects.create(
        full_name="Participante Menor",
        birth_date=date(2010, 1, 1),
    )

    with pytest.raises(ValidationError, match="responsável ativo"):
        validate_participant_eligibility(participant, date(2026, 6, 1))


@pytest.mark.parametrize("birth_date", [date(2012, 6, 2), date(2004, 5, 31)])
def test_eligibility_rejects_age_outside_range(birth_date):
    participant = Participant.objects.create(full_name="Participante", birth_date=birth_date)

    with pytest.raises(ValidationError, match="entre 14 e 21 anos"):
        validate_participant_eligibility(participant, date(2026, 6, 1))


def test_eligibility_rejects_inactive_participant():
    participant = Participant.objects.create(
        full_name="Participante Inativo",
        birth_date=date(2008, 1, 1),
        is_active=False,
    )

    with pytest.raises(ValidationError, match="está inativo"):
        validate_participant_eligibility(participant, date(2026, 6, 1))
