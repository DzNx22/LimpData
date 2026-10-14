from functools import partial

import pytest

from limpdata.core.cpf import normalize_cpf
from limpdata.core.email import normalize_email
from limpdata.core.models import Record, Status
from limpdata.core.name import NameOptions, normalize_name
from limpdata.core.pipeline import process, split_lines, to_clipboard_text
from limpdata.core.text import normalize_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", []),
        ("a", ["a"]),
        ("a\r\nb\r\n", ["a", "b"]),  # formato do Excel
        ("a\nb\n", ["a", "b"]),  # formato do Google Sheets
        ("a\rb", ["a", "b"]),
        ("a\n\nb", ["a", "", "b"]),
        ("\n", [""]),
        ("a\n\n", ["a", ""]),
    ],
)
def test_split_lines(text, expected):
    assert split_lines(text) == expected


def test_preserves_order_count_and_duplicates():
    text = "B@X.COM\n\nnao-e-email\nb@x.com\na@x.com\n"
    result = process(text, normalize_email)

    assert [r.fields[0] for r in result.records] == [
        "b@x.com",
        "",
        "nao-e-email",
        "b@x.com",
        "a@x.com",
    ]
    summary = result.summary
    assert (summary.total, summary.valid, summary.invalid, summary.empty) == (5, 3, 1, 1)
    assert summary.duplicates == 1


def test_invalid_records_are_never_dropped():
    result = process("123\n529.982.247-25\nabc", normalize_cpf, drop_empty=True)
    assert [r.status for r in result.records] == [
        Status.INVALID,
        Status.VALID,
        Status.INVALID,
    ]


def test_drop_empty_removes_only_empty_lines_but_counts_them():
    result = process("a\n \n\nb", normalize_text, drop_empty=True)
    assert [r.fields for r in result.records] == [("a",), ("b",)]
    assert result.summary.total == 4
    assert result.summary.empty == 2


def test_empty_input():
    result = process("", normalize_text)
    assert result.records == []
    assert result.summary.total == 0
    assert to_clipboard_text(result.records) == ""


def test_clipboard_text_uses_tabs_between_columns():
    normalizer = partial(normalize_name, options=NameOptions(split_first_name=True))
    result = process("maria das dores\n\nJOSÉ\nAna 1", normalizer)
    assert to_clipboard_text(result.records) == (
        "Maria\tdas Dores\n\t\nJosé\t\nAna 1\t"
    )


def test_clipboard_text_with_status_column():
    result = process("a@x.com\n\nerrado", normalize_email)
    assert to_clipboard_text(result.records, include_status=True) == (
        "a@x.com\tválido\n\tvazio\nerrado\tinválido: deve conter exatamente um @"
    )


def test_clipboard_text_never_breaks_rows():
    # Um campo com tabulação ou quebra de linha desalinharia a planilha.
    record = Record.valid("x", "a\tb\nc")
    assert to_clipboard_text([record]) == "a b c"


def test_large_input():
    lines = [f"Pessoa {i}" if i % 3 else "" for i in range(30_000)]
    result = process("\n".join(lines), normalize_name)
    assert len(result.records) == 30_000
    assert result.summary.empty == 10_000
