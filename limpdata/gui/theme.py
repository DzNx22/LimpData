"""Identidade visual: cores, fonte e folha de estilo (QSS) dos temas claro e escuro.

Visual sóbrio de software de trabalho: tons neutros, cantos discretos,
uma única fonte (Inter) e o azul da logo da Limp Data como destaque.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QColor, QFontDatabase, QIcon

ASSETS = Path(__file__).parent / "assets"

# Azul da logo da Limp Data: cor de destaque nos dois temas.
ACCENT = "#2563EB"
ACCENT_HOVER = "#1D4ED8"

FONT = "Inter"


@dataclass(frozen=True)
class Palette:
    name: str
    bg: str
    surface: str
    field: str
    line: str
    line_strong: str
    text: str
    text_2: str
    text_3: str
    success: str
    error: str
    accent_soft: str  # fundo de seleção
    invalid_bg: QColor
    empty_bg: QColor


LIGHT = Palette(
    name="light",
    bg="#F4F5F7",
    surface="#FFFFFF",
    field="#FFFFFF",
    line="#E4E4E7",
    line_strong="#D4D4D8",
    text="#18181B",
    text_2="#52525B",
    text_3="#71717A",
    success="#16A34A",
    error="#DC2626",
    accent_soft="#DBE6FD",
    invalid_bg=QColor(220, 38, 38, 22),
    empty_bg=QColor(113, 113, 122, 18),
)

DARK = Palette(
    name="dark",
    bg="#121214",
    surface="#1A1A1D",
    field="#1A1A1D",
    line="#2A2A2E",
    line_strong="#3F3F46",
    text="#E4E4E7",
    text_2="#A1A1AA",
    text_3="#71717A",
    success="#22C55E",
    error="#F87171",
    accent_soft="#1E3A8A",
    invalid_bg=QColor(248, 113, 113, 30),
    empty_bg=QColor(161, 161, 170, 18),
)

THEMES = {LIGHT.name: LIGHT, DARK.name: DARK}


def load_fonts() -> None:
    for path in sorted((ASSETS / "fonts").glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(path))


def app_icon() -> QIcon:
    """Marca da Limp Data (PNG, com a SVG como alternativa)."""
    png = ASSETS / "logo-mark.png"
    return QIcon(str(png if png.exists() else ASSETS / "logo-mark.svg"))


def icon(name: str, palette: Palette) -> QIcon:
    return QIcon(str(ASSETS / "icons" / f"{name}-{palette.name}.svg"))


def stylesheet(p: Palette) -> str:
    check = (ASSETS / "icons" / "check.svg").as_posix()
    chevron = (ASSETS / "icons" / f"chevron-{p.name}.svg").as_posix()
    return f"""
* {{
    font-family: "{FONT}";
    font-size: 9.5pt;
    color: {p.text};
    outline: none;
}}
QMainWindow, #root {{ background: {p.bg}; }}
QToolTip {{
    background: {p.surface}; color: {p.text}; border: 1px solid {p.line_strong};
    padding: 4px 8px; border-radius: 4px;
}}

/* ---------- Rodapé ---------- */
QPushButton#themeButton {{
    background: transparent; border: 1px solid transparent; border-radius: 6px;
    color: {p.text_3}; font-weight: 400; min-height: 26px; padding: 0 8px;
}}
QPushButton#themeButton:hover {{ background: {p.surface}; border-color: {p.line}; color: {p.text}; }}

/* ---------- Painéis ---------- */
#card {{
    background: {p.surface}; border: 1px solid {p.line}; border-radius: 8px;
}}
#sectionLabel {{ font-weight: 600; font-size: 10pt; }}
#muted {{ color: {p.text_3}; }}
#emptyState {{ color: {p.text_3}; }}
#separator {{ background: {p.line}; max-height: 1px; min-height: 1px; border: none; }}

