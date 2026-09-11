from datetime import date

from django.core.exceptions import ValidationError

from .models import Participant

MINIMUM_PARTICIPANT_AGE = 14
MAXIMUM_PARTICIPANT_AGE = 21
LEGAL_AGE = 18


def calculate_age(birth_date: date, reference_date: date) -> int:
    before_birthday = (reference_date.month, reference_date.day) < (
        birth_date.month,
        birth_date.day,
    )
    return reference_date.year - birth_date.year - before_birthday


def participant_has_active_guardian(participant: Participant) -> bool:
    return participant.guardian_links.filter(guardian__is_active=True).exists()


def validate_participant_eligibility(participant: Participant, reference_date: date) -> None:
    if not participant.is_active:
        raise ValidationError("O participante está inativo.")

    age = calculate_age(participant.birth_date, reference_date)
    if not MINIMUM_PARTICIPANT_AGE <= age <= MAXIMUM_PARTICIPANT_AGE:
        raise ValidationError(
            f"O participante deve ter entre {MINIMUM_PARTICIPANT_AGE} e "
            f"{MAXIMUM_PARTICIPANT_AGE} anos na data de início da turma."
        )

    if age < LEGAL_AGE and not participant_has_active_guardian(participant):
        raise ValidationError("Participantes menores de 18 anos precisam de responsável ativo.")
