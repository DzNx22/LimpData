"""Estruturas de dados compartilhadas pelos normalizadores."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    VALID = "válido"
    INVALID = "inválido"
    EMPTY = "vazio"


@dataclass(frozen=True)
class Record:
    """Resultado da normalização de uma única linha.

    `fields` sempre tem a mesma quantidade de colunas para um mesmo tipo de
    normalização, inclusive em registros inválidos ou vazios, para que a
    colagem na planilha não desalinhe as linhas.
    """

    original: str
    fields: tuple[str, ...]
    status: Status
    message: str = ""

    @classmethod
    def valid(cls, original: str, *fields: str) -> Record:
        return cls(original, tuple(fields), Status.VALID)

    @classmethod
    def invalid(cls, original: str, value: str, message: str, columns: int = 1) -> Record:
        """Registro inválido: mantém o valor (apenas limpo) para não perdê-lo."""
        return cls(original, _pad((value,), columns), Status.INVALID, message)

    @classmethod
    def empty(cls, original: str, columns: int = 1) -> Record:
        return cls(original, _pad((), columns), Status.EMPTY)


def _pad(values: tuple[str, ...], columns: int) -> tuple[str, ...]:
    return values + ("",) * (columns - len(values))


@dataclass
class Summary:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    empty: int = 0
    duplicates: int = 0


@dataclass
class Result:
    records: list[Record] = field(default_factory=list)
    summary: Summary = field(default_factory=Summary)
