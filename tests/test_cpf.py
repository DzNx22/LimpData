import pytest

from limpdata.core.cpf import CpfOptions, check_digits, normalize_cpf
from limpdata.core.models import Status

DIGITS = CpfOptions(formatted=False)


@pytest.mark.parametrize(
    "value",
    ["529.982.247-25", "52998224725", " 529.982.247-25 ", "529 982 247 25", "529982247-25"],
)
def test_valid_cpf_with_or_without_punctuation(value):
    record = normalize_cpf(value)
    assert record.status is Status.VALID
    assert record.fields == ("529.982.247-25",)


def test_digits_only_output():
    assert normalize_cpf("111.444.777-35", DIGITS).fields == ("11144477735",)


def test_check_digits():
    assert check_digits("529982247") == "25"
    assert check_digits("012345678") == "90"


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("529.982.247-24", "dígitos verificadores não conferem"),
        ("111.111.111-11", "todos os dígitos são iguais"),
        ("000.000.000-00", "todos os dígitos são iguais"),
        ("5299822472", "possui 10 dígitos"),  # pontuado não é completado
        ("529.982.247-2", "possui 10 dígitos"),
        ("529.982.247-255", "possui 12 dígitos"),
        ("529.982.247-2a", "não numéricos"),
        ("1,23457E+10", "não numéricos"),
    ],
)
def test_invalid_cpf_keeps_value_and_reason(value, message):
    record = normalize_cpf(value, CpfOptions(pad_zeros=False))
    assert record.status is Status.INVALID
    assert message in record.message
    assert record.fields == (value,)


def test_pads_leading_zeros_lost_by_spreadsheet():
    assert normalize_cpf("1234567890").fields == ("012.345.678-90",)
    assert normalize_cpf("123456797").fields == ("001.234.567-97",)


def test_padding_can_be_disabled():
    assert normalize_cpf("1234567890", CpfOptions(pad_zeros=False)).status is Status.INVALID


def test_padding_ignores_short_or_punctuated_values():
    # "191" completado viraria 000.000.001-91, que é um CPF válido.
    assert normalize_cpf("191").status is Status.INVALID
    assert normalize_cpf("12.345.678-90").status is Status.INVALID


@pytest.mark.parametrize("value", ["", "   ", "​", "\t"])
def test_empty(value):
    record = normalize_cpf(value)
    assert record.status is Status.EMPTY
    assert record.fields == ("",)
