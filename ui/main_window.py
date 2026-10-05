"""Main Application Window for Lumination.

Microsoft Office / Excel-grade desktop interface:
- Edge-to-edge 2D room canvas covering 100% of central workspace
- Two clean collapsible side panels (Left: Layers & Target, Right: KPIs, DIALux, Table)
- Small sleek floating toggle buttons with chevron icons on the left and right edges
- Physical Lux Meter hardware integration (USB Serial & Bluetooth Low Energy)
- Zero emojis anywhere — clean, crisp typography and vector icons
- Multi-language runtime translation (English, Romanian, German)
- Menu hierarchy: File, CSV & Export, Devices, Language, Help
- Comprehensive Undo / Redo system (Ctrl+Z, Ctrl+Y, Ctrl+X)
"""

from __future__ import annotations
import os
import time
from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QIcon, QUndoStack
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QDockWidget,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QLabel,
    QPushButton,
    QFrame,
)

from models.project import LuminationProject
from models.room import Room
from models.measurement import MeasurementPoint
from measurement_sources.base import MeasurementSource
from measurement_sources.manual import ManualMeasurementSource
from measurement_sources.mock import MockLuxMeterSource
from measurement_sources.usb_serial import USBSerialMeterSource
from measurement_sources.bluetooth_meter import BluetoothMeterSource

from ui.room_canvas import RoomCanvasWidget
from ui.measurement_table import MeasurementTableWidget
from ui.results_panel import ResultsPanel
from ui.target_panel import TargetPanel
from ui.comparison_panel import ComparisonPanel
from ui.layer_control_widget import LayerControlWidget
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.dialogs.grid_generator_dialog import GridGeneratorDialog
from ui.dialogs.point_edit_dialog import PointEditDialog
from ui.dialogs.export_dialog import ExportDialog
from ui.dialogs.hardware_connection_dialog import HardwareConnectionDialog

from ui.icons import create_chevron_left_icon, create_chevron_right_icon, create_bluetooth_icon
from utils.undo_commands import (
    SetMeasurementLuxCommand,
    AddPointCommand,
    DeletePointCommand,
)
from i18n.translations import tr, TranslationManager


