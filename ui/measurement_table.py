"""Measurement Table View & Editor.

Features two-way synchronization with the 2D Room Plan,
inline editing with validation, and multi-language header translation.
"""

from __future__ import annotations
from typing import Optional, List
from PySide6.QtCore import Qt, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QHeaderView,
    QMessageBox,
    QLabel,
    QAbstractItemView,
)

from models.project import LuminationProject
from models.measurement import MeasurementPoint
from i18n.translations import tr, TranslationManager


class MeasurementTableModel(QAbstractTableModel):
    """Data model for the measurement table."""

    def __init__(self, project: Optional[LuminationProject] = None) -> None:
        super().__init__()
        self.project = project

    def get_columns(self) -> List[str]:
        return [
            tr("col_point_id"),
            tr("col_x"),
            tr("col_y"),
            tr("col_lux"),
            tr("col_expected"),
            tr("col_delta"),
            tr("col_time"),
            tr("col_notes"),
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.project.points) if self.project else 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.get_columns())

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            cols = self.get_columns()
            if section < len(cols):
                return cols[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not self.project or not index.isValid():
            return None

        p = self.project.points[index.row()]
        col = index.column()

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == 0:
                return p.id
            elif col == 1:
                return f"{p.x:.3f}" if role == Qt.ItemDataRole.DisplayRole else p.x
            elif col == 2:
                return f"{p.y:.3f}" if role == Qt.ItemDataRole.DisplayRole else p.y
            elif col == 3:
                return f"{p.lux:.1f}" if p.lux is not None else ""
            elif col == 4:
                return f"{p.expected_lux:.1f}" if p.expected_lux is not None else ""
            elif col == 5:
                return f"{p.delta_lux:+.1f}" if p.delta_lux is not None else ""
            elif col == 6:
                return p.timestamp or ""
            elif col == 7:
                return p.notes

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (1, 2, 3, 4, 5):
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        # Allow editing lux, expected, and notes
        if index.column() in (3, 4, 7):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not self.project or not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        p = self.project.points[index.row()]
        col = index.column()

        try:
            if col == 3:  # Measured Lux
                val_str = str(value).strip()
                if not val_str:
                    p.clear_reading()
                else:
                    v = float(val_str)
                    if v < 0:
                        return False
                    p.record_reading(v, device_name="Table Input")
            elif col == 4:  # Expected Lux
                val_str = str(value).strip()
                p.expected_lux = float(val_str) if val_str else None
            elif col == 7:  # Notes
                p.notes = str(value).strip()
            else:
                return False

            self.project.mark_modified()
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        except ValueError:
            return False


class MeasurementTableWidget(QWidget):
    """Container widget holding the synchronized measurement table view."""

    point_selected = Signal(str)
    data_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.project: Optional[LuminationProject] = None
        self.model = MeasurementTableModel()

        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setDefaultSectionSize(22)
        self.table_view.setAlternatingRowColors(True)

        self.table_view.selectionModel().selectionChanged.connect(self._on_row_selected)
        self.model.dataChanged.connect(lambda: self.data_changed.emit())

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.table_view)

        TranslationManager.get_instance().language_changed.connect(self.retranslate_ui)

    def retranslate_ui(self) -> None:
        """Refresh headers when language changes."""
        self.model.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, self.model.columnCount() - 1)

    def set_project(self, project: LuminationProject) -> None:
        self.project = project
        self.model.project = project
        self.model.layoutChanged.emit()

    def refresh(self) -> None:
        self.model.layoutChanged.emit()

    def select_point(self, point_id: str) -> None:
        if not self.project:
            return
        for row_idx, p in enumerate(self.project.points):
            if p.id == point_id:
                idx = self.model.index(row_idx, 0)
                self.table_view.selectionModel().setCurrentIndex(
                    idx,
                    self.table_view.selectionModel().SelectionFlag.ClearAndSelect | self.table_view.selectionModel().SelectionFlag.Rows,
                )
                self.table_view.scrollTo(idx)
                break

    def _on_row_selected(self) -> None:
        if not self.project:
            return
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            if row < len(self.project.points):
                pt = self.project.points[row]
                self.point_selected.emit(pt.id)
