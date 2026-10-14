"""Teste de fumaça da interface, executado sem abrir janelas (modo offscreen)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
from PySide6.QtCore import Qt  # noqa: E402

from limpdata.gui.main_window import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def window(app):
    window = MainWindow()
    yield window
    window.close()


def select_type(window, label):
    window.type_combo.setCurrentIndex(window.type_combo.findText(label))


def test_processes_and_copies_cpf(window):
    select_type(window, "CPF")
    window.input.setPlainText("52998224725\r\n\r\n123\r\n")
    window.process()

    assert window.model.rowCount() == 3
    assert window.clipboard_text() == "529.982.247-25\n\n123"
    assert "Processados: 3" in window.summary_label.text()
    assert window.legend["invalid"].text() == "1 inválido"
    # Só o resultado e a observação (há um inválido); sem "Original"/"Status".
    assert window.model.columnCount() == 2
    assert window.model.headerData(1, Qt.Horizontal) == "Observação"


def test_name_split_produces_two_columns(window):
    select_type(window, "Nome")
    window.current_panel().split.setChecked(True)
    window.input.setPlainText("MARIA DAS DORES")
    window.process()

    assert window.model.columnCount() == 2  # tudo válido: sem observação
    assert window.clipboard_text() == "Maria\tdas Dores"


def test_status_column_and_pending_changes(window):
    select_type(window, "E-mail")
    window.include_status.setChecked(True)
    window.input.setPlainText("A@X.COM")  # sem chamar process(): timer pendente
    assert window.clipboard_text() == "a@x.com\tválido"


def test_copy_button_disabled_without_data(window):
    window.input.clear()
    window.process()
    assert not window.copy_button.isEnabled()


def test_theme_toggle(window):
    window.apply_theme("light")
    window.toggle_theme()
    assert window._palette.name == "dark"
    window.toggle_theme()
    assert window._palette.name == "light"
