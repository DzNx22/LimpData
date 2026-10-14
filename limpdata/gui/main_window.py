"""Janela principal: entrada à esquerda, comandos no meio e resultado à direita."""

from __future__ import annotations

from PySide6.QtCore import QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QBrush, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from limpdata.core.models import Summary
from limpdata.core.pipeline import process, to_clipboard_text
from limpdata import __version__
from limpdata.gui import theme, titlebar
from limpdata.gui.option_panels import PANELS, OptionsPanel
from limpdata.gui.result_model import ResultModel

# Espera o usuário parar de digitar antes de reprocessar.
PROCESS_DELAY_MS = 250
COPY_FEEDBACK_MS = 2000
COMMANDS_WIDTH = 300


def _label(text: str, name: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName(name)
    return label


def _section_label(text: str, *, card_title: bool = False) -> QLabel:
    label = _label(text, "sectionLabel")
    if card_title:  # mesma altura do botão "Copiar", alinhando os três painéis
        label.setMinimumHeight(34)
    return label


class PaddedDelegate(QStyledItemDelegate):
    """Pinta o fundo de status na célula inteira e afasta o texto da borda."""

    PADDING = 8

    def paint(self, painter, option, index) -> None:
        background = index.data(Qt.BackgroundRole)
        if background is not None:
            painter.fillRect(option.rect, background)
        option = QStyleOptionViewItem(option)
        option.rect.adjust(self.PADDING, 0, -4, 0)
        super().paint(painter, option, index)

    def initStyleOption(self, option, index) -> None:
        super().initStyleOption(option, index)
        option.backgroundBrush = QBrush()  # já pintado em paint()


def _card() -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 12, 16, 16)
    layout.setSpacing(10)
    return card, layout


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LimpData")
        self.setWindowIcon(theme.app_icon())
        self.resize(1240, 720)
        self.setMinimumSize(960, 560)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(PROCESS_DELAY_MS)
        self._timer.timeout.connect(self.process)

        self._settings = QSettings("LimpData", "LimpData")
        self.model = ResultModel()
        self.setCentralWidget(self._build_ui())
        # O delegate padrão das listas suspensas desenha um quadro de menu no
        # item atual e ignora a folha de estilo; o comum segue o tema.
        for combo in self.findChildren(QComboBox):
            combo.setItemDelegate(QStyledItemDelegate(combo))
        self.apply_theme(self._settings.value("theme", theme.LIGHT.name))
        self._show_panel(0)

    # ----- construção da tela -------------------------------------------

    def _build_ui(self) -> QWidget:
        body = QHBoxLayout()
        body.setContentsMargins(20, 20, 20, 10)
        body.setSpacing(12)
        body.addWidget(self._build_input(), stretch=3)
        body.addWidget(self._build_commands())
        body.addWidget(self._build_result(), stretch=4)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(body, stretch=1)
        layout.addWidget(self._build_footer())
        root = QWidget()
        root.setObjectName("root")
        root.setLayout(layout)
        return root

    def _build_footer(self) -> QWidget:
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setIconSize(QSize(14, 14))
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.clicked.connect(self.toggle_theme)

        footer = QWidget()
        row = QHBoxLayout(footer)
        row.setContentsMargins(20, 0, 14, 8)
        row.addWidget(_label(f"Processamento 100% local · v{__version__}", "muted"))
        row.addStretch()
        row.addWidget(self.theme_button)
        return footer

    def _build_input(self) -> QWidget:
        self.input = QPlainTextEdit()
        self.input.setPlaceholderText(
            "Cole aqui uma coluna copiada do Excel ou do Google Sheets "
            "(um valor por linha)."
        )
        self.input.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.input.textChanged.connect(self._timer.start)

        paste = QPushButton("Colar")
        paste.setCursor(Qt.PointingHandCursor)
        paste.clicked.connect(self.paste_input)
        clear = QPushButton("Limpar")
        clear.setCursor(Qt.PointingHandCursor)
        clear.clicked.connect(self.input.clear)
        self.line_count = _label("", "muted")

        top = QHBoxLayout()
        top.addWidget(_section_label("Entrada", card_title=True))
        top.addStretch()
        top.addWidget(self.line_count)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addWidget(paste)
        buttons.addWidget(clear)
        buttons.addStretch()

        card, layout = _card()
        layout.addLayout(top)
        layout.addWidget(self.input, stretch=1)
        layout.addLayout(buttons)
        return card

    def _build_commands(self) -> QWidget:
        self.type_combo = QComboBox()
        self.type_combo.setCursor(Qt.PointingHandCursor)
        self.panels = QStackedWidget()
        self.panels.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        for label, panel_class in PANELS:
            panel = panel_class()
            panel.changed.connect(self.process)
            self.type_combo.addItem(label)
            self.panels.addWidget(panel)
        self.type_combo.currentIndexChanged.connect(self._show_panel)

        separator = QFrame()
        separator.setObjectName("separator")

        self.include_status = QCheckBox("Incluir coluna de status ao copiar")
        self.include_status.setToolTip(
            "Adiciona ao lado do resultado: válido, vazio ou inválido: motivo."
        )

        card, layout = _card()
        card.setFixedWidth(COMMANDS_WIDTH)
        layout.addWidget(_section_label("Tipo de dado", card_title=True))
        layout.addWidget(self.type_combo)
        layout.addSpacing(8)
        layout.addWidget(_section_label("Opções"))
        layout.addWidget(self.panels)
        layout.addStretch()
        layout.addWidget(separator)
        layout.addWidget(self.include_status)
        return card

    def _build_result(self) -> QWidget:
        self.copy_button = QPushButton("Copiar resultado")
        self.copy_button.setObjectName("primary")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self.copy_button.setToolTip("Ctrl+Shift+C")
        self.copy_button.clicked.connect(self.copy_result)
        self._copy_reset = QTimer(self)
        self._copy_reset.setSingleShot(True)
        self._copy_reset.timeout.connect(
            lambda: self.copy_button.setText("Copiar resultado")
        )

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setItemDelegate(PaddedDelegate(self.table))
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.verticalHeader().setHighlightSections(False)

        empty = _label("O resultado aparece aqui assim que você colar os dados.", "emptyState")
        empty.setAlignment(Qt.AlignCenter)
        empty.setWordWrap(True)
        self.result_stack = QStackedWidget()
        self.result_stack.addWidget(empty)
        self.result_stack.addWidget(self.table)

        legend_box = QWidget()
        legend_box.setObjectName("legend")
        legend = QHBoxLayout(legend_box)
        legend.setContentsMargins(0, 0, 0, 0)
        legend.setSpacing(6)
        self.legend: dict[str, QLabel] = {}
        self._legend_items: dict[str, list[QWidget]] = {}
        for key in _LEGEND:
            dot = QFrame()
            dot.setObjectName(f"dot_{key}")
            label = QLabel()
            self.legend[key] = label
            self._legend_items[key] = [dot, label]
            legend.addWidget(dot)
            legend.addWidget(label)
            legend.addSpacing(12)
        legend.addStretch()
        self.summary_label = _label("", "muted")
        legend.addWidget(self.summary_label)

        top = QHBoxLayout()
        top.addWidget(_section_label("Resultado", card_title=True))
        top.addStretch()
        top.addWidget(self.copy_button)

        card, layout = _card()
        layout.addLayout(top)
        layout.addWidget(self.result_stack, stretch=1)
        layout.addWidget(legend_box)
        return card

    # ----- tema ----------------------------------------------------------

    def apply_theme(self, name: str) -> None:
        palette = theme.THEMES.get(name, theme.LIGHT)
        self._palette = palette
        QApplication.instance().setStyleSheet(theme.stylesheet(palette))
        self.model.set_palette(palette)
        dark = palette is theme.DARK
        self.theme_button.setIcon(theme.icon("sun" if dark else "moon", palette))
        self.theme_button.setText("Modo claro" if dark else "Modo escuro")
        QApplication.styleHints().setColorScheme(
            Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light
        )
        titlebar.apply(self, palette, dark)
        self._settings.setValue("theme", palette.name)

    def toggle_theme(self) -> None:
        dark = self._palette is theme.DARK
        self.apply_theme(theme.LIGHT.name if dark else theme.DARK.name)

    # ----- ações ---------------------------------------------------------

    def _show_panel(self, index: int) -> None:
        # Painéis ocultos não contam no tamanho, para a área de opções
        # ter só a altura do painel visível.
        for i in range(self.panels.count()):
            vertical = QSizePolicy.Preferred if i == index else QSizePolicy.Ignored
            self.panels.widget(i).setSizePolicy(QSizePolicy.Preferred, vertical)
        self.panels.setCurrentIndex(index)
        self.process()

    def current_panel(self) -> OptionsPanel:
        return self.panels.currentWidget()

    def process(self) -> None:
        self._timer.stop()
        panel = self.current_panel()
        result = process(
            self.input.toPlainText(), panel.normalizer(), drop_empty=panel.drop_empty()
        )
        self.model.set_result(result.records, panel.columns())
        self.result_stack.setCurrentIndex(1 if result.records else 0)
        self._update_summary(result.summary)
        self.copy_button.setEnabled(bool(result.records))

    def _update_summary(self, summary: Summary) -> None:
        total = summary.total
        self.line_count.setText(f"{total} linha{'s' if total != 1 else ''}" if total else "")
        counts = {"valid": summary.valid, "invalid": summary.invalid, "empty": summary.empty}
        for key, label in self.legend.items():
            label.setText(legend_text(key, counts[key]))
            for widget in self._legend_items[key]:
                widget.setVisible(bool(counts[key]))
        self.summary_label.setText(format_summary(summary))

    def clipboard_text(self) -> str:
        if self._timer.isActive():  # garante que o resultado está atualizado
            self.process()
        return to_clipboard_text(
            self.model.records(), include_status=self.include_status.isChecked()
        )

    def copy_result(self) -> None:
        QGuiApplication.clipboard().setText(self.clipboard_text())
        count = len(self.model.records())
        s = "s" if count != 1 else ""
        self.copy_button.setText(f"✓ {count} linha{s} copiada{s}")
        self._copy_reset.start(COPY_FEEDBACK_MS)

    def paste_input(self) -> None:
        self.input.setPlainText(QGuiApplication.clipboard().text())
        self.process()


_LEGEND = {
    "valid": ("válido", "válidos"),
    "invalid": ("inválido", "inválidos"),
    "empty": ("vazio", "vazios"),
}


def legend_text(key: str, count: int) -> str:
    singular, plural = _LEGEND[key]
    return f"{count} {singular if count == 1 else plural}"


def format_summary(summary: Summary) -> str:
    """Texto secundário da legenda: total processado e duplicados."""
    if not summary.total:
        return ""
    parts = [f"Processados: {summary.total}"]
    if summary.duplicates:
        parts.append(f"Duplicados: {summary.duplicates}")
    return "  ·  ".join(parts)
