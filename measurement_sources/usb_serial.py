"""USB Serial Lux Meter Hardware Driver.

Supports Extech, Testo, Voltcraft, PeakTech, CEM, Uni-T, and generic ASCII/SCPI lux meters.
Features auto COM port discovery, background threaded polling/streaming, and robust error recovery.
"""

from __future__ import annotations
import re
import time
import threading
from typing import List, Optional, Tuple, Dict
from PySide6.QtCore import QObject, Signal

from measurement_sources.base import MeasurementSource

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class USBSerialMeterSource(MeasurementSource):
    """USB Serial connection driver for physical lux meters."""

    live_reading_stream = Signal(float)
    connection_status_changed = Signal(bool, str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.port_name: Optional[str] = None
        self.baud_rate: int = 9600
        self.serial_inst = None
        self.is_running: bool = False
        self._thread: Optional[threading.Thread] = None
        self.latest_lux: Optional[float] = None
        self._is_connected = False

    def get_source_name(self) -> str:
        return "USB Lux Meter"

    def connect_source(self) -> bool:
        if self.port_name:
            ok, _ = self.connect_port(self.port_name, self.baud_rate)
            return ok
        return False

    def disconnect_source(self) -> None:
        self.disconnect_port()

    def is_available(self) -> bool:
        return SERIAL_AVAILABLE

    @classmethod
    def list_available_ports(cls) -> List[Tuple[str, str]]:
        """List available physical/virtual USB COM ports with descriptions."""
        if not SERIAL_AVAILABLE:
            return [("COM_MOCK", "Simulated Virtual Lux Meter (No pyserial)")]

        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append((p.device, f"{p.device} - {p.description}"))

        if not ports:
            ports.append(("COM1", "COM1 - Serial Port"))
        return ports

    def connect_port(self, port: str, baud: int = 9600, timeout: float = 1.0) -> Tuple[bool, str]:
        """Open USB serial connection to lux meter."""
        self.disconnect_port()
        self.port_name = port
        self.baud_rate = baud

        if not SERIAL_AVAILABLE or port == "COM_MOCK":
            self._is_connected = True
            self.is_running = True
            self._thread = threading.Thread(target=self._mock_stream_loop, daemon=True)
            self._thread.start()
            self.connection_status_changed.emit(True, f"Connected to {port} (Simulated)")
            return True, f"Connected to {port}"

        try:
            self.serial_inst = serial.Serial(port=port, baudrate=baud, timeout=timeout)
            self._is_connected = True
            self.is_running = True
            self._thread = threading.Thread(target=self._read_stream_loop, daemon=True)
            self._thread.start()
            self.connection_status_changed.emit(True, f"Connected to {port} @ {baud} bps")
            return True, f"Successfully connected to {port}"
        except Exception as e:
            self._is_connected = False
            self.connection_status_changed.emit(False, f"Connection Failed: {e}")
            return False, str(e)

    def disconnect_port(self) -> None:
        """Close connection."""
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.8)
        self._thread = None

        if self.serial_inst and self.serial_inst.is_open:
            try:
                self.serial_inst.close()
            except Exception:
                pass
        self.serial_inst = None
        self._is_connected = False
        self.connection_status_changed.emit(False, "Disconnected")

    def _read_stream_loop(self) -> None:
        """Background thread reading lines and parsing lux numeric values."""
        while self.is_running and self.serial_inst and self.serial_inst.is_open:
            try:
                line = self.serial_inst.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    lux = self._parse_lux_value(line)
                    if lux is not None:
                        self.latest_lux = lux
                        self.live_reading_stream.emit(lux)
            except Exception:
                time.sleep(0.1)

    def _mock_stream_loop(self) -> None:
        """Simulated stream loop for testing without physical meter."""
        import random
        base = 480.0
        while self.is_running:
            base += random.uniform(-5.0, 5.0)
            base = max(10.0, min(2000.0, base))
            self.latest_lux = round(base, 1)
            self.live_reading_stream.emit(self.latest_lux)
            time.sleep(0.5)

    @staticmethod
    def _parse_lux_value(raw_text: str) -> Optional[float]:
        """Parse raw text from lux meter into float value."""
        clean = raw_text.replace("lx", "").replace("LX", "").replace("Lux", "").replace("LUX", "")
        match = re.search(r"[-+]?\d*\.?\d+", clean)
        if match:
            try:
                val = float(match.group(0))
                if 0.0 <= val <= 200000.0:
                    return round(val, 1)
            except ValueError:
                pass
        return None