/* ---------- Campos ---------- */
QPlainTextEdit, QTableView {{
    background: {p.field}; border: 1px solid {p.line}; border-radius: 6px;
    selection-background-color: {p.accent_soft}; selection-color: {p.text};
}}
QPlainTextEdit {{ padding: 6px 4px; }}
QPlainTextEdit:focus {{ border-color: {ACCENT}; }}

QComboBox {{
    background: {p.field}; border: 1px solid {p.line_strong}; border-radius: 6px;
    padding: 0 10px; min-height: 32px;
}}
QComboBox:hover {{ border-color: {p.text_3}; }}
QComboBox:focus, QComboBox:on {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{ image: url("{chevron}"); width: 14px; height: 14px; }}
/* A lista suspensa abre numa janela própria, sem transparência: cantos
   arredondados nela deixariam pontas pretas. Por isso fica reta. */
QComboBox QAbstractItemView {{
    background: {p.surface}; border: 1px solid {p.line_strong}; border-radius: 0;
    padding: 4px; selection-background-color: {p.accent_soft}; selection-color: {p.text};
}}
QComboBox QAbstractItemView {{ outline: 0; }}
QComboBox QAbstractItemView::item {{
    min-height: 28px; padding: 0 6px; border: none; border-radius: 4px;
}}
QComboBox QAbstractItemView::item:hover {{ background: {p.bg}; }}
QComboBox QAbstractItemView::item:selected {{ background: {p.accent_soft}; color: {p.text}; }}

/* ---------- Botões ---------- */
QPushButton {{
    font-weight: 500; min-height: 32px; padding: 0 14px; border-radius: 6px;
    background: {p.surface}; border: 1px solid {p.line_strong};
}}
QPushButton:hover {{ background: {p.bg}; border-color: {p.text_3}; }}
QPushButton:disabled {{ color: {p.text_3}; border-color: {p.line}; }}
QPushButton#primary {{
    background: {ACCENT}; border: 1px solid {ACCENT}; color: #FFFFFF; font-weight: 600;
}}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; border-color: {ACCENT_HOVER}; }}
QPushButton#primary:disabled {{
    background: {p.line}; border-color: {p.line}; color: {p.text_3};
}}

/* ---------- Opções ---------- */
QCheckBox, QRadioButton {{ spacing: 8px; padding: 2px 0; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 14px; height: 14px; background: {p.field}; border: 1px solid {p.line_strong};
}}
QCheckBox::indicator {{ border-radius: 3px; }}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {ACCENT}; }}
QCheckBox::indicator:checked {{
    background: {ACCENT}; border-color: {ACCENT}; image: url("{check}");
}}
QRadioButton::indicator:checked {{
    background: {p.field}; border: 4px solid {ACCENT}; width: 8px; height: 8px;
}}
#formLabel {{ color: {p.text_2}; padding-top: 4px; }}

/* ---------- Tabela de resultado ---------- */
QTableView {{ gridline-color: transparent; }}
QHeaderView {{ background: transparent; border: none; }}
QHeaderView::section {{
    background: transparent; color: {p.text_2}; border: none;
    border-bottom: 1px solid {p.line}; padding: 5px 8px; font-weight: 600;
}}
QHeaderView::section:vertical {{
    color: {p.text_3}; border-bottom: none; border-right: 1px solid {p.line};
    padding: 0 6px; font-weight: 400;
}}
QTableCornerButton::section {{
    background: transparent; border: none;
    border-bottom: 1px solid {p.line}; border-right: 1px solid {p.line};
}}

/* ---------- Legenda ---------- */
#legend QLabel {{ color: {p.text_2}; }}
#dot_valid, #dot_invalid, #dot_empty {{
    min-width: 8px; max-width: 8px; min-height: 8px; max-height: 8px; border-radius: 4px;
}}
#dot_valid {{ background: {p.success}; }}
#dot_invalid {{ background: {p.error}; }}
#dot_empty {{ background: {p.line_strong}; }}

/* ---------- Barras de rolagem finas ---------- */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle {{ background: {p.line_strong}; border-radius: 3px; min-height: 24px; min-width: 24px; }}
QScrollBar::handle:hover {{ background: {p.text_3}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""
