"""Limpeza geral de texto."""

from dataclasses import dataclass

from limpdata.core.models import Record
from limpdata.core.textutils import collapse_spaces, remove_invisible

COLUMNS = ("Texto",)


@dataclass(frozen=True)
class TextOptions:
    trim: bool = True
    collapse_spaces: bool = True
    remove_invisible: bool = True


def normalize_text(value: str, options: TextOptions = TextOptions()) -> Record:
    result = value
    if options.remove_invisible:
        result = remove_invisible(result)
    if options.collapse_spaces:
        result = collapse_spaces(result)
    if options.trim:
        result = result.strip()
    if not result.strip():
        return Record.empty(value)
    return Record.valid(value, result)
