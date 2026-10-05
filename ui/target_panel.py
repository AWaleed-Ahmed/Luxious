"""Comparison with Selected Target Illuminance Panel.

Allows the user to specify a reference target illuminance (e.g., 500 lx)
and calculates comprehensive deviation metrics without legal compliance claims.
"""

from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QProgressBar,
    QFrame,
)

from models.project import LuminationProject
from analysis.comparison import TargetComparisonResult, compare_with_target


class TargetPanel(QWidget):
    """Panel for comparing physical measurements against a user-specified target illuminance.

    Signals:
        target_changed (float): Emitted when user sets/modifies the target illuminance.
    """
    target_changed = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.project: Optional[LuminationProject] = None

        # UI Elements
        group = QGroupBox("Comparison with Selected Target Illuminance", self)
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(8)

        # Target input row
        input_row = QHBoxLayout()
        lbl_target = QLabel("Target (lx):", self)
        lbl_target.setStyleSheet("font-weight: 600;")
        self.spin_target = QDoubleSpinBox(self)
        self.spin_target.setRange(0, 50000)
        self.spin_target.setValue(500.0)
        self.spin_target.setSingleStep(50.0)
        self.spin_target.setSuffix(" lx")
        self.spin_target.valueChanged.connect(self._on_target_changed)

        input_row.addWidget(lbl_target)
        input_row.addWidget(self.spin_target)
        input_row.addStretch()

        # Preset buttons for convenience
        preset_row = QHBoxLayout()
        for val in [100, 200, 300, 500, 750, 1000]:
            btn = QPushButton(f"{val}", self)
            btn.setMaximumWidth(45)
            btn.setStyleSheet("padding: 2px 4px; font-size: 11px;")
            btn.clicked.connect(lambda checked=False, v=val: self.spin_target.setValue(v))
            preset_row.addWidget(btn)

        # Compliance Progress Bar
        self.lbl_progress = QLabel("Points Meeting Target: 0 / 0 (0%)", self)
        self.lbl_progress.setStyleSheet("font-size: 11px; font-weight: 600; color: #1e3a8a;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                text-align: center;
                height: 16px;
                background-color: #fee2e2;
                color: #0f172a;
                font-size: 10px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #22c55e;
                border-radius: 3px;
            }
        """)

        # Metric Details Card Grid
        self.metrics_frame = QFrame(self)
        self.metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        m_grid = QGridLayout(self.metrics_frame)
        m_grid.setSpacing(4)

        self.lbl_m_target = QLabel("Target: <b>- lx</b>", self)
        self.lbl_m_avg = QLabel("Avg Measured: <b>- lx</b>", self)
        self.lbl_m_below = QLabel("Below Target: <b>-</b>", self)
        self.lbl_m_above = QLabel("≥ Target: <b>-</b>", self)
        self.lbl_m_max_deficit = QLabel("Max Deficit: <b>-</b>", self)
        self.lbl_m_max_surplus = QLabel("Max Surplus: <b>-</b>", self)
        self.lbl_m_mae = QLabel("Mean Abs Deviation: <b>-</b>", self)
        self.lbl_m_avg_dev = QLabel("Mean Deviation: <b>-</b>", self)

        m_grid.addWidget(self.lbl_m_target, 0, 0)
        m_grid.addWidget(self.lbl_m_avg, 0, 1)
        m_grid.addWidget(self.lbl_m_below, 1, 0)
        m_grid.addWidget(self.lbl_m_above, 1, 1)
        m_grid.addWidget(self.lbl_m_max_deficit, 2, 0)
        m_grid.addWidget(self.lbl_m_max_surplus, 2, 1)
        m_grid.addWidget(self.lbl_m_mae, 3, 0)
        m_grid.addWidget(self.lbl_m_avg_dev, 3, 1)

        # Summary Note
        self.lbl_summary = QLabel("Enter measured points to compare against target.", self)
        self.lbl_summary.setWordWrap(True)
        self.lbl_summary.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; font-size: 11px; color: #334155;")

        g_layout.addLayout(input_row)
        g_layout.addLayout(preset_row)
        g_layout.addSpacing(4)
        g_layout.addWidget(self.lbl_progress)
        g_layout.addWidget(self.progress_bar)
        g_layout.addWidget(self.metrics_frame)
        g_layout.addWidget(self.lbl_summary)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(group)
        main_layout.addStretch()

    def set_project(self, project: LuminationProject) -> None:
        """Set project reference and update target input."""
        self.project = project
        if project.target_lux and project.target_lux > 0:
            self.spin_target.blockSignals(True)
            self.spin_target.setValue(project.target_lux)
            self.spin_target.blockSignals(False)
        self.update_analysis()

    def update_analysis(self) -> None:
        """Recalculate target comparison and refresh widgets."""
        if not self.project:
            return

        target_val = self.spin_target.value()
        comp = compare_with_target(self.project.points, target_val)

        if comp is None:
            self.progress_bar.setValue(0)
            self.lbl_progress.setText("Points Meeting Target: 0 / 0 (0%)")
            self.lbl_m_target.setText(f"Target: <b>{target_val:.0f} lx</b>")
            self.lbl_m_avg.setText("Avg Measured: <b>-</b>")
            self.lbl_m_below.setText("Below Target: <b>-</b>")
            self.lbl_m_above.setText("≥ Target: <b>-</b>")
            self.lbl_m_max_deficit.setText("Max Deficit: <b>-</b>")
            self.lbl_m_max_surplus.setText("Max Surplus: <b>-</b>")
            self.lbl_m_mae.setText("Mean Abs Dev: <b>-</b>")
            self.lbl_m_avg_dev.setText("Mean Dev: <b>-</b>")
            self.lbl_summary.setText(f"Target entered by user: {target_val:.0f} lx.\nNo measured points recorded yet.")
            return

        pct_above = int(round(comp.percentage_above_or_equal))
        self.progress_bar.setValue(pct_above)
        self.lbl_progress.setText(f"Points ≥ Target: <b>{comp.points_above_or_equal_target} / {comp.points_evaluated}</b> ({comp.percentage_above_or_equal:.1f}%)")

        self.lbl_m_target.setText(f"Target: <b>{comp.target_lux:.0f} lx</b>")
        self.lbl_m_avg.setText(f"Avg Measured: <b>{comp.e_avg:.1f} lx</b>")
        self.lbl_m_below.setText(f"Below Target: <b>{comp.points_below_target}</b> ({comp.percentage_below_target:.1f}%)")
        self.lbl_m_above.setText(f"≥ Target: <b>{comp.points_above_or_equal_target}</b> ({comp.percentage_above_or_equal:.1f}%)")

        deficit_sub = f" (at {comp.max_deficit_point_id})" if comp.max_deficit_point_id else ""
        self.lbl_m_max_deficit.setText(f"Max Deficit: <b>-{comp.max_negative_deficit:.1f} lx</b>{deficit_sub}")
        self.lbl_m_max_surplus.setText(f"Max Surplus: <b>+{comp.max_positive_deviation:.1f} lx</b>")
        self.lbl_m_mae.setText(f"Mean Abs Dev: <b>{comp.avg_absolute_deviation:.1f} lx</b>")
        self.lbl_m_avg_dev.setText(f"Mean Dev: <b>{comp.avg_deviation:+.1f} lx</b>")

        self.lbl_summary.setText(comp.summary_text)

    def _on_target_changed(self, val: float) -> None:
        if self.project:
            self.project.target_lux = val if val > 0 else None
            self.project.mark_modified()
        self.update_analysis()
        self.target_changed.emit(val)
