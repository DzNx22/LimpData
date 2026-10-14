"""Validação e formatação de CPF."""

import re
from dataclasses import dataclass

from limpdata.core.models import Record
from limpdata.core.textutils import basic_clean

COLUMNS = ("CPF",)
LENGTH = 11
# Só completa com zeros valores próximos do tamanho real, evitando que
# números curtos (ex.: "191") virem um CPF válido por acaso.
MIN_LENGTH_TO_PAD = 8

_ALLOWED = re.compile(r"^[\d.\-/ ]+$")


@dataclass(frozen=True)
class CpfOptions:
    formatted: bool = True
    # Planilhas costumam remover zeros à esquerda de CPFs salvos como número.
    pad_zeros: bool = True


def check_digits(base: str) -> str:
    """Calcula os dois dígitos verificadores para os 9 primeiros dígitos."""
    digits = [int(d) for d in base]
    for weight_start in (10, 11):
        total = sum(d * w for d, w in zip(digits, range(weight_start, 1, -1)))
        remainder = total % 11
        digits.append(0 if remainder < 2 else 11 - remainder)
    return "".join(str(d) for d in digits[-2:])


def validate_cpf(digits: str) -> str | None:
    """Retorna a mensagem de erro, ou None se o CPF (só dígitos) for válido."""
    if len(digits) != LENGTH:
        return f"possui {len(digits)} dígitos (esperado {LENGTH})"
    if digits == digits[0] * LENGTH:
        return "todos os dígitos são iguais"
    if check_digits(digits[:9]) != digits[9:]:
        return "dígitos verificadores não conferem"
    return None


def format_cpf(digits: str) -> str:
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def normalize_cpf(value: str, options: CpfOptions = CpfOptions()) -> Record:
    cleaned = basic_clean(value)
    if not cleaned:
        return Record.empty(value)
    if not _ALLOWED.match(cleaned):
        return Record.invalid(value, cleaned, "contém caracteres não numéricos")

    digits = re.sub(r"\D", "", cleaned)
    can_pad = cleaned.isdigit() and MIN_LENGTH_TO_PAD <= len(digits) < LENGTH
    if options.pad_zeros and can_pad:
        digits = digits.zfill(LENGTH)

    error = validate_cpf(digits)
    if error:
        return Record.invalid(value, cleaned, error)
    return Record.valid(value, format_cpf(digits) if options.formatted else digits)
