"""Normalização de nomes de pessoas."""

import re
from dataclasses import dataclass
from enum import Enum

from limpdata.core.models import Record
from limpdata.core.textutils import basic_clean

PARTICLES = frozenset({"de", "da", "das", "do", "dos", "e"})
ROMAN_NUMERALS = frozenset({"ii", "iii", "iv"})

# Letras (inclusive acentuadas), espaços, apóstrofos, hífens e pontos.
_VALID_NAME = re.compile(r"^[^\W\d_]+(?:[ '’.\-]+[^\W\d_]+)*\.?$")
_SEGMENT_SEPARATORS = re.compile(r"([-'’])")


class NameCase(Enum):
    PROPER = "Nome Próprio"
    UPPER = "MAIÚSCULAS"
    LOWER = "minúsculas"
    KEEP = "manter"


@dataclass(frozen=True)
class NameOptions:
    case: NameCase = NameCase.PROPER
    split_first_name: bool = False


def columns(options: NameOptions) -> tuple[str, ...]:
    if options.split_first_name:
        return ("Primeiro nome", "Restante do nome")
    return ("Nome",)


def proper_case(name: str) -> str:
    """Capitaliza um nome próprio mantendo partículas em minúsculas.

    Ex.: "MARIA DAS DORES" -> "Maria das Dores"; "ana-luíza d'ávila" ->
    "Ana-Luíza D'Ávila".
    """
    words = name.lower().split(" ")
    result = []
    for index, word in enumerate(words):
        if index > 0 and word in PARTICLES:
            result.append(word)
        elif word in ROMAN_NUMERALS:
            result.append(word.upper())
        else:
            parts = _SEGMENT_SEPARATORS.split(word)
            result.append("".join(part[:1].upper() + part[1:] for part in parts))
    return " ".join(result)


def normalize_name(value: str, options: NameOptions = NameOptions()) -> Record:
    width = len(columns(options))
    name = basic_clean(value)
    if not name:
        return Record.empty(value, width)
    if not _VALID_NAME.match(name):
        return Record.invalid(value, name, "contém números ou símbolos", width)

    if options.case is NameCase.PROPER:
        name = proper_case(name)
    elif options.case is NameCase.UPPER:
        name = name.upper()
    elif options.case is NameCase.LOWER:
        name = name.lower()

    if options.split_first_name:
        first, _, rest = name.partition(" ")
        return Record.valid(value, first, rest)
    return Record.valid(value, name)
