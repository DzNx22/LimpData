"""Modelo de tabela para a prévia dos resultados.

Mostra só o que será copiado. O status aparece pela cor da linha; a coluna
"Observação" só existe quando algum registro precisa de explicação.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from limpdata.core.models import Record, Status
from limpdata.gui.theme import LIGHT, Palette

NOTE_HEADER = "Observação"


class ResultModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self._records: list[Record] = []
        self._headers: tuple[str, ...] = ()
        self._has_notes = False
        self._palette = LIGHT

    def set_palette(self, palette: Palette) -> None:
        self.beginResetModel()
        self._palette = palette
        self.endResetModel()

    def set_result(self, records: list[Record], columns: tuple[str, ...]) -> None:
        self.beginResetModel()
        self._records = records
        self._has_notes = any(r.status is Status.INVALID for r in records)
        self._headers = (*columns, NOTE_HEADER) if self._has_notes else columns
        self.endResetModel()

    def records(self) -> list[Record]:
        return self._records

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._records)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._headers)

    def _is_note(self, column: int) -> bool:
        return self._has_notes and column == len(self._headers) - 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        record = self._records[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if self._is_note(column):
                return record.message if record.status is Status.INVALID else ""
            return record.fields[column]
        if role == Qt.ToolTipRole and record.status is not Status.VALID:
            return record.message or "Linha vazia"
        if role == Qt.BackgroundRole:
            if record.status is Status.INVALID:
                return self._palette.invalid_bg
            if record.status is Status.EMPTY:
                return self._palette.empty_bg
        if role == Qt.ForegroundRole and self._is_note(column):
            return QColor(self._palette.error)
        return None

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1
