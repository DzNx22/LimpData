import pytest

from limpdata.core.email import EmailCase, EmailOptions, normalize_email
from limpdata.core.models import Status


@pytest.mark.parametrize(
    "value",
    [
        "joao@exemplo.com",
        "joao.silva+promo@exemplo.com.br",
        "a_b-c@sub.dominio.org",
        "x@a.io",
        "o'neil@exemplo.com",
    ],
)
def test_valid_emails(value):
    record = normalize_email(value)
    assert record.status is Status.VALID
    assert record.fields == (value.lower(),)


def test_trims_and_removes_invisible_characters():
    record = normalize_email("  ﻿Joao@Exemplo.COM​  ")
    assert record.fields == ("joao@exemplo.com",)


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        (EmailCase.LOWER, "joao@exemplo.com"),
        (EmailCase.UPPER, "JOAO@EXEMPLO.COM"),
        (EmailCase.KEEP, "Joao@Exemplo.com"),
    ],
)
def test_case_options(case, expected):
    assert normalize_email("Joao@Exemplo.com", EmailOptions(case=case)).fields == (expected,)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("joao exemplo@x.com", "contém espaços"),
        ("joaoexemplo.com", "exatamente um @"),
        ("joao@@exemplo.com", "exatamente um @"),
        ("joao@exemplo", "formato inválido"),
        ("joao@exemplo.c", "formato inválido"),
        ("joao..silva@exemplo.com", "formato inválido"),
        (".joao@exemplo.com", "formato inválido"),
        ("joao@-exemplo.com", "formato inválido"),
        ("joao@exemplo..com", "formato inválido"),
        ("joão@exemplo.com", "formato inválido"),
        ("@exemplo.com", "formato inválido"),
        ("a" * 65 + "@exemplo.com", "muito longa"),
        ("a@" + "b" * 250 + ".com", "muito longo"),
    ],
)
def test_invalid_emails_are_kept_with_reason(value, message):
    record = normalize_email(value)
    assert record.status is Status.INVALID
    assert message in record.message
    assert record.fields == (value,)  # valor mantido, sem alteração de caixa


def test_local_part_length_limit_is_inclusive():
    assert normalize_email("a" * 64 + "@exemplo.com").status is Status.VALID


@pytest.mark.parametrize("value", ["", "   ", "​ "])
def test_empty(value):
    assert normalize_email(value).status is Status.EMPTY
