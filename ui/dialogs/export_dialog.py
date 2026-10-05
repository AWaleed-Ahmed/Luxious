"""Export Options Dialog.

Allows the user to select and configure export formats:
- Professional PDF Survey Report
- High-Resolution Room Map Image (PNG / SVG)
- Measurement Data CSV
"""

from __future__ import annotations
import os
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
    QPushButton,
    QFileDialog,
    QLabel,
    QMessageBox,
    QDialogButtonBox,
)

from models.project import LuminationProject
from reporting.pdf_report import generate_pdf_report
from reporting.chart_exporter import export_room_map_image
from persistence.csv_io import export_measurements_to_csv


class ExportDialog(QDialog):
    """Dialog to export project reports, high-res images, and data tables."""

    def __init__(self, project: LuminationProject, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Export Project Data & Reports")
        self.setMinimumWidth(400)

        # Export Format Group
        group = QGroupBox("Select Export Type", self)
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(10)

        self.btn_group = QButtonGroup(self)
        self.rb_pdf = QRadioButton("📄 Professional Engineering PDF Survey Report", self)
        self.rb_img = QRadioButton("🖼 High-Resolution 2D Illuminance Map (PNG, 300 DPI)", self)
        self.rb_csv = QRadioButton("📊 Measurement Schedule Table (CSV)", self)

        self.rb_pdf.setChecked(True)
        self.btn_group.addButton(self.rb_pdf, 0)
        self.btn_group.addButton(self.rb_img, 1)
        self.btn_group.addButton(self.rb_csv, 2)

        g_layout.addWidget(self.rb_pdf)
        g_layout.addWidget(self.rb_img)
        g_layout.addWidget(self.rb_csv)

        # Standard dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Export...")
        button_box.accepted.connect(self._do_export)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(group)
        layout.addWidget(button_box)

    def _do_export(self) -> None:
        proj_safe_name = "".join(c for c in self.project.name if c.isalnum() or c in (' ', '_', '-')).strip()

        if self.rb_pdf.isChecked():
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export PDF Report", f"{proj_safe_name}_Report.pdf", "PDF Files (*.pdf)"
            )
            if file_path:
                try:
                    generate_pdf_report(self.project, file_path)
                    QMessageBox.information(self, "Export Complete", f"PDF report generated successfully at:\n{file_path}")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to generate PDF:\n{e}")

        elif self.rb_img.isChecked():
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Map Image", f"{proj_safe_name}_IlluminanceMap.png", "PNG Images (*.png)"
            )
            if file_path:
                try:
                    export_room_map_image(self.project, output_path=file_path, dpi=300)
                    QMessageBox.information(self, "Export Complete", f"High-res map image saved to:\n{file_path}")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to save image:\n{e}")

        elif self.rb_csv.isChecked():
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export CSV Measurements", f"{proj_safe_name}_measurements.csv", "CSV Files (*.csv)"
            )
            if file_path:
                try:
                    export_measurements_to_csv(self.project, file_path)
                    QMessageBox.information(self, "Export Complete", f"CSV file saved to:\n{file_path}")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to save CSV:\n{e}")
