import pytest
from django.core.exceptions import ValidationError

from apps.people.validators import (
    format_phone,
    only_digits,
    validate_cnpj,
    validate_cpf,
    validate_phone,
)


def test_only_digits_removes_document_formatting():
    assert only_digits("529.982.247-25") == "52998224725"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("16999991234", "(16) 99999-1234"),
        ("1636001234", "(16) 3600-1234"),
        ("123", "123"),
    ],
)
def test_format_phone(value, expected):
    assert format_phone(value) == expected


@pytest.mark.parametrize("cpf", ["52998224725", "529.982.247-25"])
def test_validate_cpf_accepts_valid_value(cpf):
    validate_cpf(cpf)


@pytest.mark.parametrize("cpf", ["", "11111111111", "52998224724"])
def test_validate_cpf_rejects_invalid_value(cpf):
    with pytest.raises(ValidationError):
        validate_cpf(cpf)


def test_validate_cnpj_accepts_formatted_valid_value():
    validate_cnpj("11.222.333/0001-81")


@pytest.mark.parametrize("cnpj", ["", "11111111111111", "11222333000180"])
def test_validate_cnpj_rejects_invalid_value(cnpj):
    with pytest.raises(ValidationError):
        validate_cnpj(cnpj)


@pytest.mark.parametrize("phone", ["1636001234", "16999991234", "(16) 99999-1234"])
def test_validate_phone_accepts_ten_or_eleven_digits(phone):
    validate_phone(phone)


def test_validate_phone_rejects_invalid_length():
    with pytest.raises(ValidationError):
        validate_phone("123")
