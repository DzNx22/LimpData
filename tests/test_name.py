import pytest

from limpdata.core.models import Status
from limpdata.core.name import NameCase, NameOptions, normalize_name, proper_case


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("MARIA DAS DORES", "Maria das Dores"),
        ("joão da silva e souza", "João da Silva e Souza"),
        ("ANA DE SOUZA DOS SANTOS", "Ana de Souza dos Santos"),
        ("da silva", "Da Silva"),  # partícula no início é capitalizada
        ("ana-luíza d'ávila", "Ana-Luíza D'Ávila"),
        ("PEDRO II", "Pedro II"),
        ("ÉRICA ÇARDOSO", "Érica Çardoso"),
    ],
)
def test_proper_case(value, expected):
    assert proper_case(value) == expected


def test_cleans_spaces_and_invisible_characters():
    record = normalize_name("  maria    das​   dores ")
    assert record.fields == ("Maria das Dores",)


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        (NameCase.UPPER, "MARIA DAS DORES"),
        (NameCase.LOWER, "maria das dores"),
        (NameCase.KEEP, "maria DAS Dores"),
    ],
)
def test_case_options(case, expected):
    assert normalize_name("maria DAS Dores", NameOptions(case=case)).fields == (expected,)


def test_split_first_name():
    options = NameOptions(split_first_name=True)
    assert normalize_name("maria das dores", options).fields == ("Maria", "das Dores")
    assert normalize_name("Cher", options).fields == ("Cher", "")


def test_split_keeps_column_count_for_invalid_and_empty():
    options = NameOptions(split_first_name=True)
    assert normalize_name("", options).fields == ("", "")
    invalid = normalize_name("Maria 123", options)
    assert invalid.status is Status.INVALID
    assert invalid.fields == ("Maria 123", "")


@pytest.mark.parametrize("value", ["Maria 2", "joao@x.com", "Ana_Silva", "#nome", "-", "Ana--"])
def test_invalid_names(value):
    record = normalize_name(value)
    assert record.status is Status.INVALID
    assert record.fields == (value,)


def test_accepts_abbreviations():
    assert normalize_name("JOSÉ A. SILVA JR.").fields == ("José A. Silva Jr.",)


def test_invalid_long_input_is_fast():
    # Garante que a expressão regular não sofre backtracking exponencial.
    assert normalize_name("a" + "-" * 5000 + "1").status is Status.INVALID


def test_empty():
    assert normalize_name(" \t ").status is Status.EMPTY
