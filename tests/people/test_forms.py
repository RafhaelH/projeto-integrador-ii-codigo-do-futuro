import pytest

from apps.people.forms import InstitutionForm, ParticipantForm

pytestmark = pytest.mark.django_db


def test_participant_form_accepts_and_normalizes_formatted_values():
    form = ParticipantForm(
        data={
            "full_name": "Participante Exemplo",
            "birth_date": "2008-01-10",
            "cpf": "529.982.247-25",
            "contact_email": "participante@example.com",
            "phone": "(16) 99999-1234",
            "is_active": True,
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["cpf"] == "52998224725"
    assert form.cleaned_data["phone"] == "16999991234"


def test_institution_form_rejects_invalid_cnpj():
    form = InstitutionForm(
        data={
            "name": "Instituição Exemplo",
            "document": "11.222.333/0001-80",
            "is_active": True,
        }
    )

    assert not form.is_valid()
    assert "document" in form.errors
