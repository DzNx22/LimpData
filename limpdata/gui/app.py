"""Ponto de entrada da aplicação gráfica."""

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from limpdata import __version__
from limpdata.gui import theme
from limpdata.gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("LimpData")
    app.setApplicationVersion(__version__)
    # Fusion respeita a folha de estilo por inteiro, sem a aparência nativa do Windows.
    app.setStyle("Fusion")
    theme.load_fonts()
    app.setFont(QFont(theme.FONT, 10))
    app.setWindowIcon(theme.app_icon())
    window = MainWindow()
    window.show()
    return app.exec()
