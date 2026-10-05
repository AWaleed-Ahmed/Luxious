"""Automated UI Integration and Workflow Tests with PySide6 / QTest."""

import os
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from models.room import Room
from models.project import LuminationProject
from ui.main_window import MainWindow
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.dialogs.grid_generator_dialog import GridGeneratorDialog


@pytest.fixture(scope="session")
def qapp():
    """Ensure QApplication instance is running."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_lifecycle(qapp, tmp_path):
    """Verify MainWindow creation, data loading, point editing, and calculations."""
    window = MainWindow()
    window.show()
    qapp.processEvents()

    # Check project is loaded
    assert window.project is not None
    assert len(window.project.points) == 12

    # Check statistical calculations on default project
    stats = window.results_panel.stats
    assert stats is not None
    assert stats.count == 12
    assert stats.e_min == 320.0
    assert stats.e_max == 570.0
    assert pytest.approx(stats.uniformity_u0, 0.01) == 320.0 / stats.e_avg

    # Check target comparison
    assert window.target_panel.project.target_lux == 500.0

    # Simulate changing a measurement in point 0 (P1)
    p1 = window.project.points[0]
    p1.record_reading(600.0)
    window.table_widget.data_changed.emit()

    # Recalculated stats should update
    new_stats = window.results_panel.stats
    assert new_stats.e_min == 370.0  # P1 is now 600, so new min is P2 (370)
    assert new_stats.e_max == 600.0

    # Test switching display mode to difference
    window.comparison_panel.set_display_mode("difference")
    assert window.project.visualization_settings.display_mode == "difference"

    # Test saving project
    save_path = str(tmp_path / "ui_saved_project.luxproj")
    window.project.file_path = save_path
    window._on_save_project()
    assert os.path.exists(save_path)

    window.close()
