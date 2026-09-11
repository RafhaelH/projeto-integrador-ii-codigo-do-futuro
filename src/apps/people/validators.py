import re

from django.core.exceptions import ValidationError


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def format_phone(value: str) -> str:
    digits = only_digits(value)
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return value


def validate_phone(value: str) -> None:
    digits = only_digits(value)
    if len(digits) not in {10, 11}:
        raise ValidationError("Informe um telefone com DDD e 10 ou 11 dígitos.")


def validate_cpf(value: str) -> None:
    digits = only_digits(value)
    if len(digits) != 11 or len(set(digits)) == 1:
        raise ValidationError("Informe um CPF válido.")

    numbers = [int(digit) for digit in digits]
    first_total = sum(
        number * weight for number, weight in zip(numbers[:9], range(10, 1, -1), strict=True)
    )
    first_digit = (first_total * 10 % 11) % 10
    second_total = sum(
        number * weight for number, weight in zip(numbers[:10], range(11, 1, -1), strict=True)
    )
    second_digit = (second_total * 10 % 11) % 10

    if numbers[9:] != [first_digit, second_digit]:
        raise ValidationError("Informe um CPF válido.")


def validate_cnpj(value: str) -> None:
    digits = only_digits(value)
    if len(digits) != 14 or len(set(digits)) == 1:
        raise ValidationError("Informe um CNPJ válido.")

    numbers = [int(digit) for digit in digits]

    def check_digit(base: list[int], weights: list[int]) -> int:
        remainder = sum(number * weight for number, weight in zip(base, weights, strict=True)) % 11
        return 0 if remainder < 2 else 11 - remainder

    first_digit = check_digit(numbers[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second_digit = check_digit(
        numbers[:12] + [first_digit], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    )

    if numbers[12:] != [first_digit, second_digit]:
        raise ValidationError("Informe um CNPJ válido.")
