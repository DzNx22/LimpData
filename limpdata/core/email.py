"""Normalização e validação de endereços de e-mail."""

import re
from dataclasses import dataclass
from enum import Enum

from limpdata.core.models import Record
from limpdata.core.textutils import basic_clean

COLUMNS = ("E-mail",)

# Validação sintática pragmática (subconjunto da RFC 5322 usado na prática).
_LOCAL = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
_EMAIL = re.compile(rf"^{_LOCAL}@(?:{_LABEL}\.)+[A-Za-z]{{2,63}}$")

MAX_LOCAL_LENGTH = 64
MAX_LENGTH = 254


class EmailCase(Enum):
    LOWER = "minúsculas"
    UPPER = "MAIÚSCULAS"
    KEEP = "manter"


@dataclass(frozen=True)
class EmailOptions:
    case: EmailCase = EmailCase.LOWER


def validate_email(email: str) -> str | None:
    """Retorna a mensagem de erro, ou None se o e-mail for válido."""
    if " " in email:
        return "contém espaços"
    if email.count("@") != 1:
        return "deve conter exatamente um @"
    if len(email) > MAX_LENGTH:
        return "endereço muito longo"
    if len(email.split("@")[0]) > MAX_LOCAL_LENGTH:
        return "parte antes do @ muito longa"
    if not _EMAIL.match(email):
        return "formato inválido"
    return None


def normalize_email(value: str, options: EmailOptions = EmailOptions()) -> Record:
    email = basic_clean(value)
    if not email:
        return Record.empty(value)

    error = validate_email(email)
    if error:
        return Record.invalid(value, email, error)

    if options.case is EmailCase.LOWER:
        email = email.lower()
    elif options.case is EmailCase.UPPER:
        email = email.upper()
    return Record.valid(value, email)
