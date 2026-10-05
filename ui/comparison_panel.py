"""Simulated / DIALux Reference Comparison Panel.

Compares physical lux meter measurements with simulated lighting calculations (e.g. DIALux),
calculates Delta E and percentage difference metrics, and controls map display modes.
"""

from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGroupBox,
    QPushButton,
    QRadioButton,
    QButtonGroup,
)

from models.project import LuminationProject
from analysis.comparison import SimulatedComparisonResult, compare_measured_with_simulated


class ComparisonPanel(QWidget):
    """Panel for comparing measured illuminance against simulated/DIALux models.

    Signals:
        display_mode_changed (str): "measured", "expected", or "difference".
    """
    display_mode_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.project: Optional[LuminationProject] = None

        # Map Mode Selection
        mode_group = QGroupBox("Illuminance Map Display Mode", self)
        m_layout = QVBoxLayout(mode_group)
        m_layout.setSpacing(6)

        self.btn_group = QButtonGroup(self)
        self.rb_measured = QRadioButton("Physical Measured Map", self)
        self.rb_expected = QRadioButton("Simulated / DIALux Expected Map", self)
        self.rb_difference = QRadioButton("Difference Map (Δ E = Measured − Expected)", self)

        self.rb_measured.setChecked(True)
        self.btn_group.addButton(self.rb_measured, 0)
        self.btn_group.addButton(self.rb_expected, 1)
        self.btn_group.addButton(self.rb_difference, 2)

        self.btn_group.idClicked.connect(self._on_mode_radio_clicked)

        m_layout.addWidget(self.rb_measured)
        m_layout.addWidget(self.rb_expected)
        m_layout.addWidget(self.rb_difference)

        # Numerical Comparison Group
        comp_group = QGroupBox("Measured vs. Simulated Analytics", self)
        c_layout = QVBoxLayout(comp_group)
        c_layout.setSpacing(5)

        self.lbl_points_both = QLabel("Points Compared: 0", self)
        self.lbl_mean_delta = QLabel("Mean Delta (Δ E): -", self)
        self.lbl_mae = QLabel("Mean Absolute Error (MAE): -", self)
        self.lbl_rmse = QLabel("Root Mean Squared Error (RMSE): -", self)
        self.lbl_mape = QLabel("Mean Percentage Error: -", self)

        c_layout.addWidget(self.lbl_points_both)
        c_layout.addWidget(self.lbl_mean_delta)
        c_layout.addWidget(self.lbl_mae)
        c_layout.addWidget(self.lbl_rmse)
        c_layout.addWidget(self.lbl_mape)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(mode_group)
        main_layout.addWidget(comp_group)
        main_layout.addStretch()

    def set_project(self, project: LuminationProject) -> None:
        """Set project reference and update widgets."""
        self.project = project
        mode = project.visualization_settings.display_mode
        self.btn_group.blockSignals(True)
        if mode == "expected":
            self.rb_expected.setChecked(True)
        elif mode == "difference":
            self.rb_difference.setChecked(True)
        else:
            self.rb_measured.setChecked(True)
        self.btn_group.blockSignals(False)
        self.update_analysis()

    def set_display_mode(self, mode: str) -> None:
        """Set active map display mode and update project."""
        if mode == "expected":
            self.rb_expected.setChecked(True)
        elif mode == "difference":
            self.rb_difference.setChecked(True)
        else:
            mode = "measured"
            self.rb_measured.setChecked(True)

        if self.project:
            self.project.visualization_settings.display_mode = mode
            self.project.mark_modified()

        self.display_mode_changed.emit(mode)

    def update_analysis(self) -> None:
        """Recalculate simulated vs measured metrics."""
        if not self.project:
            return

        res = compare_measured_with_simulated(self.project.points)
        if res is None:
            self.lbl_points_both.setText("Points with Expected Values: <b>0</b>")
            self.lbl_mean_delta.setText("Mean Delta (Δ E): -")
            self.lbl_mae.setText("Mean Absolute Error (MAE): -")
            self.lbl_rmse.setText("Root Mean Squared Error (RMSE): -")
            self.lbl_mape.setText("Mean Percentage Error: -")
            return

        self.lbl_points_both.setText(f"Points Compared: <b>{res.points_evaluated}</b>")
        self.lbl_mean_delta.setText(f"Mean Delta (Δ E): <b>{res.mean_delta:+.1f} lx</b> (Avg Meas: {res.avg_measured:.0f} vs Exp: {res.avg_expected:.0f})")
        self.lbl_mae.setText(f"Mean Absolute Error (MAE): <b>{res.mean_absolute_error:.1f} lx</b>")
        self.lbl_rmse.setText(f"RMSE: <b>{res.root_mean_squared_error:.1f} lx</b>")
        self.lbl_mape.setText(f"Mean Percentage Error: <b>{res.mean_percentage_diff:.1f}%</b> (Max Δ: {res.max_absolute_delta:.1f} lx)")

    def _on_mode_radio_clicked(self, id_val: int) -> None:
        if id_val == 1:
            mode = "expected"
        elif id_val == 2:
            mode = "difference"
        else:
            mode = "measured"

        self.set_display_mode(mode)
