"""Barra de título nativa do Windows acompanhando o tema do app.

Windows 10 (build 19041+): alterna entre barra clara e escura.
Windows 11: além disso, pinta a barra com a cor de fundo do app.
Em outros sistemas, ou se a chamada falhar, nada acontece.
"""

from __future__ import annotations

import ctypes
import sys

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from limpdata.gui.theme import Palette

_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_CAPTION_COLOR = 35
_DWMWA_TEXT_COLOR = 36


def _colorref(hex_color: str) -> int:
    color = QColor(hex_color)
    return color.red() | color.green() << 8 | color.blue() << 16  # 0x00BBGGRR


def apply(window: QWidget, palette: Palette, dark: bool) -> None:
    if sys.platform != "win32":
        return
    try:
        set_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    except (AttributeError, OSError):
        return
    hwnd = ctypes.c_void_p(int(window.winId()))
    for attribute, value in (
        (_DWMWA_USE_IMMERSIVE_DARK_MODE, int(dark)),
        (_DWMWA_CAPTION_COLOR, _colorref(palette.bg)),
        (_DWMWA_TEXT_COLOR, _colorref(palette.text)),
    ):
        data = ctypes.c_int(value)
        # Atributos não suportados (ex.: cor no Windows 10) só retornam erro.
        set_attribute(hwnd, attribute, ctypes.byref(data), ctypes.sizeof(data))
