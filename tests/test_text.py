import pytest

from limpdata.core.models import Status
from limpdata.core.text import TextOptions, normalize_text
from limpdata.core.textutils import basic_clean, remove_invisible


def test_default_cleanup():
    record = normalize_text("  ﻿Produto​   azul  grande  ")
    assert record.status is Status.VALID
    assert record.fields == ("Produto azul grande",)


@pytest.mark.parametrize(
    "char", ["​", "‌", "‍", "⁠", "﻿", "­", "\x00", "\x07"]
)
def test_removes_invisible_characters(char):
    assert remove_invisible(f"a{char}b") == "ab"


def test_special_spaces_become_regular_spaces():
    assert remove_invisible("a b c　d") == "a b c d"


def test_options_can_be_disabled():
    options = TextOptions(trim=False, collapse_spaces=False, remove_invisible=False)
    value = "  a​  b  "
    assert normalize_text(value, options).fields == (value,)


def test_only_trim():
    options = TextOptions(collapse_spaces=False, remove_invisible=False)
    assert normalize_text("  a   b  ", options).fields == ("a   b",)


@pytest.mark.parametrize("value", ["", " ", "   ​ ", " "])
def test_empty(value):
    assert normalize_text(value).status is Status.EMPTY


def test_whitespace_only_is_empty_even_without_trim():
    assert normalize_text("   ", TextOptions(trim=False)).status is Status.EMPTY


def test_basic_clean():
    assert basic_clean("​  a    b ") == "a b"