class MainWindow(QMainWindow):
    """Main Application Window for Lumination."""

    def __init__(self, project: Optional[LuminationProject] = None) -> None:
        super().__init__()

        self.project: LuminationProject = project or self._create_default_project()
        self._is_updating: bool = False
        self.interp_result = None
        self.active_point_id: Optional[str] = None

        # Undo / Redo Stack
        self.undo_stack = QUndoStack(self)

        self.setWindowTitle("Lumination — Real-Room Illuminance Survey & Photometric Reconstruction")
        self.resize(1380, 860)
        self.setMinimumSize(960, 600)

        # Hardware Lux Meter Sources Setup (USB Serial + Bluetooth BLE)
        self.manual_source = ManualMeasurementSource(self)
        self.usb_source = USBSerialMeterSource(self)
        self.bt_source = BluetoothMeterSource(self)

        self.usb_source.live_reading_stream.connect(self._on_hardware_stream)
        self.bt_source.live_reading_stream.connect(self._on_hardware_stream)
        self.usb_source.connection_status_changed.connect(self._on_hardware_status_changed)
        self.bt_source.connection_status_changed.connect(self._on_hardware_status_changed)

        # Create Core UI Widgets
        self.canvas_widget = RoomCanvasWidget(self)
        self.table_widget = MeasurementTableWidget(self)
        self.results_panel = ResultsPanel(self)
        self.target_panel = TargetPanel(self)
        self.comparison_panel = ComparisonPanel(self)
        self.layer_widget = LayerControlWidget(self)

        # 1. Central Widget: Edge-to-Edge Canvas with Sleek Floating Edge Toggle Buttons
        central_container = QWidget(self)
        central_layout = QHBoxLayout(central_container)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Small Left Edge Toggle Button
        self.btn_toggle_left = QPushButton(central_container)
        self.btn_toggle_left.setIcon(create_chevron_left_icon())
        self.btn_toggle_left.setFixedSize(16, 48)
        self.btn_toggle_left.setToolTip("Toggle Left Panel (Layers & Target)")
        self.btn_toggle_left.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_toggle_left.clicked.connect(self._toggle_dock_left)

        # Small Right Edge Toggle Button
        self.btn_toggle_right = QPushButton(central_container)
        self.btn_toggle_right.setIcon(create_chevron_right_icon())
        self.btn_toggle_right.setFixedSize(16, 48)
        self.btn_toggle_right.setToolTip("Toggle Right Panel (KPIs & Measurements)")
        self.btn_toggle_right.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-right: none;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_toggle_right.clicked.connect(self._toggle_dock_right)

        # Canvas Wrapper
        canvas_wrapper = QWidget(central_container)
        c_vbox = QVBoxLayout(canvas_wrapper)
        c_vbox.setContentsMargins(2, 2, 2, 2)
        c_vbox.addWidget(self.canvas_widget)

        central_layout.addWidget(self.btn_toggle_left)
        central_layout.addWidget(canvas_wrapper, stretch=1)
        central_layout.addWidget(self.btn_toggle_right)

        self.setCentralWidget(central_container)

        # 2. Setup 2 Distinct Collapsible Side Panels (Left and Right)
        self._setup_docks()

        # 3. Setup Menus & Actions
        self._setup_menus()

        # 4. Setup Compact Status Bar
        self._setup_status_bar()

        # 5. Connect Signals
        self._connect_signals()

        # 6. Initial UI Data Bind
        self.load_project_into_ui(initial=True)

        # 7. Connect Language Changes
        TranslationManager.get_instance().language_changed.connect(self.retranslate_ui)

        # Defer first computation to after window is shown
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.recalculate_and_refresh)

    def _create_default_project(self) -> LuminationProject:
        """Create a default sample project."""
        room = Room(name="Office 201", length=6.0, width=4.0, height=2.8, measurement_plane_height=0.75, wall_margin=0.5, traversal_order="serpentine")
        proj = LuminationProject(name="Office Illuminance Survey", room=room, target_lux=500.0)
        proj.regenerate_grid(mode="count", rows=3, cols=4, wall_margin=0.5, centered_in_cells=True, traversal_order="serpentine")

        sample_lux = [320, 370, 410, 430, 380, 450, 520, 500, 400, 490, 570, 540]
        sample_exp = [350, 400, 450, 450, 400, 500, 550, 500, 420, 500, 580, 550]
        for i, p in enumerate(proj.points):
            if i < len(sample_lux):
                p.lux = float(sample_lux[i])
                p.expected_lux = float(sample_exp[i])

        return proj

    def _setup_docks(self) -> None:
        """Configure 2 clean collapsible side panels on left and right."""
        # Panel 1: Left Dock (Layers & Visuals + Target Illuminance)
        self.dock_left = QDockWidget(tr("tab_layers"), self)
        self.dock_left.setObjectName("dock_left")
        self.dock_left.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.dock_left.visibilityChanged.connect(self._on_left_dock_visibility_changed)

        self.left_tabs = QTabWidget(self.dock_left)
        self.left_tabs.addTab(self.layer_widget, tr("tab_layers"))
        self.left_tabs.addTab(self.target_panel, tr("tab_target"))
        self.dock_left.setWidget(self.left_tabs)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_left)

        # Panel 2: Right Dock (Photometric KPIs + Measurements Schedule Table + DIALux)
        self.dock_right = QDockWidget(tr("tab_kpis"), self)
        self.dock_right.setObjectName("dock_right")
        self.dock_right.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.dock_right.visibilityChanged.connect(self._on_right_dock_visibility_changed)

        self.right_tabs = QTabWidget(self.dock_right)
        self.right_tabs.addTab(self.results_panel, tr("tab_kpis"))
        self.right_tabs.addTab(self.table_widget, tr("tab_measurements"))
        self.right_tabs.addTab(self.comparison_panel, tr("tab_simulated"))
        self.dock_right.setWidget(self.right_tabs)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_right)

    def _toggle_dock_left(self) -> None:
        self.dock_left.setVisible(not self.dock_left.isVisible())

    def _toggle_dock_right(self) -> None:
        self.dock_right.setVisible(not self.dock_right.isVisible())

    def _on_left_dock_visibility_changed(self, visible: bool) -> None:
        self.btn_toggle_left.setIcon(create_chevron_left_icon() if visible else create_chevron_right_icon())

    def _on_right_dock_visibility_changed(self, visible: bool) -> None:
        self.btn_toggle_right.setIcon(create_chevron_right_icon() if visible else create_chevron_left_icon())

    def _setup_menus(self) -> None:
        """Create clean menu hierarchy: File, CSV & Export, Devices, Language, Help."""
        menubar = self.menuBar()
        menubar.clear()

        # 1. File Menu
        self.menu_file = menubar.addMenu(f"&{tr('menu_file')}")

        self.act_new = QAction(f"&{tr('menu_new_project')}", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self._on_new_project)
        self.menu_file.addAction(self.act_new)

        self.act_open = QAction(f"&{tr('menu_open_project')}", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self._on_open_project)
        self.menu_file.addAction(self.act_open)

        self.act_save = QAction(f"&{tr('menu_save_project')}", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self._on_save_project)
        self.menu_file.addAction(self.act_save)

        self.act_save_as = QAction(f"{tr('menu_save_project_as')}", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self._on_save_project_as)
        self.menu_file.addAction(self.act_save_as)

        self.menu_file.addSeparator()

        self.act_exit = QAction(tr("menu_exit"), self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        self.menu_file.addAction(self.act_exit)

        # 2. CSV & Export Menu
        self.menu_export = menubar.addMenu(f"&{tr('menu_csv_export')}")

        self.act_import_csv = QAction(tr("menu_import_csv"), self)
        self.act_import_csv.triggered.connect(self._on_import_csv)
        self.menu_export.addAction(self.act_import_csv)

        self.act_export_csv = QAction(tr("menu_export_csv"), self)
        self.act_export_csv.triggered.connect(self._on_export_csv)
        self.menu_export.addAction(self.act_export_csv)

        self.menu_export.addSeparator()

        self.act_export_pdf = QAction(tr("menu_export_pdf"), self)
        self.act_export_pdf.setShortcut(QKeySequence.StandardKey.Print)
        self.act_export_pdf.triggered.connect(self._on_export_pdf)
        self.menu_export.addAction(self.act_export_pdf)

        self.act_export_img = QAction(tr("menu_export_image"), self)
        self.act_export_img.triggered.connect(self._on_export_image)
        self.menu_export.addAction(self.act_export_img)

        # 3. Devices Menu (Hardware Connectivity)
        self.menu_devices = menubar.addMenu("&Devices")

        self.act_connect_meter = QAction("Connect Physical Lux Meter (USB / Bluetooth)...", self)
        self.act_connect_meter.setIcon(create_bluetooth_icon())
        self.act_connect_meter.triggered.connect(self._on_open_hardware_dialog)
        self.menu_devices.addAction(self.act_connect_meter)

        # 4. Language Menu
        self.menu_lang = menubar.addMenu(f"&{tr('menu_language')}")

        self.act_lang_en = QAction("English (EN)", self)
        self.act_lang_en.triggered.connect(lambda: TranslationManager.get_instance().set_language("en"))
        self.menu_lang.addAction(self.act_lang_en)

        self.act_lang_ro = QAction("Română (RO)", self)
        self.act_lang_ro.triggered.connect(lambda: TranslationManager.get_instance().set_language("ro"))
        self.menu_lang.addAction(self.act_lang_ro)

        self.act_lang_de = QAction("Deutsch (DE)", self)
        self.act_lang_de.triggered.connect(lambda: TranslationManager.get_instance().set_language("de"))
        self.menu_lang.addAction(self.act_lang_de)

        # 5. Help Menu
        self.menu_help = menubar.addMenu(f"&{tr('menu_help')}")

        self.act_shortcuts = QAction(tr("menu_shortcuts"), self)
        self.act_shortcuts.triggered.connect(self._on_show_shortcuts)
        self.menu_help.addAction(self.act_shortcuts)

        self.act_methodology = QAction(tr("menu_methodology"), self)
        self.act_methodology.triggered.connect(self._on_show_methodology)
        self.menu_help.addAction(self.act_methodology)

        self.menu_help.addSeparator()

        self.act_about = QAction(tr("menu_about"), self)
        self.act_about.triggered.connect(self._on_about)
        self.menu_help.addAction(self.act_about)

    def _setup_status_bar(self) -> None:
        """Create clean, compact status bar positioned comfortably within viewport."""
        self.status_bar = QStatusBar(self)
        self.status_bar.setFixedHeight(22)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
                color: #334155;
                font-size: 11px;
            }
        """)
        self.setStatusBar(self.status_bar)

        self.lbl_project_status = QLabel("Ready", self)
        self.lbl_project_status.setStyleSheet("color: #334155; font-size: 11px; padding: 0 6px;")

        self.lbl_hardware_status = QLabel("Meter: Disconnected", self)
        self.lbl_hardware_status.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; padding: 0 8px;")

        self.status_bar.addWidget(self.lbl_project_status, stretch=1)
        self.status_bar.addPermanentWidget(self.lbl_hardware_status)

    def _connect_signals(self) -> None:
        """Connect inter-widget signals."""
        self.canvas_widget.point_selected.connect(self._on_point_selected)
        self.canvas_widget.point_edit_requested.connect(self._on_point_edit_requested)
        self.canvas_widget.point_add_requested.connect(self._on_point_add_requested)
        self.canvas_widget.point_delete_requested.connect(self._on_point_delete_requested)
        self.canvas_widget.measurement_saved.connect(self._on_measurement_recorded)
        self.canvas_widget.hardware_connect_requested.connect(self._on_open_hardware_dialog)
        self.canvas_widget.undo_requested.connect(self.undo_stack.undo)
        self.canvas_widget.redo_requested.connect(self.undo_stack.redo)

        self.table_widget.point_selected.connect(self._on_point_selected)
        self.table_widget.data_changed.connect(self.recalculate_and_refresh)

        self.results_panel.highlight_point_requested.connect(self._on_point_selected)
        self.target_panel.target_changed.connect(lambda val: self.recalculate_and_refresh())
        self.comparison_panel.display_mode_changed.connect(lambda mode: self.recalculate_and_refresh())
        self.layer_widget.settings_changed.connect(self.recalculate_and_refresh)

    def retranslate_ui(self) -> None:
        """Update window, menus, and side panel tabs when language switches."""
        self.setWindowTitle(f"Lumination — {tr('dlg_new_project_title')} [{self.project.name}]")
        self._setup_menus()

        self.dock_left.setWindowTitle(tr("tab_layers"))
        self.left_tabs.setTabText(0, tr("tab_layers"))
        self.left_tabs.setTabText(1, tr("tab_target"))

        self.dock_right.setWindowTitle(tr("tab_kpis"))
        self.right_tabs.setTabText(0, tr("tab_kpis"))
        self.right_tabs.setTabText(1, tr("tab_measurements"))
        self.right_tabs.setTabText(2, tr("tab_simulated"))

        self.recalculate_and_refresh()

    def load_project_into_ui(self, initial: bool = False) -> None:
        """Bind project data to all UI components with signal guards."""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            self.table_widget.set_project(self.project)
            self.layer_widget.set_project(self.project)
            self.target_panel.set_project(self.project)
            self.comparison_panel.set_project(self.project)
        finally:
            self._is_updating = False

        if not initial:
            self.recalculate_and_refresh()

    def recalculate_and_refresh(self) -> None:
        """Perform numerical statistics, 2D interpolation, and refresh canvas and panels."""
        if self._is_updating:
            return
        self._is_updating = True

        try:
            from analysis.statistics import calculate_statistics
            from analysis.interpolation import reconstruct_illuminance_field

            stats = calculate_statistics(self.project.points)
            self.results_panel.update_statistics(stats)
            self.target_panel.update_analysis()
            self.comparison_panel.update_analysis()

            display_mode = self.project.visualization_settings.display_mode
            active_points = self.project.points
            if display_mode == "expected":
                active_points = [p for p in self.project.points if p.expected_lux is not None]
            elif display_mode == "difference":
                active_points = [p for p in self.project.points if p.delta_lux is not None]

            measured_count = len([p for p in active_points if (p.is_measured and p.lux is not None and p.lux >= 0)])

            if measured_count >= 3:
                self.interp_result = reconstruct_illuminance_field(
                    self.project.points if display_mode == "measured" else active_points,
                    self.project.room,
                    resolution=100,
                    method=self.project.visualization_settings.interpolation_method,
                    extrapolate_to_walls=False,
                )
            else:
                self.interp_result = None

            self.canvas_widget.set_project(
                self.project,
                interp_result=self.interp_result,
                selected_point_id=self.active_point_id,
            )

            r = self.project.room
            n_meas = len(self.project.get_measured_points())
            n_tot = len(self.project.points)
            u0_str = f"U₀: {stats.uniformity_u0:.2f}" if stats else "U₀: -"
            avg_str = f"Avg: {stats.e_avg:.0f} lx" if stats else "Avg: - lx"

            self.lbl_project_status.setText(
                f"{r.length:.1f}×{r.width:.1f}m ({r.area:.1f}m²) | {n_meas}/{n_tot} measured | {avg_str} | {u0_str}"
            )
        finally:
            self._is_updating = False

    def _on_point_selected(self, point_id: str) -> None:
        if self._is_updating:
            return
        self._is_updating = True
        try:
            self.active_point_id = point_id
            self.canvas_widget.set_selected_point_id(point_id)
            self.table_widget.select_point(point_id)
        finally:
            self._is_updating = False

    def _on_measurement_recorded(self, point_id: str, lux: float) -> None:
        """Record measurement via Undo/Redo command stack."""
        cmd = SetMeasurementLuxCommand(
            project=self.project,
            point_id=point_id,
            new_lux=lux,
            new_device="Direct Input",
            callback=self._on_data_modified,
        )
        self.undo_stack.push(cmd)

    def _on_data_modified(self) -> None:
        """Callback when undo/redo modifies data."""
        self.table_widget.refresh()
        self.recalculate_and_refresh()

    def _on_point_edit_requested(self, point_id: str) -> None:
        pt = self.project.find_point_by_id(point_id)
        if pt:
            dlg = PointEditDialog(pt, self.project.room, self)
            if dlg.exec() == PointEditDialog.DialogCode.Accepted:
                self.table_widget.refresh()
                self.recalculate_and_refresh()

    def _on_point_add_requested(self, x: float, y: float) -> None:
        pt = self.project.add_custom_point(x, y, notes="Custom Sensor")
        cmd = AddPointCommand(self.project, pt, callback=self._on_data_modified)
        self.undo_stack.push(cmd)
        self._on_point_selected(pt.id)

    def _on_point_delete_requested(self, point_id: str) -> None:
        cmd = DeletePointCommand(self.project, point_id, callback=self._on_data_modified)
        self.undo_stack.push(cmd)
        self.active_point_id = None
        self.canvas_widget.set_selected_point_id(None)

    def _on_open_hardware_dialog(self) -> None:
        dlg = HardwareConnectionDialog(self.usb_source, self.bt_source, self)
        dlg.reading_captured.connect(self._on_hardware_reading_captured)
        dlg.exec()

    def _on_hardware_reading_captured(self, lux: float) -> None:
        """Capture reading from dialog into the currently active point."""
        if not self.active_point_id and self.project.points:
            self.active_point_id = self.project.points[0].id

        if self.active_point_id:
            self._on_measurement_recorded(self.active_point_id, lux)
            # Advance to next sequential point
            pts = self.project.points
            for i, p in enumerate(pts):
                if p.id == self.active_point_id:
                    next_pt = pts[(i + 1) % len(pts)]
                    self._on_point_selected(next_pt.id)
                    break

    def _on_hardware_stream(self, lux: float) -> None:
        """Handle continuous stream reading from connected USB or Bluetooth meter."""
        source_name = "USB" if self.usb_source.is_connected else "Bluetooth"
        self.lbl_hardware_status.setText(f"Meter: {source_name} [{lux:.1f} lx]")

    def _on_hardware_status_changed(self, connected: bool, desc: str) -> None:
        if connected:
            self.lbl_hardware_status.setText(f"Meter: {desc}")
            self.lbl_hardware_status.setStyleSheet("color: #16a34a; font-size: 11px; font-weight: bold; padding: 0 8px;")
        else:
            self.lbl_hardware_status.setText("Meter: Disconnected")
            self.lbl_hardware_status.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; padding: 0 8px;")

    # --- Menu Handlers ---

    def _on_new_project(self) -> None:
        dlg = NewProjectDialog(self)
        if dlg.exec() == NewProjectDialog.DialogCode.Accepted:
            new_proj = dlg.get_created_project()
            if new_proj:
                self.project = new_proj
                self.active_point_id = None
                self.undo_stack.clear()
                self.load_project_into_ui()

    def _on_open_project(self) -> None:
        from persistence.project_io import load_project
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Lumination Project",
            "",
            "Lumination Project (*.luxproj);;JSON Files (*.json);;All Files (*.*)",
        )
        if file_path:
            try:
                proj = load_project(file_path)
                self.project = proj
                self.active_point_id = None
                self.undo_stack.clear()
                self.load_project_into_ui()
                self.status_bar.showMessage(f"Project loaded: {os.path.basename(file_path)}", 4000)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load project file:\n{e}")

    def _on_save_project(self) -> None:
        if not self.project.file_path:
            self._on_save_project_as()
            return
        from persistence.project_io import save_project
        try:
            save_project(self.project, self.project.file_path)
            self.status_bar.showMessage("Project saved successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save project:\n{e}")

    def _on_save_project_as(self) -> None:
        from persistence.project_io import save_project
        default_name = f"{self.project.name.replace(' ', '_').lower()}.luxproj"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Lumination Project As",
            default_name,
            "Lumination Project (*.luxproj);;All Files (*.*)",
        )
        if file_path:
            try:
                save_project(self.project, file_path)
                self.status_bar.showMessage(f"Saved as: {os.path.basename(file_path)}", 4000)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save project file:\n{e}")

    def _on_import_csv(self) -> None:
        from persistence.csv_io import import_measurements_from_csv
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Measurements CSV",
            "",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)",
        )
        if file_path:
            try:
                upd, crt = import_measurements_from_csv(self.project, file_path)
                self.table_widget.refresh()
                self.recalculate_and_refresh()
                QMessageBox.information(
                    self,
                    "CSV Import Successful",
                    f"Import completed:\n- {upd} points updated\n- {crt} new points added",
                )
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import CSV:\n{e}")

    def _on_export_csv(self) -> None:
        from persistence.csv_io import export_measurements_to_csv
        default_name = f"{self.project.name.replace(' ', '_').lower()}_measurements.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Measurements to CSV",
            default_name,
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if file_path:
            try:
                export_measurements_to_csv(self.project, file_path)
                QMessageBox.information(self, "Export Successful", f"Measurements exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{e}")

    def _on_export_pdf(self) -> None:
        from reporting.pdf_report import generate_pdf_report
        default_name = f"{self.project.name.replace(' ', '_').lower()}_report.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF Survey Report",
            default_name,
            "PDF Documents (*.pdf);;All Files (*.*)",
        )
        if file_path:
            try:
                generate_pdf_report(self.project, file_path)
                QMessageBox.information(self, "PDF Report Generated", f"Report saved successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "PDF Export Error", f"Failed to generate PDF report:\n{e}")

    def _on_export_image(self) -> None:
        from reporting.chart_exporter import export_room_map_image
        default_name = f"{self.project.name.replace(' ', '_').lower()}_map.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export High-Resolution Map Image",
            default_name,
            "PNG Images (*.png);;JPEG Images (*.jpg);;PDF Document (*.pdf);;All Files (*.*)",
        )
        if file_path:
            try:
                img_bytes = export_room_map_image(self.project, dpi=300)
                with open(file_path, "wb") as f:
                    f.write(img_bytes)
                QMessageBox.information(self, "Export Successful", f"High-resolution map saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save image:\n{e}")

    def _on_show_shortcuts(self) -> None:
        QMessageBox.information(
            self,
            "Keyboard Shortcuts Reference",
            "<h3>Lumination Keyboard Shortcuts</h3>"
            "<ul>"
            "<li><b>Click point</b>: Open in-place editor tag to modify lux value</li>"
            "<li><b>Enter</b>: Save lux reading and jump directly to next point in sequence</li>"
            "<li><b>Backspace / Delete</b>: Delete currently selected measurement point</li>"
            "<li><b>Ctrl + Z</b>: Undo last action</li>"
            "<li><b>Ctrl + Y / Ctrl + X</b>: Redo undone action</li>"
            "<li><b>Ctrl + S</b>: Save project</li>"
            "<li><b>Ctrl + O</b>: Open project</li>"
            "<li><b>Ctrl + N</b>: Create new room project</li>"
            "<li><b>Mouse Wheel</b>: Zoom in / Zoom out on room canvas</li>"
            "<li><b>Escape</b>: Exit custom point placement mode / close editor tag</li>"
            "</ul>",
        )

    def _on_show_methodology(self) -> None:
        QMessageBox.information(
            self,
            "Measurement & Reconstruction Methodology",
            "<h3>Physical Illuminance Reconstruction</h3>"
            "<p>Lumination is designed for real physical lux meter surveys.</p>"
            "<p><b>Spatial Interpolation:</b> 2D Scipy spatial algorithms (Linear, Cubic, RBF) "
            "reconstruct the continuous illuminance field across the room measurement plane from discrete physical readings.</p>"
            "<p><b>Scientific Integrity:</b> Raw physical measurements remain immutable. "
            "Interpolated values represent mathematical estimates and are clearly distinguished from recorded points.</p>",
        )

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About Lumination",
            "<h2>Lumination</h2>"
            "<p><b>Real-Room Illuminance Survey & Photometric Analysis</b></p>"
            "<p>Version 1.4.0</p>"
            "<p>Engineered for precision physical lighting audits, hardware lux meter acquisition, and spatial illuminance reconstruction.</p>",
        )
