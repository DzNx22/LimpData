"""Funções básicas de limpeza de texto reutilizadas pelos demais módulos."""

import re
import unicodedata

_MULTIPLE_SPACES = re.compile(r" {2,}")


def remove_invisible(value: str) -> str:
    """Remove caracteres invisíveis e troca espaços especiais por espaço comum.

    - Remove caracteres de formatação (ex.: espaço de largura zero, BOM,
      hífen suave) e de controle, exceto a tabulação.
    - Converte espaços especiais (ex.: espaço não separável) em espaço comum.
    """
    chars = []
    for char in value:
        category = unicodedata.category(char)
        if char == "\t":
            chars.append(char)
        elif category in ("Cf", "Cc"):
            continue
        elif category in ("Zs", "Zl", "Zp"):
            chars.append(" ")
        else:
            chars.append(char)
    return "".join(chars)


def collapse_spaces(value: str) -> str:
    """Troca sequências de espaços por um único espaço."""
    return _MULTIPLE_SPACES.sub(" ", value)


def basic_clean(value: str) -> str:
    """Limpeza aplicada antes de qualquer normalização específica."""
    return collapse_spaces(remove_invisible(value)).strip()
