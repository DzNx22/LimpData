"""Processamento de várias linhas e geração do texto para a área de transferência."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable

from limpdata.core.models import Record, Result, Status

Normalizer = Callable[[str], Record]

_LINE_BREAK = re.compile(r"\r\n|\r|\n")


def split_lines(text: str) -> list[str]:
    """Divide o texto colado em linhas, preservando linhas vazias.

    O Excel e o Google Sheets terminam a cópia com uma quebra de linha; ela é
    ignorada para não gerar um registro vazio a mais no final.
    """
    if not text:
        return []
    lines = _LINE_BREAK.split(text)
    if lines[-1] == "":
        lines.pop()
    return lines


def process(text: str, normalizer: Normalizer, *, drop_empty: bool = False) -> Result:
    """Normaliza cada linha, mantendo ordem e quantidade de registros.

    Registros inválidos nunca são descartados. Com `drop_empty=True`, apenas as
    linhas vazias são omitidas do resultado (mas continuam sendo contadas).
    """
    result = Result()
    summary = result.summary
    seen: set[tuple[str, ...]] = set()

    for line in split_lines(text):
        record = normalizer(line)
        summary.total += 1
        if record.status is Status.EMPTY:
            summary.empty += 1
            if drop_empty:
                continue
        elif record.status is Status.INVALID:
            summary.invalid += 1
        else:
            summary.valid += 1
            if record.fields in seen:
                summary.duplicates += 1
            seen.add(record.fields)
        result.records.append(record)
    return result


def status_text(record: Record) -> str:
    if record.status is Status.INVALID and record.message:
        return f"{record.status.value}: {record.message}"
    return record.status.value


def to_clipboard_text(records: Iterable[Record], *, include_status: bool = False) -> str:
    """Gera texto pronto para colar em planilhas: colunas separadas por
    tabulação e uma linha por registro."""
    rows = []
    for record in records:
        fields = list(record.fields)
        if include_status:
            fields.append(status_text(record))
        # Tabulações ou quebras dentro de um campo desalinhariam a planilha.
        rows.append("\t".join(_single_cell(value) for value in fields))
    return "\n".join(rows)


def _single_cell(value: str) -> str:
    return _LINE_BREAK.sub(" ", value).replace("\t", " ")
