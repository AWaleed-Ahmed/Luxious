"""Survey / Measurement Mode Fast Entry Widget.

Optimized for real-world room walking workflow:
- Current point target tracking with coordinates
- High-efficiency Enter-to-advance entry (sequential walking traversal)
- Previous / Next navigation controls
- Survey progress indicator (e.g. 18 / 30 points completed)
- Non-destructive outlier warning alerts
- No emojis, clean readable typography
- Full i18n support (English, Romanian, German)
"""

from __future__ import annotations
from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QProgressBar,
    QFrame,
)

from models.project import LuminationProject
from models.measurement import MeasurementPoint
from analysis.outliers import evaluate_spatial_outliers
from i18n.translations import tr, TranslationManager


class SurveyModeWidget(QFrame):
    """Interactive top/bottom survey bar for physical walkthrough data entry.

    Signals:
        measurement_saved (str, float): Emitted when lux value is saved for a point (point_id, lux).
        point_navigated (str): Emitted when active point selection moves (point_id).
    """
    measurement_saved = Signal(str, float)
    point_navigated = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.project: Optional[LuminationProject] = None
        self.active_point_id: Optional[str] = None

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            SurveyModeWidget {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 10px;
            }
        """)

        # 1. Point Info & Target Indicator
        self.lbl_point_id = QLabel(f"{tr('survey_point')} --", self)
        self.lbl_point_id.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e3a8a;")

        self.lbl_coords = QLabel("(X: -- m, Y: -- m)", self)
        self.lbl_coords.setStyleSheet("font-size: 11px; color: #64748b;")

        # 2. Lux Entry SpinBox
        self.spin_lux = QDoubleSpinBox(self)
        self.spin_lux.setRange(0.0, 150000.0)
        self.spin_lux.setDecimals(1)
        self.spin_lux.setSingleStep(10.0)
        self.spin_lux.setSuffix(" lx")
        self.spin_lux.setMinimumWidth(110)
        self.spin_lux.setStyleSheet("font-size: 13px; font-weight: bold; padding: 3px 6px;")

        # 3. Action Buttons (No emojis, crisp readable text)
        self.btn_save_next = QPushButton(f"{tr('survey_save_next')} (Enter)", self)
        self.btn_save_next.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: bold;
                padding: 5px 12px;
                border-radius: 4px;
                border: 1px solid #1d4ed8;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_prev = QPushButton(tr("survey_prev"), self)
        self.btn_next = QPushButton(tr("survey_next"), self)
        self.btn_next_unmeasured = QPushButton(tr("survey_next_unmeasured"), self)

        self.btn_save_next.clicked.connect(self._save_and_advance)
        self.btn_prev.clicked.connect(self._go_previous)
        self.btn_next.clicked.connect(self._go_next)
        self.btn_next_unmeasured.clicked.connect(self._go_next_unmeasured)

        # Connect Enter key inside spinbox
        self.spin_lux.lineEdit().returnPressed.connect(self._save_and_advance)

        # 4. Progress bar & completion counter
        self.lbl_progress = QLabel(f"{tr('survey_progress')} 0 / 0 (0%)", self)
        self.lbl_progress.setStyleSheet("font-size: 11px; font-weight: 600; color: #334155;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumWidth(130)
        self.progress_bar.setMaximumHeight(14)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cbd5e1;
                border-radius: 3px;
                background-color: #f1f5f9;
            }
            QProgressBar::chunk {
                background-color: #16a34a;
                border-radius: 2px;
            }
        """)

        # 5. Outlier Alert Banner (hidden by default)
        self.lbl_outlier_warning = QLabel("", self)
        self.lbl_outlier_warning.setStyleSheet("""
            color: #b45309;
            background-color: #fef3c7;
            border: 1px solid #fde68a;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 600;
        """)
        self.lbl_outlier_warning.setVisible(False)

        # Layout Assembly
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(6)

        top_row.addWidget(self.lbl_point_id)
        top_row.addWidget(self.lbl_coords)
        top_row.addSpacing(6)
        self.lbl_reading_tag = QLabel(tr("survey_reading"), self)
        top_row.addWidget(self.lbl_reading_tag)
        top_row.addWidget(self.spin_lux)
        top_row.addWidget(self.btn_save_next)
        top_row.addWidget(self.btn_prev)
        top_row.addWidget(self.btn_next)
        top_row.addWidget(self.btn_next_unmeasured)
        top_row.addStretch()
        top_row.addWidget(self.lbl_progress)
        top_row.addWidget(self.progress_bar)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(3)
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.lbl_outlier_warning)

        TranslationManager.get_instance().language_changed.connect(self.retranslate_ui)

    def retranslate_ui(self) -> None:
        """Update strings on language change."""
        self.lbl_reading_tag.setText(tr("survey_reading"))
        self.btn_save_next.setText(f"{tr('survey_save_next')} (Enter)")
        self.btn_prev.setText(tr("survey_prev"))
        self.btn_next.setText(tr("survey_next"))
        self.btn_next_unmeasured.setText(tr("survey_next_unmeasured"))
        self.set_active_point(self.active_point_id)

    def set_project(self, project: LuminationProject, active_point_id: Optional[str] = None) -> None:
        """Bind project reference and activate point."""
        self.project = project
        if active_point_id:
            self.set_active_point(active_point_id)
        elif project and project.points:
            self.set_active_point(project.points[0].id)
        self.update_progress()

    def set_active_point(self, point_id: Optional[str]) -> None:
        """Highlight and load the given measurement point into the fast entry bar."""
        self.active_point_id = point_id
        if not self.project or not point_id:
            self.lbl_point_id.setText(f"{tr('survey_point')} --")
            self.lbl_coords.setText("(X: -- m, Y: -- m)")
            self.lbl_outlier_warning.setVisible(False)
            return

        pt = self.project.find_point_by_id(point_id)
        if pt:
            status_str = f"[{tr('survey_completed')}]" if pt.is_measured else "[Pending]"
            self.lbl_point_id.setText(f"{tr('survey_point')} {pt.id} {status_str}")
            self.lbl_coords.setText(f"(X: {pt.x:.2f} m, Y: {pt.y:.2f} m)")

            self.spin_lux.blockSignals(True)
            if pt.is_measured and pt.lux is not None:
                self.spin_lux.setValue(pt.lux)
            else:
                self.spin_lux.setValue(0.0)
            self.spin_lux.blockSignals(False)

            self.spin_lux.selectAll()
            self.spin_lux.setFocus()

            # Show outlier badge if flagged
            if pt.is_possible_outlier and pt.outlier_reason:
                self.lbl_outlier_warning.setText(f"{tr('survey_possible_outlier')} {pt.outlier_reason}")
                self.lbl_outlier_warning.setVisible(True)
            else:
                self.lbl_outlier_warning.setVisible(False)

        self.update_progress()

    def update_progress(self) -> None:
        """Update progress bar and completion count."""
        if not self.project or not self.project.points:
            self.lbl_progress.setText(f"{tr('survey_progress')} 0 / 0 (0%)")
            self.progress_bar.setValue(0)
            return

        total = len(self.project.points)
        measured = len(self.project.get_measured_points())
        pct = int(round((measured / total) * 100)) if total > 0 else 0

        self.lbl_progress.setText(f"{tr('survey_progress')} {measured} / {total} ({pct}%)")
        self.progress_bar.setValue(pct)

    def _save_and_advance(self) -> None:
        """Save current lux reading, check outliers, and advance to next consecutive point."""
        if not self.project or not self.active_point_id:
            return

        pt = self.project.find_point_by_id(self.active_point_id)
        if not pt:
            return

        lux_val = self.spin_lux.value()
        self.measurement_saved.emit(pt.id, lux_val)
        self.update_progress()

        # Sequential walking traversal: move directly to (cur_idx + 1) % n
        self._go_next()

    def _go_previous(self) -> None:
        """Navigate to previous point in project point sequence."""
        if not self.project or not self.project.points:
            return
        cur_idx = self._get_current_index()
        prev_idx = (cur_idx - 1) % len(self.project.points)
        target_id = self.project.points[prev_idx].id
        self.set_active_point(target_id)
        self.point_navigated.emit(target_id)

    def _go_next(self) -> None:
        """Navigate to next sequential point."""
        if not self.project or not self.project.points:
            return
        cur_idx = self._get_current_index()
        next_idx = (cur_idx + 1) % len(self.project.points)
        target_id = self.project.points[next_idx].id
        self.set_active_point(target_id)
        self.point_navigated.emit(target_id)

    def _go_next_unmeasured(self) -> None:
        """Find and navigate to the next unmeasured point following current sequence."""
        if not self.project or not self.project.points:
            return

        cur_idx = self._get_current_index()
        pts = self.project.points
        n = len(pts)

        for step in range(1, n + 1):
            idx = (cur_idx + step) % n
            if not pts[idx].is_measured:
                target_id = pts[idx].id
                self.set_active_point(target_id)
                self.point_navigated.emit(target_id)
                return

        # If all measured, go to next sequential
        self._go_next()

    def _get_current_index(self) -> int:
        if not self.project or not self.active_point_id:
            return 0
        for i, p in enumerate(self.project.points):
            if p.id == self.active_point_id:
                return i
        return 0
