"""Painéis de opções de cada tipo de dado.

Cada painel traduz os controles da tela para as opções do módulo de
normalização correspondente em `limpdata.core`.
"""

from __future__ import annotations

from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from limpdata.core import cpf, email, name, text
from limpdata.core.pipeline import Normalizer


class OptionsPanel(QWidget):
    """Base dos painéis: emite `changed` sempre que uma opção muda."""

    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.form = QVBoxLayout(self)
        self.form.setContentsMargins(0, 0, 0, 0)
        self.form.setSpacing(4)

    def normalizer(self) -> Normalizer:
        raise NotImplementedError

    def columns(self) -> tuple[str, ...]:
        raise NotImplementedError

    def drop_empty(self) -> bool:
        return False

    def _checkbox(self, label: str, checked: bool, tooltip: str = "") -> QCheckBox:
        box = QCheckBox(label)
        box.setChecked(checked)
        box.setToolTip(tooltip)
        box.toggled.connect(self.changed)
        self.form.addWidget(box)
        return box

    def _label(self, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("formLabel")
        self.form.addWidget(label)

    def _enum_combo(self, label: str, enum_type) -> QComboBox:
        combo = QComboBox()
        for member in enum_type:
            combo.addItem(member.value, member)
        combo.currentIndexChanged.connect(self.changed)
        self._label(label)
        self.form.addWidget(combo)
        return combo


class TextPanel(OptionsPanel):
    def __init__(self) -> None:
        super().__init__()
        self.trim = self._checkbox("Remover espaços no início e no fim", True)
        self.collapse = self._checkbox("Trocar espaços repetidos por um só", True)
        self.invisible = self._checkbox(
            "Remover caracteres invisíveis",
            True,
            "Espaço de largura zero, BOM, caracteres de controle etc. "
            "Espaços não separáveis viram espaços comuns.",
        )
        self.remove_empty = self._checkbox(
            "Remover linhas vazias",
            False,
            "Atenção: o resultado terá menos linhas que a entrada.",
        )

    def normalizer(self) -> Normalizer:
        options = text.TextOptions(
            trim=self.trim.isChecked(),
            collapse_spaces=self.collapse.isChecked(),
            remove_invisible=self.invisible.isChecked(),
        )
        return partial(text.normalize_text, options=options)

    def columns(self) -> tuple[str, ...]:
        return text.COLUMNS

    def drop_empty(self) -> bool:
        return self.remove_empty.isChecked()


class EmailPanel(OptionsPanel):
    def __init__(self) -> None:
        super().__init__()
        self.case = self._enum_combo("Letras", email.EmailCase)

    def normalizer(self) -> Normalizer:
        options = email.EmailOptions(case=self.case.currentData())
        return partial(email.normalize_email, options=options)

    def columns(self) -> tuple[str, ...]:
        return email.COLUMNS


class NamePanel(OptionsPanel):
    def __init__(self) -> None:
        super().__init__()
        self.case = self._enum_combo("Letras", name.NameCase)
        self.split = self._checkbox(
            "Separar primeiro nome do restante",
            False,
            "Gera duas colunas separadas por tabulação.",
        )

    def _options(self) -> name.NameOptions:
        return name.NameOptions(
            case=self.case.currentData(), split_first_name=self.split.isChecked()
        )

    def normalizer(self) -> Normalizer:
        return partial(name.normalize_name, options=self._options())

    def columns(self) -> tuple[str, ...]:
        return name.columns(self._options())


class CpfPanel(OptionsPanel):
    def __init__(self) -> None:
        super().__init__()
        self.formatted = QRadioButton("Formatado (000.000.000-00)")
        self.digits = QRadioButton("Somente dígitos")
        self.formatted.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self.formatted)
        group.addButton(self.digits)
        group.buttonToggled.connect(self.changed)
        self._label("Saída")
        self.form.addWidget(self.formatted)
        self.form.addWidget(self.digits)
        self.pad = self._checkbox(
            "Completar zeros à esquerda",
            True,
            "Recupera CPFs que a planilha salvou como número e perderam os "
            "zeros iniciais (8 a 10 dígitos).",
        )

    def normalizer(self) -> Normalizer:
        options = cpf.CpfOptions(
            formatted=self.formatted.isChecked(), pad_zeros=self.pad.isChecked()
        )
        return partial(cpf.normalize_cpf, options=options)

    def columns(self) -> tuple[str, ...]:
        return cpf.COLUMNS


# Ordem em que os tipos aparecem na tela.
PANELS: list[tuple[str, type[OptionsPanel]]] = [
    ("Limpeza geral", TextPanel),
    ("E-mail", EmailPanel),
    ("Nome", NamePanel),
    ("CPF", CpfPanel),
]
