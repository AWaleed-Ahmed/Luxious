"""Hardware Lux Meter Connection Dialog (USB & Bluetooth).

Enables connecting to physical lux meters via:
- USB Serial (COM ports, Extech, Testo, Voltcraft, PeakTech, Uni-T)
- Bluetooth Low Energy & Bluetooth Classic (Testo 540i, CEM, UT383-BT)
Includes real-time lux streaming monitor and live reading capture.
"""

from __future__ import annotations
from typing import Optional, List, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QGroupBox,
    QDialogButtonBox,
    QProgressBar,
)

from measurement_sources.usb_serial import USBSerialMeterSource
from measurement_sources.bluetooth_meter import BluetoothMeterSource
from i18n.translations import tr


class HardwareConnectionDialog(QDialog):
    """Dialog for scanning, connecting, and live-streaming from USB & Bluetooth lux meters."""

    reading_captured = Signal(float)  # Emitted when user captures a reading

    def __init__(
        self,
        usb_source: USBSerialMeterSource,
        bt_source: BluetoothMeterSource,
        parent: Optional[QDialog] = None,
    ) -> None:
        super().__init__(parent)
        self.usb_source = usb_source
        self.bt_source = bt_source

        self.setWindowTitle("Connect Physical Lux Meter (USB & Bluetooth)")
        self.setMinimumWidth(520)

        # 1. Top Live Stream Monitor Banner
        self.monitor_frame = QFrame(self)
        self.monitor_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        m_layout = QHBoxLayout(self.monitor_frame)

        self.lbl_live_title = QLabel("LIVE SENSOR READOUT:", self.monitor_frame)
        self.lbl_live_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")

        self.lbl_live_value = QLabel("--.- lx", self.monitor_frame)
        self.lbl_live_value.setStyleSheet("color: #38bdf8; font-size: 24px; font-weight: bold; font-family: monospace;")

        self.btn_capture = QPushButton("Capture Reading", self.monitor_frame)
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_capture.clicked.connect(self._capture_reading)

        m_layout.addWidget(self.lbl_live_title)
        m_layout.addStretch()
        m_layout.addWidget(self.lbl_live_value)
        m_layout.addSpacing(10)
        m_layout.addWidget(self.btn_capture)

        # 2. Connection Tabs: USB Serial vs Bluetooth
        self.tabs = QTabWidget(self)

        # --- Tab 1: USB Serial ---
        self.tab_usb = QWidget(self)
        u_layout = QGridLayout(self.tab_usb)
        u_layout.setSpacing(8)

        self.combo_ports = QComboBox(self.tab_usb)
        self.btn_refresh_ports = QPushButton("Scan Ports", self.tab_usb)
        self.btn_refresh_ports.clicked.connect(self._refresh_ports)

        self.combo_baud = QComboBox(self.tab_usb)
        for b in [9600, 19200, 38400, 57600, 115200]:
            self.combo_baud.addItem(f"{b} bps", b)

        self.btn_connect_usb = QPushButton("Connect USB Meter", self.tab_usb)
        self.btn_connect_usb.setStyleSheet("font-weight: bold; padding: 5px 12px;")
        self.btn_connect_usb.clicked.connect(self._toggle_usb_connect)

        self.lbl_usb_status = QLabel("Status: Disconnected", self.tab_usb)
        self.lbl_usb_status.setStyleSheet("color: #64748b; font-size: 11px;")

        u_layout.addWidget(QLabel("Serial / COM Port:"), 0, 0)
        u_layout.addWidget(self.combo_ports, 0, 1)
        u_layout.addWidget(self.btn_refresh_ports, 0, 2)

        u_layout.addWidget(QLabel("Baud Rate:"), 1, 0)
        u_layout.addWidget(self.combo_baud, 1, 1)

        u_layout.addWidget(self.btn_connect_usb, 2, 0, 1, 3)
        u_layout.addWidget(self.lbl_usb_status, 3, 0, 1, 3)

        self.tabs.addTab(self.tab_usb, "USB Serial (COM)")

        # --- Tab 2: Bluetooth ---
        self.tab_bt = QWidget(self)
        b_layout = QVBoxLayout(self.tab_bt)
        b_layout.setSpacing(6)

        b_top = QHBoxLayout()
        self.btn_scan_bt = QPushButton("Scan Bluetooth Devices", self.tab_bt)
        self.btn_scan_bt.clicked.connect(self._scan_bluetooth)
        self.lbl_bt_scan_status = QLabel("", self.tab_bt)
        self.lbl_bt_scan_status.setStyleSheet("color: #64748b; font-size: 11px;")
        b_top.addWidget(self.btn_scan_bt)
        b_top.addWidget(self.lbl_bt_scan_status)
        b_top.addStretch()

        self.list_bt_devices = QListWidget(self.tab_bt)
        self.list_bt_devices.setStyleSheet("font-size: 12px; padding: 4px;")

        self.btn_connect_bt = QPushButton("Connect Selected Bluetooth Device", self.tab_bt)
        self.btn_connect_bt.setStyleSheet("font-weight: bold; padding: 5px 12px;")
        self.btn_connect_bt.clicked.connect(self._toggle_bt_connect)

        self.lbl_bt_status = QLabel("Status: Disconnected", self.tab_bt)
        self.lbl_bt_status.setStyleSheet("color: #64748b; font-size: 11px;")

        b_layout.addLayout(b_top)
        b_layout.addWidget(self.list_bt_devices)
        b_layout.addWidget(self.btn_connect_bt)
        b_layout.addWidget(self.lbl_bt_status)

        self.tabs.addTab(self.tab_bt, "Bluetooth (BLE)")

        # 3. Close Button Box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        button_box.rejected.connect(self.accept)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.addWidget(self.monitor_frame)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(button_box)

        # Wire Driver Signals
        self.usb_source.live_reading_stream.connect(self._on_live_stream_value)
        self.bt_source.live_reading_stream.connect(self._on_live_stream_value)
        self.bt_source.device_discovered.connect(self._on_bt_device_discovered)
        self.bt_source.scan_finished.connect(self._on_bt_scan_finished)

        # Initialize Ports
        self._refresh_ports()

    def _refresh_ports(self) -> None:
        """Scan and populate COM ports."""
        self.combo_ports.clear()
        ports = self.usb_source.list_available_ports()
        for p_id, p_name in ports:
            self.combo_ports.addItem(p_name, p_id)

    def _toggle_usb_connect(self) -> None:
        if self.usb_source.is_connected:
            self.usb_source.disconnect_port()
            self.btn_connect_usb.setText("Connect USB Meter")
            self.lbl_usb_status.setText("Status: Disconnected")
            self.lbl_live_value.setText("--.- lx")
        else:
            port = self.combo_ports.currentData()
            baud = self.combo_baud.currentData()
            if port:
                ok, msg = self.usb_source.connect_port(port, baud=baud)
                if ok:
                    self.btn_connect_usb.setText("Disconnect USB Meter")
                    self.lbl_usb_status.setText(f"Status: Connected ({port})")
                else:
                    self.lbl_usb_status.setText(f"Error: {msg}")

    def _scan_bluetooth(self) -> None:
        self.list_bt_devices.clear()
        self.lbl_bt_scan_status.setText("Scanning for Bluetooth meters...")
        self.btn_scan_bt.setEnabled(False)
        self.bt_source.scan_devices(timeout=3.0)

    def _on_bt_device_discovered(self, address: str, name: str, rssi: int) -> None:
        item = QListWidgetItem(f"{name} ({address}) [RSSI: {rssi} dBm]")
        item.setData(Qt.ItemDataRole.UserRole, (address, name))
        self.list_bt_devices.addItem(item)

    def _on_bt_scan_finished(self) -> None:
        self.lbl_bt_scan_status.setText("Scan complete.")
        self.btn_scan_bt.setEnabled(True)

    def _toggle_bt_connect(self) -> None:
        if self.bt_source.is_connected:
            self.bt_source.disconnect_device()
            self.btn_connect_bt.setText("Connect Selected Bluetooth Device")
            self.lbl_bt_status.setText("Status: Disconnected")
            self.lbl_live_value.setText("--.- lx")
        else:
            cur = self.list_bt_devices.currentItem()
            if cur:
                addr, name = cur.data(Qt.ItemDataRole.UserRole)
                self.bt_source.connect_device(addr, name)
                self.btn_connect_bt.setText("Disconnect Bluetooth Device")
                self.lbl_bt_status.setText(f"Status: Connected to {name}")

    def _on_live_stream_value(self, lux: float) -> None:
        """Update live digital display."""
        self.lbl_live_value.setText(f"{lux:.1f} lx")

    def _capture_reading(self) -> None:
        """Emit captured reading."""
        if self.usb_source.latest_lux is not None:
            self.reading_captured.emit(self.usb_source.latest_lux)
        elif self.bt_source.latest_lux is not None:
            self.reading_captured.emit(self.bt_source.latest_lux)
